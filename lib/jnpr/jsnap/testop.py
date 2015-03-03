import re
import colorama


class Operator:

    result = 0
    no_failed = 0
    no_passed = 0

    def define_operator(
            self, testop, x_path, ele_list, err_mssg, info_mssg, *args):
        try:
            getattr(
                self,
                testop.replace(
                    '-',
                    '_'))(
                x_path,
                ele_list,
                err_mssg,
                info_mssg,
                *args)
        except AttributeError as e:
            print "\n  ****************Test case not defined !!!!! ***************\n " \
                  "error message :", e.message
        except:
            print "\n *****************Undefined error occurred, please check test cases " \
                  "!!! ******************\n"

    def all_same(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element ****" \
                  "*********", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                value = node[0].text
                for n in node:
                    if n.text != value:
                        res = False
                        print err_mssg, n.text
                    else:
                        print info_mssg
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                '\n ************Overall Result of Test case: all-same failed *******************\n' +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                '\n ************* Overall Result of Test case: all-same passed ******************\n' +
                info_mssg)

    def is_equal(self, x_path, ele_list, err_mssg, info_mssg, *args):
        colorama.init(autoreset=True)
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element *****" \
                  "********", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if n.text != value:
                        res = False
                        print err_mssg, n.text
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case is-equal failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************* Overall result of is-equal passed *************\n" +
                info_mssg)

    def not_equal(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element *******" \
                  "******", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if n.text == value:
                        res = False
                        print err_mssg, n.text
                    else:
                        print info_mssg
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case not-equal failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************ Test case not-equal passed *********************\n" +
                info_mssg)

    def in_range(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            range1 = int(ele_list[1])
            range2 = int(ele_list[2])
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element **********" \
                  "**\n", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (range1 < n.text and n.text < range2):
                        print info_mssg
                    else:
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case in-range failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************ Test case in-range passed *********************\n" +
                info_mssg)

    def is_gt(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            val1 = int(ele_list[1])
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element ******" \
                  "*******", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text < val1):
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case is-gt failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************ Test case is-gt passed *********************\n" +
                info_mssg)

    def is_lt(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            val1 = int(ele_list[1])
        except IndexError as e:
            print "\n ************** Error occured while accessing test element **********" \
                  "***", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text > val1):
                        print info_mssg
                    else:
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (colorama.Fore.RED + "\n **********"
                   "*** Test case is-lt failed *********************\n" + err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************* Test case is-lt passed *********************\n" +
                info_mssg)

    def not_range(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            range1 = int(ele_list[1])
            range2 = int(ele_list[2])
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element ****" \
                  "*********", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if n.text > range1 or n.text < range2:
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case not-range failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************ Test case not-range passed *********************\n" +
                info_mssg)

    def contains(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            value = int(ele_list[1])
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element *" \
                  "************", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text.find(value) == -1):
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case contains failed *****************"
                "****\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************ Test case contains passed *********************\n" +
                info_mssg)

    def is_in(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            values = int(ele_list[1])
            value_list = [v.strip() for v in values.split(' ')]
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element *" \
                  "************", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text not in value_list):
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************ Test case is-in failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************ Test case is-in passed *********************\n" +
                info_mssg)

    def not_in(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
            values = int(ele_list[1])
            value_list = [v.strip() for v in values.split(' ')]
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element *" \
                  "************", e.message
        else:
            nodes = xml1.xpath('//' + x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in nodes:
                    if (n.text in value_list):
                        res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print (
                colorama.Fore.RED +
                "\n ************* Test case not-in failed *********************\n" +
                err_mssg)
        else:
            Operator.no_passed = Operator.no_passed + 1
            print (
                colorama.Fore.GREEN +
                "\n ************* Test case not-in passed *******************\n" +
                info_mssg)

    # operator requiring two operands

    def no_diff(self, x_path, id_list, ele_list, err_mssg, info_mssg, *args):
        print (
            colorama.Fore.BLUE +
            "\n ********* Running no_diff test cases *************** \n")
        res = True
        xml1 = args[0]
        xml2 = args[1]
        data1 = {}
        data2 = {}
        pathx = xml1.xpath(
            '//physical-interface[normalize-space(name)="ge-0/0/0"]')
        print "pathx", pathx
        node1 = xml1.xpath(x_path)
        node2 = xml2.xpath(x_path)

        # assuming one iterator has unique set of ids, i.e only one node matching to id
        # making dictionary for id and its corresponding xpath
        for path in node1:
            xlist = [path.find(id) for id in id_list]
            val = []
            for values in xlist:
                if values is not None:
                    val.append(values.text)
            data1[tuple(val)] = path
        print data1

        for path in node2:
            xlist = [path.find(id) for id in id_list]
            val = []
            for values in xlist:
                if values is not None:
                    val.append(values.text)
            data2[tuple(val)] = path
        print data2

        # what if there are extra data added in one list
        for k in data1:
            if k in data2:
                ele_xpath1 = data1.get(k).xpath(ele_list[0])
                ele_xpath2 = data2.get(k).xpath(ele_list[0])
                val_list1 = [element.text for element in ele_xpath1]
                val_list2 = [element.text for element in ele_xpath2]
                if val_list1 != val_list2:
                    res = False
                    print val_list1, "doesn't match with", val_list2
            else:
                print "\n id miss match"
                res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print "Test Failed", err_mssg
        else:
            print "Test Passed", info_mssg
            Operator.no_passed = Operator.no_passed + 1
        print "\n total tests passed: ", Operator.no_passed
        print "\n total tests failed: ", Operator.no_failed

    def list_not_less(
            self, x_path, id_list, ele_list, err_mssg, info_mssg, *args):
        print (
            colorama.Fore.BLUE +
            "\n ********* Running list-not-less test cases *************** \n")
        res = True
        xml1 = args[0]
        xml2 = args[1]
        data1 = {}
        data2 = {}
        node1 = xml1.xpath(x_path)
        node2 = xml2.xpath(x_path)

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
                    # print "data values are", data1.get(k), data2.get(k)
                    ele_xpath1 = data1.get(k).xpath(ele_list[0])
                    ele_xpath2 = data2.get(k).xpath(ele_list[0])
                    # print "ele_list is", ele_list[0]
                    val_list1 = [element.text for element in ele_xpath1]
                    val_list2 = [element.text for element in ele_xpath2]
                    for val1 in val_list1:
                        if val1 not in val_list2:
                            res = False
                            print "missing node :", val1, "for element tag ", ele_xpath1[0].tag, \
                                "and parent element", ele_xpath1[0].getparent().tag
            else:
                print "\n id miss match"
                res = False
        if res is False:
            Operator.no_failed = Operator.no_failed + 1
            print "Test Failed", err_mssg
        else:
            print "Test Passed", info_mssg
            Operator.no_passed = Operator.no_passed + 1

        print "\n total tests passed: ", Operator.no_passed
        print "\n total tests failed: ", Operator.no_failed

    def list_not_more(
            self, x_path, id_list, ele_list, err_mssg, info_mssg, *args):
        print (
            colorama.Fore.BLUE +
            "\n ********* Running list-not-more test cases *************** \n")
        res = True
        xml1 = args[0]
        xml2 = args[1]
        data1 = {}
        data2 = {}
        node1 = xml1.xpath(x_path)
        node2 = xml2.xpath(x_path)

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
                    # print "data values are", data1.get(k), data2.get(k)
                    ele_xpath1 = data1.get(k).xpath(ele_list[0])
                    ele_xpath2 = data2.get(k).xpath(ele_list[0])
                    # print "ele_list is", ele_list[0]
                    val_list1 = [element.text for element in ele_xpath1]
                    val_list2 = [element.text for element in ele_xpath2]
                    for val2 in val_list2:
                        if val2 not in val_list1:
                            res = False
                            print "missing node :", val2, "for element tag ", ele_xpath2[0].tag, \
                                "and parent element", ele_xpath2[0].getparent().tag
            else:
                print "\n id miss match"
                res = False
        if res is False:
            print "Test Failed", err_mssg
            Operator.no_failed = Operator.no_failed + 1
        else:
            print "Test Passed", info_mssg
            Operator.no_passed = Operator.no_passed + 1
        print "\n total tests passed: ", Operator.no_passed
        print "\n total tests failed: ", Operator.no_failed

    def delta(self, x_path, id_list, ele_list, err_mssg, info_mssg, *args):
        print (
            colorama.Fore.BLUE +
            "\n ********* Running delta test cases *************** \n")
        res = True
        xml1 = args[0]
        xml2 = args[1]
        data1 = {}
        data2 = {}
        node1 = xml1.xpath(x_path)
        node2 = xml2.xpath(x_path)

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
                    # print "data values are", data1.get(k), data2.get(k)
                    # print "ele_list[0]", ele_list[0]
                    ele_xpath1 = data1.get(k).xpath(ele_list[0])
                    ele_xpath2 = data2.get(k).xpath(ele_list[0])
                    # print "ele_list is", ele_list[0]
                    # print "ele_xpath1 is", ele_xpath1
                    if ele_xpath1 is not None:
                     #   print "ele_xpath1 is", ele_xpath1
                        val1 = int(ele_xpath1[0].text)
                    if ele_xpath2 is not None:
                        val2 = int(ele_xpath2[0].text)
                    del_val = ele_list[1]

                    # an absolute percentage
                    if re.search('%', del_val) and (re.search('-', del_val)):
                        print "matching -%"
                        dvalue = ((val1 - val2) * 100) / val1
                        if (dvalue == int(ele_list[1].strip('%'))):
                            print "percent test passed"
                        else:
                            res = False
                            print "Node value in percent changed by, that is by: %d", dvalue

                    # negative percent difference
                    elif re.search('%', del_val):
                        dvalue = (abs(val1 - val2) * 100) / val1
                       # print "abs(val1-val2)", abs(val1-val2)
                       # print "(abs(val1-val2)/val1)", (abs(val1-val2)/val1)
                        if (dvalue == int(ele_list[1].strip('%'))):
                            print "absolute percent test passed"
                        else:
                            print "Node value in absolute percent changed by, that is by: %d", dvalue
                            res = False

                    # negative difference
                    elif re.search('-', del_val):
                        # an absolute percentage
                        dvalue = (val1 - val2)
                        if dvalue == int(ele_list[1]):
                            print "absolute delta difference test passed"
                        else:
                            res = False
                            print "Node value in absolute difference changed by, that is by: %d", dvalue

                    # positive difference
                    else:
                        dvalue = abs((val1) - (val2))
                        if dvalue == int(ele_list[1]):
                            print "delta difference test passed"
                        else:
                            res = False
                            print "Node value in difference changed by, that is by: %d" % dvalue
            else:
                print "\n id miss match"
                res = False
        if res is False:
            print "Overall Result of delta Failed", err_mssg
            Operator.no_failed = Operator.no_failed + 1
        else:
            print "Overall Result of delta Passed", info_mssg
            Operator.no_passed = Operator.no_passed + 1

    def final_result(self):
        print (
            colorama.Fore.BLUE +
            "\n\n        ----------  Final Result!! ----------------          ")
        print (
            colorama.Fore.GREEN +
            "\nTotal No of tests passed: {}".format(
                Operator.no_passed))
        print (
            colorama.Fore.RED +
            "\nTotal No of tests failed: {} ".format(
                Operator.no_failed))
        if (Operator.no_failed):
            print (
                colorama.Fore.BLACK +
                colorama.Style.BRIGHT +
                colorama.Back.RED +
                "\nOverall Tests failed!!! ")
        else:
            print (
                colorama.Fore.BLACK +
                colorama.Style.BRIGHT +
                colorama.Back.GREEN +
                "\nOverall Tests passed!!! ")
