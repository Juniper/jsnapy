import re
import colorama
from collections import defaultdict
import jinja2


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
                teston,
                iter,
                id,
                *args)
        except AttributeError as e:
            print "\nTest case not defined !!!!! \n error message :", e.message
        except:
            print "\nUndefined error occurred, please check test cases !!!"

    def print_result(self, testname, result):
        if result is False:
            self.no_failed = self.no_failed + 1
            print (
                colorama.Fore.RED +
                '\nFinal result of ' + testname + ': FAILED\n')
        elif result is True:
            self.no_passed = self.no_passed + 1
            print (
                colorama.Fore.GREEN +
                '\nFinal result of ' + testname + ': PASSED \n')

    def print_testmssg(self, msg):
        testmssg = (80 - len(msg) - 2) / 2 * '*' + \
            msg + (80 - len(msg) - 2) / 2 * '*'
        print (colorama.Fore.BLUE + testmssg)

# two for loops, one for xpath, other for iterating nodes inside xpath, if value is not
# given for comparision, then it will take first value

    def all_same(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing all-same Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "all-same"
        try:
            element = ele_list[0]
        except IndexError as e:
            print "\nError occurred while accessing test element", e.message
        else:
            post_nodes = xml2.xpath(x_path)if iter else xml2.xpath(x_path)[0:1]
            if xml1 is not None:
                pre_nodes = xml1.xpath(
                    x_path)if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path)if iter else xml2.xpath(x_path)[0:1]

            #nodes = xml1.xpath(x_path) if iter else xml1.xpath(x_path)[0:1]
            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                if len(ele_list) >= 2:
                    vpath = x_path + ele_list[1] + '/' + ele_list[0]
                    value = xml2.xpath(vpath)[0].text
                else:
                    value = xml2.xpath(x_path + '/' + ele_list[0])[0].text
                i = 0
                while (i < len(post_nodes)):
                    postnode = post_nodes[i].xpath(element)
                    prenode = pre_nodes[i].xpath(element)
                    # id will be same for pre and post
                    for j in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(j)] = post_nodes[i].xpath(
                            id_list[j])[0].text.strip() if post_nodes[i].xpath(
                            id_list[j]) else None

                    if postnode:
                        j = 0
                        while(j < len(postnode)):
                            pre_nodevalue = prenode[j].text.strip()
                            post_nodevalue = postnode[j].text.strip()
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if post_nodevalue != value.strip():
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
                            j = j + 1
                    i = i + 1

        self.print_result('all-same', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

        '''

    def is_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing is-equal Test Operation"

        self.print_testmssg(msg)
        colorama.init(autoreset=True)
        res = True
        resdict={}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "is-equal"


        err_list=re.findall('{{(.*?)}}', err_mssg)
        info_list=re.findall('{{(.*?)}}', info_mssg)
        print err_mssg
        err_list= [ elements for elements in err_list if elements not in [x_path,ele_list[0]]]
        print "err_list", err_list

        print "err_list, info_list", err_list, info_list

        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            print "\n Error occurred while accessing test element", e.message
            print "\n is-equal test operator require two parameters"
        else:
            #nodes = xml1.xpath('//' + x_path)
            post_nodes = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
            #xml1 contains post snapshot for check and the only snapshot for
            if xml1 is not None:
                pre_nodes = xml1.xpath(x_path)if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    postnode = post_nodes[i].xpath(element)
                    prenode = pre_nodes[i].xpath(element)
                    for j in range(len(id_list)):
                        resdict['id_'+str(j)]= post_nodes[i].xpath(id_list[j])[0].text.strip() if post_nodes[i].xpath(id_list[j]) else None
                    if postnode:
                        for k in range(len(postnode)):
                            post_nodevalue = postnode[k].text.strip()
                            pre_nodevalue = prenode[k].text.strip()
                            resdict[('pre_' + element.replace('-','_'))] = pre_nodevalue
                            resdict[('post_' + element.replace('-','_'))]= post_nodevalue
                            if  post_nodevalue != value.strip():
                                res = False
                                print jinja2.Template(err_mssg.replace('-','_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-','_')).render(resdict)

        self.print_result('is-equal', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

        '''

    def is_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing is-equal Test Operation"

        self.print_testmssg(msg)
        colorama.init(autoreset=True)
        res = True
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            # xml1 contains post snapshot for check and the only snapshot for
            if xml1 is not None:
                pre_nodes = xml1.xpath(
                    x_path)if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    postnode = post_nodes[i].xpath(element)
                    prenode = pre_nodes[i].xpath(element)
                    for j in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(j)] = post_nodes[i].xpath(
                            id_list[j])[0].text.strip() if post_nodes[i].xpath(
                            id_list[j]) else None
                    if postnode:
                        for k in range(len(postnode)):
                            post_nodevalue = postnode[k].text.strip()
                            pre_nodevalue = prenode[k].text.strip()
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if post_nodevalue != value.strip():
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

        self.print_result('is-equal', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing not-equal Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path)if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path)if iter else xml2.xpath(x_path)[0:1]
            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    postnode = post_nodes[i].xpath(element)
                    prenode = pre_nodes[i].xpath(element)
                    for j in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(j)] = post_nodes[i].xpath(
                            id_list[j])[0].text.strip() if post_nodes[i].xpath(
                            id_list[j]) else None
                    if postnode:
                        for j in range(len(postnode)):
                            post_nodevalue = postnode[j].text.strip()
                            pre_nodevalue = prenode[j].text.strip()
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if post_nodevalue == value.strip():
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
        self.print_result('not-equal', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def in_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing in-range Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(x_path)if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path) if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]
            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    prenode = pre_nodes[i].xpath(element)
                    postnode = post_nodes[i].xpath(element)
                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnode:
                        for j in range(len(postnode)):
                            pre_nodevalue = float(prenode[j].text)
                            post_nodevalue = float(postnode[j].text)
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            print resdict
                            if (range1 < post_nodevalue
                                    and post_nodevalue < range2):
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
                            else:
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)

        self.print_result('in-range', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_gt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing is-gt Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path) if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    postnodes = post_nodes[i].xpath(element)
                    prenodes = pre_nodes[i].xpath(element)

                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnodes:
                        for j in range(len(postnodes)):
                            pre_nodevalue = float(prenodes[j].text)
                            post_nodevalue = float(postnodes[j].text)
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            print resdict
                            if (post_nodevalue < val1):
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

        self.print_result('is-gt', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_lt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing is-lt Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path) if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    postnode = post_nodes[i].xpath(element)
                    prenode = pre_nodes[i].xpath(element)

                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnode:
                        for j in range(len(postnode)):
                            post_nodevalue = float(postnode[j].text)
                            pre_nodevalue = float(prenode[j].text)
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if (post_nodevalue > val1):
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

        self.print_result('is-lt', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing not-range Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path) if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    postnode = post_nodes[i].xpath(element)
                    prenode = pre_nodes[i].xpath(element)

                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnode:
                        for j in range(len(postnode)):
                            post_nodevalue = float(postnode[j].text)
                            pre_nodevalue = float(prenode[j].text)
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if post_nodevalue > range1 and post_nodevalue < range2:
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

        self.print_result('not-range', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def contains(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing contains Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path) if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    prenode = pre_nodes[i].xpath(element)
                    postnode = post_nodes[i].xpath(element)

                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnode:
                        for i in range(len(postnode)):
                            post_nodevalue = postnode[i].text
                            pre_nodevalue = prenode[i].text
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if (postnode[i].text.find(value) == -1):
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
        self.print_result('contains', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_in(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing is-in Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path) if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    prenode = pre_nodes[i].xpath(element)
                    postnode = post_nodes[i].xpath(element)

                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnode:
                        for j in range(len(postnode)):
                            pre_nodevalue = prenode[j].text.strip()
                            post_nodevalue = postnode[j].text.strip()
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue
                            if (post_nodevalue not in value_list):
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
        self.print_result('is-in', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_in(self, x_path, ele_list, err_mssg,
               info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing not-in Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        resdict = {}
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
            post_nodes = xml2.xpath(
                x_path) if iter else xml2.xpath(x_path)[0:1]
            if xml1:
                pre_nodes = xml1.xpath(
                    x_path)if iter else xml1.xpath(x_path)[0:1]
            else:
                pre_nodes = xml2.xpath(
                    x_path) if iter else xml2.xpath(x_path)[0:1]

            if not post_nodes:
                print "Nodes are not present in given Xpath!!"
                res = False
            else:
                for i in range(len(post_nodes)):
                    prenode = pre_nodes[i].xpath(element)
                    postnode = post_nodes[i].xpath(element)

                    for k in range(len(id_list)):
                        resdict[
                            'id_' +
                            str(k)] = post_nodes[i].xpath(
                            id_list[k])[0].text.strip() if post_nodes[i].xpath(
                            id_list[k]) else None

                    if postnode:
                        for j in range(len(postnode)):
                            pre_nodevalue = prenode[j].text.strip()
                            post_nodevalue = postnode[j].text.strip()
                            resdict[
                                ('pre_' + element.replace('-', '_'))] = pre_nodevalue
                            resdict[
                                ('post_' + element.replace('-', '_'))] = post_nodevalue

                            if (post_nodevalue in value_list):
                                res = False
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
        self.print_result('not-in', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    # operator requiring two operands

    def no_diff(self, x_path, ele_list, err_mssg,
                info_mssg, teston, iter, id_list, xml1, xml2):

        msg = "Performing no-diff Test Operation"
        self.print_testmssg(msg)
        res = True
        data1 = {}
        data2 = {}
        tresult = {}
        resdict = {}
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

                    # store ids in resdict
                    for length in range(len(k)):
                        resdict['id_' + str(length)] = k[length].strip()

                    ele_xpath1 = data1.get(k).xpath(ele_list[0])
                    ele_xpath2 = data2.get(k).xpath(ele_list[0])
                    # assuming only one node
                    val_list1 = [
                        element.text for element in ele_xpath1][0].strip()
                    val_list2 = [
                        element.text for element in ele_xpath2][0].strip()
                    resdict[
                        ('pre_' + ele_list[0].replace('-', '_'))] = val_list1
                    resdict[
                        ('post_' + ele_list[0].replace('-', '_'))] = val_list2
                    if val_list1 != val_list2:
                        res = False
                        print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                    else:
                        print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
                else:
                    print "\n Error, id miss match ocuurred!!"
                    res = False
        self.print_result('no-diff', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def list_not_less(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing list-not-less Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "list-not-less"
        resdict = {}
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

                    for length in range(len(k)):
                        resdict['id_' + str(length)] = k[length].strip()

                    if ele_list is not None:
                        ele_xpath1 = data1.get(k).xpath(ele_list[0])
                        ele_xpath2 = data2.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip()
                                     for element in ele_xpath1]
                        val_list2 = [element.text.strip()
                                     for element in ele_xpath2]

                        for val1 in val_list1:
                            if val1 not in val_list2:
                                # user can only ask for values which are in pre
                                # and not in post
                                resdict[
                                    ('pre_' + ele_list[0].replace('-', '_'))] = val1
                                res = False
                                print "Missing node :", val1, "for element tag ", ele_xpath1[0].tag, \
                                    "and parent element", ele_xpath1[
                                        0].getparent().tag
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
                else:
                    print "\n ERROR, id miss match occurred!!!"
                    res = False

        self.print_result('list-not-less', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def list_not_more(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing list-not-more Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "list-not-more"
        data1 = {}
        data2 = {}
        resdict = {}
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

                    for length in range(len(k)):
                        resdict['id_' + str(length)] = k[length].strip()

                    if ele_list is not None:
                        ele_xpath1 = data1.get(k).xpath(ele_list[0])
                        ele_xpath2 = data2.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip()
                                     for element in ele_xpath1]
                        val_list2 = [element.text.strip()
                                     for element in ele_xpath2]
                        for val2 in val_list2:
                            if val2 not in val_list1:
                                resdict[
                                    ('post_' + ele_list[0].replace('-', '_'))] = val2
                                res = False
                                print "Missing node :", val2, "for element tag ", ele_xpath2[0].tag, \
                                    "and parent element", ele_xpath2[
                                        0].getparent().tag
                                print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                            else:
                                print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
                else:
                    print "\n ERROR, id miss match occurred !!"
                    res = False
        self.print_result('list-not-more', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def delta(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        msg = "Performing delta Test Operation"
        self.print_testmssg(msg)
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['element_list'] = ele_list
        tresult['testoperation'] = "delta"
        data1 = {}
        data2 = {}
        resdict = {}
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

                    for length in range(len(k)):
                        resdict['id_' + str(length)] = k[length]

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
                            resdict[
                                ('pre_' + ele_list[0].replace('-', '_'))] = val1
                            resdict[
                                ('post_' + ele_list[0].replace('-', '_'))] = val2

                            # for negative percentage
                            if re.search('%', del_val) and (
                                    re.search('-', del_val)):
                                dvalue = abs(float(ele_list[1].strip('%')))
                                mvalue = val1 - ((val1 * dvalue) / 100)
                                if (val2 > val1 or val2 < mvalue):
                                    res = False
                                    print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                                else:
                                    print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

                            # for positive percent change
                            elif re.search('%', del_val) and (re.search('/+', del_val)):
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue = val1 + ((val1 * dvalue) / 100)
                                if (val2 < val1 or val2 > mvalue):
                                    res = False
                                    print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                                else:
                                    print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

                            # absolute percent change
                            elif re.search('%', del_val):
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue1 = val1 - (val1 * dvalue) / 100
                                mvalue2 = val1 + (val1 * dvalue) / 100
                                if (val2 < mvalue1 or val2 > mvalue2):
                                    res = False
                                    print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                                else:
                                    print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

                            # for negative change
                            elif re.search('-', del_val):
                                dvalue = abs(float(ele_list[1].strip('%')))
                                mvalue = val1 - dvalue
                                if (val2 < mvalue or val2 > val1):
                                    res = False
                                    print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                                else:
                                    print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

                             # for positive change
                            elif re.search('\+', del_val):
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue = val1 + dvalue
                                if (val2 >= mvalue or val2 <= val1):
                                    res = False
                                    print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                                else:
                                    print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)

                            else:
                                dvalue = float(ele_list[1].strip('%'))
                                mvalue1 = val1 - dvalue
                                mvalue2 = val1 + dvalue
                                if (val2 < mvalue1 or val2 > mvalue2):
                                    res = False
                                    print jinja2.Template(err_mssg.replace('-', '_')).render(resdict)
                                else:
                                    print jinja2.Template(info_mssg.replace('-', '_')).render(resdict)
                else:
                    print "\n ERROR, id miss match occurred !! "
                    res = False

        self.print_result('delta', res)
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
