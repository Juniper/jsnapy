import difflib
import re
import sys
import os
import logging
import colorama

color_add = '\033[1;32;44m'
color_sub = '\033[1;31;44m'
color_change = '\033[1;33;41m'
color_sep = '\033[1;34m'
color_none = '\033[m'


class Differ(object):

    def __init__(self):
        self.column_size = 150
        self.line_width = (150 // 2) - 9

    def generate_diff(self, lines_left, lines_right, headers):

        lines_left = [self._tabtospace(x) for x in lines_left]
        lines_right = [self._tabtospace(x) for x in lines_right]

        diff_data = difflib._mdiff(lines_left, lines_right, 5,
                                   linejunk=None,
                                   charjunk=difflib.IS_CHARACTER_JUNK)

        diff_data = self._decorate_lines(diff_data)
        diff_data = self._accumulate_formatted_lines(diff_data)

        for lines_left, lines_right in self._generate_lines(
                headers, diff_data):
            yield self._colour_lines(
                "%s %s" % (self._adjust_text(lines_left, self.column_size // 2 - 1, "l"),
                           self._adjust_text(lines_right, self.column_size // 2 - 1, "l")))

    def _colour_lines(self, string):

        cdict = {'\0+': color_add, '\0-': color_sub,
                 '\0^': color_change, '\1': color_none,
                 '\t': ' '}

        for key, value in cdict.items():
            string = string.replace(key, value)

        return re.sub("\033\\[[01];3([123])m(\\s+)(\033\\[)",
                      "\033[7;3\\1m\\2\\3", string)

    def _accumulate_formatted_lines(self, diffs):

        def compile_string(line_number, string):
            string = string.rstrip()
            try:
                linenum = '%d' % line_number
            except TypeError:
                return string
            return '%s %s' % (self._adjust_text(linenum, 6, "r"), string)

        for lines_left, lines_right, flag in diffs:
            if lines_left is not None or lines_right is not None or flag is not None:
                yield (compile_string(*lines_left),
                       compile_string(*lines_right))
            else:
                yield None

    def _actual_length(self, text):
        dictn = {'\0+': "",
                 '\0-': "",
                 '\0^': "",
                 '\1': "",
                 '\t': ' '}
        for key, value in dictn.items():
            text = text.replace(key, value)
        return self._ignore_escape_char(text)

    def _ignore_escape_char(self, text):
        ctr = 0
        inside_color_char = False
        p_char = ' '
        for char in text:
            if inside_color_char:
                if char == "m":
                    inside_color_char = False
            else:
                if char == "[" and p_char == "\033":
                    inside_color_char = True
                    ctr -= 1
                else:
                    ctr += 1
            p_char = char
        return ctr

    def _decorate_lines(self, diff_data):

        def line_divide(list_lines, index_line, text):
            if not index_line:
                list_lines.append((index_line, text))
                return
            if ((len(text) - (text.count('\0') * 3) <=
                 self.line_width)):
                list_lines.append((index_line, text))
                return

            idx = 0
            ctr = 0
            mark = ''
            while ctr < self.line_width and idx < len(text):
                if text[idx] == '\1':
                    idx += 1
                    mark = ''
                elif text[idx] == '\0':
                    idx += 1
                    mark = text[idx]
                    idx += 1
                else:
                    ctr += len(text[idx])
                    idx += 1
            line_1 = text[:idx]
            line_2 = text[idx:]

            if mark:
                line_1 = line_1 + '\1'
                line_2 = '\0' + mark + line_2

            list_lines.append((index_line, line_1))
            line_divide(list_lines, '>', line_2)

        for lines_left, lines_right, flag in diff_data:

            if flag is None:
                yield lines_left, lines_right, flag
                continue

            (line_num_left, text_left), (line_num_right,
                                         text_right) = lines_left, lines_right
            list_left, list_right = [], []
            line_divide(list_left, line_num_left, text_left)
            line_divide(list_right, line_num_right, text_right)
            while list_left or list_right:
                if list_right:
                    lines_right = list_right.pop(0)
                else:
                    lines_right = ('', ' ')
                if list_left:
                    lines_left = list_left.pop(0)
                else:
                    lines_left = ('', ' ')
                yield lines_left, lines_right, flag

    def _adjust_text(self, text, text_size, mode):
        l = self._actual_length(text)
        if mode == "l":
            return text + (" " * (text_size - l))
        elif mode == "r":
            return (" " * (text_size - l)) + text

    def _tabtospace(self, string):
        string = string.replace(' ', '\0')
        string = string.expandtabs(8)
        string = string.replace(' ', '\t')
        string = string.replace('\0', ' ').rstrip('\n')
        return string

    def _generate_lines(self, headers, diff_lines):

        if headers[0] or headers[1]:
            header_left = color_sep + headers[0] + color_none
            header_right = color_sep + headers[1] + color_none
            yield (header_left, header_right)
        for text in diff_lines:
            if text is None:
                separator = color_sep + '-' * 3 + color_none
                yield (separator, separator)
            else:
                yield text


class Diff:

    def __init__(self, log_detail):
        self.logger_diff = logging.getLogger(__name__)
        self.log_detail = log_detail
        colorama.init(autoreset=True)

    def readfile(self, name):
        if os.path.isfile(name) and os.path.isfile(name):
            with open(name, mode="rb") as f:
                return f.readlines()
        else:
            self.logger_diff.error(colorama.Fore.RED +
                                   "ERROR!!! File is not present at given location", extra=self.log_detail)

    def diff_files(self, a, b):
        headers = a, b
        for x in [a, b]:
            if os.path.isdir(x):
                self.logger_diff.error(colorama.Fore.RED +
                                       "ERROR!!! File is not present at given location", extra=self.log_detail)
                return
        lines_a = self.readfile(a)
        lines_b = self.readfile(b)
        self.diff(lines_a, lines_b, headers)

    def diff_strings(self, a, b, headers=(None, None)):
        lines_a = a.splitlines(True)
        lines_b = b.splitlines(True)
        self.diff(lines_a, lines_b, headers)

    def diff(self, a, b, headers=(None, None)):
        obj = Differ()

        for line in obj.generate_diff(
                a, b, headers):
            self.print_line(line)
            sys.stdout.flush()

    def print_line(self, s):
        s = "%s\n" % s
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(s.encode("utf-8"))
        else:
            sys.stdout.write(s.encode("utf-8"))
