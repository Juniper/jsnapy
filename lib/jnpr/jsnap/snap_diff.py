import difflib
import re
import sys
import os

color_code_list = {
    "red":     '\033[0;31m',
    "green":   '\033[0;32m',
    "yellow":  '\033[0;33m',
    "blue":    '\033[0;34m',
    "magenta": '\033[0;35m',
    "cyan":    '\033[0;36m',
    "none":    '\033[m',
    "red_bold":     '\033[1;31m',
    "green_bold":   '\033[1;32m',
    "yellow_bold":  '\033[1;33m',
    "blue_bold":    '\033[1;34m',
    "magenta_bold": '\033[1;35m',
    "cyan_bold":    '\033[1;36m',
}


class Differ(object):

    def __init__(self, column_size=150, numbered_lines=True):

        self.tabsize = 8
        self.numbered_lines = numbered_lines
        self.column_size = column_size

        if not numbered_lines:
            self.wrap_size = (self.column_size // 2) - 3
        else:
            self.wrap_size = (self.column_size // 2) - 9

    def generate_diff(self, lines_left, lines_right, headers, context_lines=5):

        lines_left = [self.expand_tabs(line) for line in lines_left]
        lines_right = [self.expand_tabs(line) for line in lines_right]

        diff_data = difflib._mdiff(lines_left, lines_right, context_lines,
                               linejunk=None,
                               charjunk=difflib.IS_CHARACTER_JUNK)

        diff_data = self.wrap_lines(diff_data)
        diff_data = self.collect_formatted_lines(diff_data)

        for lines_left, lines_right in self.generate_lines(headers[0], headers[1], diff_data):
            yield self.colour_lines(
                "%s %s" % (self.left_pad(lines_left, self.column_size // 2 - 1),
                           self.left_pad(lines_right, self.column_size // 2 - 1)))

    def colour_lines(self, s):

        color_add = color_code_list["green_bold"]
        color_sub = color_code_list["red_bold"]
        color_change = color_code_list["yellow_bold"]
        color_none = color_code_list["none"]
        color_dict = {'\0+': color_add, '\0-': color_sub,
                     '\0^': color_change, '\1': color_none,
                     '\t': ' '}

        for key, value in color_dict.items():
            s = s.replace(key, value)

        return re.sub("\033\\[[01];3([123])m(\\s+)(\033\\[)",
                          "\033[7;3\\1m\\2\\3", s)

    def wrap_lines(self, diff_data):

        for lines_left, lines_right, flag in diff_data:

            if flag is None:
                yield lines_left, lines_right, flag
                continue

            (line_num_left, text_left), (line_num_right, text_right) = lines_left, lines_right
            list_left, list_right = [], []
            self.line_split(list_left, line_num_left, text_left)
            self.line_split(list_right, line_num_right, text_right)
            while list_left or list_right:
                if list_left:
                    lines_left = list_left.pop(0)
                else:
                    lines_left = ('', ' ')
                if list_right:
                    lines_right = list_right.pop(0)
                else:
                    lines_right = ('', ' ')

                yield lines_left, lines_right, flag

    def line_split(self, list_lines, index_line, text):

        if not index_line:
            list_lines.append((index_line, text))
            return

        if ((len(text) - (text.count('\0') * 3) <=
             self.wrap_size)):
            list_lines.append((index_line, text))
            return

        idx = 0
        ctr = 0
        mark = ''
        while ctr < self.wrap_size and idx < len(text):
            if text[idx] == '\0':
                idx += 1
                mark = text[idx]
                idx += 1
            elif text[idx] == '\1':
                idx += 1
                mark = ''
            else:
                ctr += len(text[idx])
                idx += 1
        line_1 = text[:idx]
        line_2 = text[idx:]

        if mark:
            line_1 = line_1 + '\1'
            line_2 = '\0' + mark + line_2

        list_lines.append((index_line, line_1))
        self.line_split(list_lines, '>', line_2)

    def collect_formatted_lines(self, diffs):

        for lines_left, lines_right, flag in diffs:
            if (lines_left, lines_right, flag) == (None, None, None):
                yield None
            else:
                yield (self.format_line(*lines_left),
                       self.format_line(*lines_right))

    def format_line(self, linenum, text):

        text = text.rstrip()
        if self.numbered_lines:
            try:
                linenum = '%d' % linenum
            except TypeError:
                return text
            return '%s %s' % (self.right_pad(linenum, 6), text)
        else:
            return text

    def actual_length(self, text):
        dictn = {'\0+': "",
                              '\0-': "",
                              '\0^': "",
                              '\1': "",
                              '\t': ' '}
        for key, value in dictn.items():
            text = text.replace(key, value)
        ctr = 0
        inside_esc_char = False
        prev_char = ' '
        for char in text:
            if inside_esc_char:
                if char == "m":
                    inside_esc_char = False
            else:
                if char == "[" and prev_char == "\033":
                    inside_esc_char = True
                    ctr -= 1
                else:
                    ctr += 1
            prev_char = char
        return ctr

    def right_pad(self, s, field_width):
        return (" " * (field_width - self.actual_length(s))) + s

    def left_pad(self, s, field_width):
        return s + (" " * (field_width - self.actual_length(s)))

    def expand_tabs(self, string):
        string = string.replace(' ', '\0')
        string = string.expandtabs(self.tabsize)
        string = string.replace(' ', '\t')
        return string.replace('\0', ' ').rstrip('\n')

    def generate_lines(self, header_left, header_right, diff_lines):
        if header_left or header_right:
            header_left = "%s%s%s" % (color_code_list["blue"], header_left, color_code_list["none"])
            header_right = "%s%s%s" % (color_code_list["blue"], header_right, color_code_list["none"])
            yield (header_left, header_right)

        for text in diff_lines:
            if text is None:
                separator = "%s%s%s" % (color_code_list["blue"], '---', color_code_list["none"])
                yield (separator,separator)
            else:
                yield text


class Diff:

    def readfile(self, name):
        if os.path.isfile(name) and os.path.isfile(name):
            with open(name, mode="rb") as f:
                return f.readlines()
        else:
            print "ERROR!!! File is not present at given location"

    def diff_files(self, a, b):
        headers = a, b
        for x in [a, b]:
            if os.path.isdir(x):
                self.codec_print("File not found at specified location.")
                return
        lines_a = self.readfile(a)
        lines_b = self.readfile(b)
        self.diff(lines_a, lines_b, headers)

    def diff_strings(self, a, b, headers=(None, None)):
        lines_a = a.splitlines(True)
        lines_b = b.splitlines(True)
        self.diff(lines_a, lines_b, headers)

    def diff(self, a, b, headers=(None, None)):
        # context_lines = None
        context_lines = 5
        obj = Differ()

        for line in obj.generate_diff(
                a, b, headers,
                context_lines=context_lines):
            self.print_line(line)
            sys.stdout.flush()

    def print_line(self, s):
        s = "%s\n" % s
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(s.encode("utf-8"))
        else:
            sys.stdout.write(s.encode("utf-8"))
