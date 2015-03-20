import re
import colorama
from collections import defaultdict


class Operator:

    def __init__(self):
        self.result = True
        self.no_failed = 0
        self.no_passed = 0
        self.test_details = defaultdict(list)
        colorama.init(autoreset=True)

    def __del__(self):
        colorama.init(autoreset=True)

    # call methods based on test operation specified, eg if testop is
    # is-equal, then it will call is_equal function
    def define_operator(
            self, testop, x_path, ele_list, err_mssg, info_mssg, teston, iter, id=0, *args):
        # try:
        getattr(
            self,
            testop.replace(
                '-',
                '_'))(
            x_path,
            ele_list,
            err_mssg,
            info_mssg,
            teston,
            iter,
            id,
            *args)
        # except AttributeError as e:
        #    print "\nTest case not defined !!!!! \n error message :", e.message
        # except:
        #    print "\nUndefined error occurred, please check test cases !!!"

    def print_result(self, testname, result, err_mssg, info_mssg):
        if result is False:
            self.no_failed = self.no_failed + 1
            print (
                colorama.Fore.RED +
                '\nFinal result of ' + testname + ': FAILED\n' +
                err_mssg)
        elif result is True:
            self.no_passed = self.no_passed + 1
            print (
                colorama.Fore.GREEN +
                '\nFinal result of ' + testname + ': PASSED \n' +
                info_mssg)

    def print_testmssg(self, msg):
        testmssg = (80 - len(msg) - 2) / 2 * '*' + \
            msg + (80 - len(msg) - 2) / 2 * '*'
        print (colorama.Fore.BLUE + testmssg)

