import colorama


class Operator:

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
            print "\n  ****************Test case not defined !!!!! ***************\n error message :", e.message
        except:
            print "\n *****************Undefined error occurred, please check test cases !!! ******************\n"

    def all_same(self, x_path, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        try:
            element = ele_list[0]
        except IndexError as e:
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
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
                    print (
                        colorama.Fore.RED +
                        '\n ************Overall Result of Test case: all-same failed *******************\n' +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if n.text != value:
                        res = False
                if res is False:

                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case is-equal failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if n.text == value:
                        res = False
                        print err_mssg, n.text
                    else:
                        print info_mssg
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case not-equal failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element ************\n", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (range1 < n.text and n.text < range2):
                        print info_mssg
                    else:
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case in-range failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text < val1):
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case is-gt failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occured while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text < val1):
                        print info_mssg
                    else:
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************* Test case is-lt failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if n.text > range1 or n.text < range2:
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case not-range failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text.find(value) == -1):
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case contains failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in node:
                    if (n.text not in value_list):
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************ Test case is-in failed *********************\n" +
                        err_mssg)
                else:
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
            print "\n ************** Error occurred while accessing test element *************", e.message
        else:
            nodes = xml1.xpath(x_path)
            for node_path in nodes:
                node = node_path.xpath(element)
                for n in nodes:
                    if (n.text in value_list):
                        res = False
                if res is False:
                    print (
                        colorama.Fore.RED +
                        "\n ************* Test case not-in failed *********************\n" +
                        err_mssg)
                else:
                    print (
                        colorama.Fore.GREEN +
                        "\n ************* Test case not-in passed *******************\n" +
                        info_mssg)

    # operator requiring two operands

    def no_diff(self, x_path, id, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        xml2 = args[1]
        node1 = xml1.xpath(x_path + '/' + ele_list[0])
        node2 = xml2.xpath(x_path + '/' + ele_list[0])
        if (len(node1) == len(node2)):
            i = 0
            while i < len(node1):
                if(node1[i].text == node2[i].text):
                    i = i + 1
                    print info_mssg
                else:
                    res = False
                    i = i + 1
                    print err_mssg
            if (res is False):
                print (
                    colorama.Fore.RED +
                    "\n *********** No-diff test failed ***********\n" +
                    err_mssg)
            else:
                print (
                    colorama.Fore.GREEN +
                    "\n *********** No-diff test Passed ***********\n" +
                    info_mssg)
        else:
            print (
                colorama.Fore.RED +
                "\n *********** No-diff test failed: Node length not same***********\n")

    def list_not_less(
            self, x_path, id_list, ele_list, err_mssg, info_mssg, *args):
        res = True
        xml1 = args[0]
        xml2 = args[1]
        node1_iter = xml1.xpath(x_path)
        node2_iter = xml2.xpath(x_path)
        print len(node1_iter), len(node2_iter)
        if(len(node1_iter) == len(node2_iter)):
            i = 0
            while(i < len(node1_iter)):
                flag = True
                for id in id_list:
                    if(node1_iter[i].findtext(id) != node2_iter[i].findtext(id)):
                        flag = False
                    if flag is True:
                        node1_list = node1_iter[i].findall(ele_list[0])
                        node2_list = node2_iter[i].findall(ele_list[0])
                        print "node length are", len(node1_list), len(node2_list)
                        j = 0
                        while (j < len(node1_list)):
                            if (len(node2_list) == 0 or node1_list[
                                    j].text != node2_list[j].text):
                                print "missing node is %s and its value %s: " % (node1_list[j].tag, node1_list[j].text)
                                res = False
                            j = j + 1
                    else:
                        print "\n ******** id matching failed *********\n"
                i = i + 1
        else:
            print "xpaths are less different"

        if res is False:
            print(
                colorama.Fore.RED +
                "\n ********** Overall result of list-not-less failed *************\n" +
                err_mssg)
        else:
            print(
                colorama.Fore.GREEN +
                "\n ********** Overall result of list-not-less Passed *************\n" +
                info_mssg)

    def list_not_more(
            self, x_path, id_list, ele_list, err_mssg, info_mssg, *args):
        res = True
        flag = True
        xml1 = args[0]
        xml2 = args[1]
        # print "id is ", id_list[0]
        node1_iter = xml1.xpath(x_path)
        node2_iter = xml2.xpath(x_path)
        print len(node1_iter), len(node2_iter)
        if(len(node1_iter) == len(node2_iter)):
            i = 0
            while(i < len(node1_iter)):
                for id in id_list:
                    # print "id is ", id
                    if(node1_iter[i].findtext(id) != node2_iter[i].findtext(id)):
                        print "flag is false"
                        flag = False
                        node1_list = node1_iter[i].findall(ele_list[0])
                        node2_list = node2_iter[i].findall(ele_list[0])
                        print "node length are", len(node1_list), len(node2_list)
                        j = 0
                        while (j < len(node2_list) - 1):
                            if node1_list[j].text != node2_list[j].text:
                                print "missing node:", node2_list[j].text
                            j = j + 1
                i = i + 1
        else:
            print "xpaths are less different"