# two for loops, one for xpath, other for iterating nodes inside xpath, if value is not
# given for comparision, then it will take first value

    def all_same(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        msg = "Performing all-same Test Operation"
        self.print_testmssg(msg)
        xml1 = args[0]
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "all-same"
        try:
            element = ele_list[0]
        except IndexError as e:
            print "\nError occurred while accessing test element", e.message
        else:
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                if len(ele_list) >= 2:
                    vpath = x_path + ele_list[1] + '/' + ele_list[0]
                    value = xml1.xpath(vpath)[0].text
                else:
                    value = xml1.xpath(x_path + '/' + ele_list[0])[0].text
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if n.text.strip() != value.strip():
                                res = False
        self.print_result('all-same', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        msg = "Performing is-equal Test Operation"
        xml1 = args[0]
        self.print_testmssg(msg)
        colorama.init(autoreset=True)
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "is-equal"
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n is-equal test operator require two parameters"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if n.text.strip() != value.strip():
                                res = False
                            print res
        self.print_result('is-equal', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        msg = "Performing not-equal Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "not-equal"
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            print "\nError occurred while accessing test element", e.message
            print "\n not-equal test operator requires two parameter"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if n.text.strip() == value.strip():
                                res = False
        self.print_result('not-equal', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def in_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        msg = "Performing in-range Test Operation"
        self.print_testmssg(msg)
        xml1 = args[0]
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "in-range"
        try:
            element = ele_list[0]
            range1 = float(ele_list[1])
            range2 = float(ele_list[2])
        except IndexError as e:
            print "\nError occurred while accessing test element\n", e.message
            print "\n in-range test operator requires two parameter"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if (range1 < float(n.text)
                                    and float(n.text) < range2):
                                print info_mssg
                            else:
                                res = False
        self.print_result('in-range', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_gt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id, *args):
        msg = "Performing is-gt Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "is-gt"
        try:
            element = ele_list[0]
            val1 = float(ele_list[1])
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n is-gt test operator require two parameter"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if (float(n.text) < val1):
                                res = False

        self.print_result('is-gt', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_lt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id, *args):
        msg = "Performing is-lt Test Operation"
        self.print_testmssg(msg)
        xml1 = args[0]
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "is-lt"
        try:
            element = ele_list[0]
            val1 = float(ele_list[1])
        except IndexError as e:
            print "\n Error occurred while accessing test element ", e.message
            print "\n is-lt test operator require two parameter"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if (float(n.text) > val1):
                                res = False

        self.print_result('is-lt', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        msg = "Performing not-range Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "not-range"
        try:
            element = ele_list[0]
            range1 = float(ele_list[1])
            range2 = float(ele_list[2])
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n not-range test operator require two parameters"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if float(n.text) > range1 and float(
                                    n.text) < range2:
                                res = False
        self.print_result('not-range', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def contains(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        msg = "Performing contains Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "contains"
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n Contains require two parameters"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if (n.text.find(value) == -1):
                                res = False
        self.print_result('contains', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_in(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id, *args):
        msg = "Performing is-in Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "is-in"
        try:
            element = ele_list[0]
            value_list = ele_list[1:]
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n is-in test operator require two parameters"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if (n.text.strip() not in value_list):
                                res = False
        self.print_result('is-in', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_in(self, x_path, ele_list, err_mssg,
               info_mssg, teston, iter, id, *args):
        msg = "Performing all-same Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        xml1 = args[0]
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "not-in"
        try:
            element = ele_list[0]
            value_list = ele_list[1:]
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n not-in test operator require two parameters"
        else:
            #nodes = xml1.xpath('//' + x_path)
            nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for node_path in nodes:
                    node = node_path.xpath(element)
                    if node:
                        for n in node:
                            if (n.text.strip() in value_list):
                                res = False
        self.print_result('not-in', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    # operator requiring two operands

    def no_diff(self, x_path, ele_list, err_mssg,
                info_mssg, teston, iter, id_list, *args):
        msg = "Performing no-diff Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        xml2 = args[1]
        data1 = {}
        data2 = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "no-diff"
        node1 = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
        node2 = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
        #node1 = xml1.xpath(x_path)
        #node2 = xml2.xpath(x_path)

        if (not node1) or (not node2):
            print "Nodes are not present in given Xpath!!"
            res = False

        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath
            for path in node1:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data1[tuple(val)] = path
            # print data1

            for path in node2:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data2[tuple(val)] = path
            # print data2

            # what if there are extra data added in one list
            for k in data1:
                if k in data2:
                    ele_xpath1 = data1.get(k).xpath(ele_list[0])
                    ele_xpath2 = data2.get(k).xpath(ele_list[0])
                    # assuming only one node
                    val_list1 = [element.text for element in ele_xpath1][0]
                    val_list2 = [element.text for element in ele_xpath2][0]
                    if val_list1.strip() != val_list2.strip():
                        res = False
                else:
                    print "\n id miss match"
                    res = False
        self.print_result('no-diff', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def list_not_less(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, *args):
        msg = "Performing list-not-less Test Operation"
        self.print_testmssg(msg)
        res = True
        xml1 = args[0]
        xml2 = args[1]
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "list-not-less"
        data1 = {}
        data2 = {}
        node1 = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
        node2 = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
        #node1 = xml1.xpath(x_path)
        #node2 = xml2.xpath(x_path)

        if not node1 or not node2:
            print "Nodes are not present in given Xpath!!"
            res = False

        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath
            for path in node1:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data1[tuple(val)] = path
            # print data1

            for path in node2:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data2[tuple(val)] = path
            # print data2

            for k in data1:
                if k in data2:
                    if ele_list is not None:
                        ele_xpath1 = data1.get(k).xpath(ele_list[0])
                        ele_xpath2 = data2.get(k).xpath(ele_list[0])
                        val_list1 = [element.text for element in ele_xpath1]
                        val_list2 = [element.text for element in ele_xpath2]
                        for val1 in val_list1:
                            if val1 not in val_list2:
                                res = False
                                print "missing node :", val1, "for element tag ", ele_xpath1[0].tag, \
                                    "and parent element", ele_xpath1[
                                        0].getparent().tag
                else:
                    print "\n id miss match"
                    res = False

        self.print_result('list-not-less', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def list_not_more(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, *args):
        msg = "Performing list-not-more Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        xml1 = args[0]
        xml2 = args[1]
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "list-not-more"
        data1 = {}
        data2 = {}
        node1 = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
        node2 = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
        #node1 = xml1.xpath(x_path)
        #node2 = xml2.xpath(x_path)

        if not node1 or not node2:
            print "Nodes are not present in given Xpath!!"
            res = False

        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath
            for path in node1:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data1[tuple(val)] = path
            # print data1

            for path in node2:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data2[tuple(val)] = path
            # print data2

            for k in data2:
                if k in data1:
                    if ele_list is not None:
                        ele_xpath1 = data1.get(k).xpath(ele_list[0])
                        ele_xpath2 = data2.get(k).xpath(ele_list[0])
                        val_list1 = [element.text for element in ele_xpath1]
                        val_list2 = [element.text for element in ele_xpath2]
                        for val2 in val_list2:
                            if val2 not in val_list1:
                                res = False
                                print "missing node :", val2, "for element tag ", ele_xpath2[0].tag, \
                                    "and parent element", ele_xpath2[
                                        0].getparent().tag
                else:
                    print "\nid miss match"
                    res = False
        self.print_result('list-not-more', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def delta(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, *args):
        msg = "Performing delta Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        xml1 = args[0]  # //pre snap file
        xml2 = args[1]  # post snap file
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "delta"
        data1 = {}
        data2 = {}
        node1 = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
        node2 = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
        #node1 = xml1.xpath(x_path)
        #node2 = xml2.xpath(x_path)

        if not node1 or not node2:
            print "Nodes are not present in given Xpath!!"
            res = False

        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath
            for path in node1:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data1[tuple(val)] = path

            # data1 is dictionary of id and its xpath
            for path in node2:
                xlist = [path.find(id) for id in id_list]
                val = []
                for values in xlist:
                    if values is not None:
                        val.append(values.text)
                data2[tuple(val)] = path

            for k in data1:
                # checking if id in first data set is present in second data
                # set or not
                if k in data2:
                    if ele_list is not None:
                        # print "data values are", data1.get(k), data2.get(k)
                        ele_xpath1 = data1.get(k).xpath(ele_list[0])
                        ele_xpath2 = data2.get(k).xpath(ele_list[0])
                        if len(ele_xpath1) and len(ele_xpath2):
                            val1 = float(
                                ele_xpath1[0].text)  # value of desired node for pre snapshot
                            val2 = float(
                                ele_xpath2[0].text)  # value of desired node for post snapshot
                            del_val = ele_list[1]

                            # for negative percentage
                            if re.search('%', del_val) and (
                                    re.search('-', del_val)):
                                dvalue = abs(float(ele_list[1].strip('%')))
                                mvalue = val1 - ((val1 * dvalue) / 100)
                                if (val2 > val1 or val2 < mvalue):
                                    res = False
                                    print "Node value in percent changed by, that is by: %d", dvalue

                            # for positive percent change
                            elif re.search('%', del_val) and (re.search('/+', del_val)):
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue = val1 + ((val1 * dvalue) / 100)
                                if (val2 < val1 or val2 > mvalue):
                                    res = False
                                    print "Node value in percent changed by, that is by: %d", dvalue

                            # absolute percent change
                            elif re.search('%', del_val):
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue1 = val1 - (val1 * dvalue) / 100
                                mvalue2 = val1 + (val1 * dvalue) / 100
                                if (val2 < mvalue1 or val2 > mvalue2):
                                    res = False
                                    print "Node value in percent changed by, that is by: %d", dvalue

                            # for negative change
                            elif re.search('-', del_val):
                                dvalue = abs(float(ele_list[1].strip('%')))
                                mvalue = val1 - dvalue
                                if (val2 < mvalue or val2 > val1):
                                    res = False
                                    print "Node value in percent changed by, that is by: %d", dvalue

                             # for positive change
                            elif re.search('/+', del_val):
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue = val1 + dvalue
                                if (val2 > mvalue or val2 < val1):
                                    res = False
                                    print "Node value in percent changed by, that is by: %d", dvalue

                            else:
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue1 = val1 - dvalue
                                mvalue2 = val1 + dvalue
                                if (val2 < mvalue1 or val2 > mvalue2):
                                    res = False
                                    print "Node value in percent changed by, that is by: %d", dvalue
                else:
                    print "\n id miss match"
                    res = False

        self.print_result('delta', res, err_mssg, info_mssg)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    # generate final result
    def final_result(self):
        msg = " Final Result!! "
        finalmssg = (80 - len(msg) - 2) / 2 * '-' + \
            msg + (80 - len(msg) - 2) / 2 * '-'

        print (colorama.Fore.BLUE + "\n" + finalmssg)
        print (
            colorama.Fore.GREEN +
            "\nTotal No of tests passed: {}".format(
                self.no_passed))
        print (
            colorama.Fore.RED +
            "\nTotal No of tests failed: {} ".format(
                self.no_failed))
        if (self.no_failed):
            print (
                colorama.Fore.RED +
                colorama.Style.BRIGHT +
                "\nOverall Tests failed!!! ")
            self.result = "Failed"
        elif (self.no_passed == 0 and self.no_failed == 0):
            print (
                colorama.Fore.RED +
                colorama.Style.BRIGHT +
                "\nNone of the test cases executed !!! ")
        else:
            print (
                colorama.Fore.GREEN +
                colorama.Style.BRIGHT +
                "\nOverall Tests passed!!! ")
            self.result = "Passed"
