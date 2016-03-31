import re
import colorama
import jinja2
import logging
from collections import defaultdict
from lxml import etree

class Operator:

    def __init__(self):
        self.result = True
        self.no_failed = 0
        self.no_passed = 0
        self.device = None
        self.log_detail = {'hostname': None}
        self.test_details = defaultdict(list)
        colorama.init(autoreset=True)
        self.logger_testop = logging.getLogger(__name__)

    def __del__(self):
        colorama.init(autoreset=True)

    def define_operator(
            self, logdetail, testop, x_path, ele_list, err_mssg, info_mssg, teston, iter, id, *args):
        """
        It will call functions according to test operator
        eg if testop is: is-equal, then it will call is_equal function
        :param logdetail: dictionary containing parameters for logging module, ex hostname
        :param testop: test operation to be performed
        :param x_path: Xpath in test file
        :param ele_list: Node name and their expected value, like is-equal: admin-status, up
        :param err_mssg: Error message
        :param info_mssg: Info message
        :param teston: Command or RPC to be tested
        :param iter: if true, test operation will be iterated to all nodes, ow only first node is tested
        :param id: id given in testfile
        :param args: other arguments like xml1 or xml2 (pre or post snapshots)
        :return:
        """
        self.log_detail = logdetail
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
            self.logger_testop.error(colorama.Fore.RED +
                "ERROR!! Complete message: %s" % e.message, extra=self.log_detail)
            self.no_failed = self.no_failed + 1
        except Exception as ex:
            self.logger_testop.error(colorama.Fore.RED +
                "ERROR!! Complete message: %s" % str(ex), extra=self.log_detail)
            self.no_failed = self.no_failed + 1

    def print_result(self, testname, result):
        if result is False:
            self.no_failed = self.no_failed + 1
            self.logger_testop.info(colorama.Fore.RED +
                                    'Final result of ' + testname + ': FAILED\n', extra=self.log_detail)
        elif result is True:
            self.no_passed = self.no_passed + 1
            self.logger_testop.info(
                colorama.Fore.GREEN +
                'Final result of ' + testname + ': PASSED \n', extra=self.log_detail)

    def print_testmssg(self, testname):
        """
        Print info and error messages
        :param testname: test operation like "no-diff", "is-equal"
        """
        msg = "Performing %s Test Operation" % testname
        testmssg = (80 - len(msg) - 2) / 2 * '-' + \
            msg + (80 - len(msg) - 2) / 2 * '-'
        self.logger_testop.info(
            colorama.Fore.BLUE +
            testmssg,
            extra=self.log_detail)

# two for loops, one for xpath, other for iterating nodes inside xpath, if value is not
# given for comparision, then it will take first value

    def _find_xpath(self, iter, x_path, xml1=None, xml2=None):
        """
        this function will find pre and post nodes for given Xpath
        :param iter: if true, it will iterate through all nodes
        :param x_path: Xpath in Test file
        :param xml1: pre snapshot
        :param xml2: post snapshot
        :return: return prenodes and postnodes in given xpath
        """
        if xml1 is not None:
            pre_nodes = xml1.xpath(x_path)if iter else xml1.xpath(x_path)[0:1]
        else:
            pre_nodes = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
        post_nodes = xml2.xpath(x_path) if iter else xml2.xpath(x_path)[0:1]
        return pre_nodes, post_nodes

    def _find_element(self, id_list, iddict, element, pre_node, post_node):
        """
        get element node for test operation
        Not used by "no-diff", "list-not-less", "list-not-more" and "delta" functions
        """
        prenode = pre_node.xpath(element)
        postnode = post_node.xpath(element)
        for j in range(len(id_list)):
            iddict[
                'id_' +
                str(j)] = post_node.xpath(
                id_list[j])[0].text.strip() if post_node.xpath(
                id_list[j]) else None
        return iddict, prenode, postnode

    def _find_value(self, predict, postdict, element, postnode, prenode):
        """
        get value of element node for test operation
        """
        post_nodevalue = postnode.text.strip(
        ) if postnode.text is not None else None
        pre_nodevalue = prenode.text.strip(
        ) if prenode.text is not None else None
        predict[element.replace('-', '_')] = pre_nodevalue
        postdict[element.replace('-', '_')] = post_nodevalue
        return predict, postdict, post_nodevalue, pre_nodevalue

    def _get_data(self, id_list, nodes):
        """
        This function is used by "no-diff", "list-not-less", "list-not-more" and "delta" functions
        used to calculate values of nodes mentioned in id
        :param id_list: list of ids
        :param nodes: pre or post nodes
        :return: return dictionary containing ids and their respective values
        """
        data = {}
        #i = 0
        for path in nodes:
         #   i = i + 1
            xlist = [path.findall(id) for id in id_list]
            val = []
            for values in xlist:
                if values is not None:
                    if isinstance(values, list):
                        val1 = [v.text for v in values]
                        val.append(tuple(val1))
                    else:
                        val.append(values.text)
          #  val.append(i)
            data[tuple(val)] = path
        return data

    def _get_nodevalue(
            self, predict, postdict, pre_nodes, post_nodes, x_path, element, mssg):
        """
        Used to calculate value of any node mentioned inside info and error messages
        """
        mssg = re.findall('{{(.*?)}}', mssg)
        for e in mssg:
            if (e.startswith("post") or e.startswith("Post")):
                val = e[6:-2]
                if val not in [x_path, element]:
                    postdict[
                        val.replace(
                            '-',
                            '_')] = post_nodes.findtext(val).strip()if post_nodes.findtext(val) is not None else None

            if (e.startswith("pre") or e.startswith("PRE")):
                val = e[5:-2]
                if val not in [x_path, element]:
                    predict[
                        val.replace(
                            '-',
                            '_')] = pre_nodes.findtext(val).strip() if pre_nodes.findtext(val) is not None else None
        return predict, postdict

    def exists(self, x_path, ele_list, err_mssg, info_mssg,
               teston, iter, id_list, xml1, xml2):
        """
        Calculate if node value is present in given snapshot
        """
        self.print_testmssg("exists")
        res = True
        predict = {}
        postdict = {}
        iddict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "exists"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\n Error occurred while accessing test element: %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n Element is not specified for testing",
                extra=self.log_detail)
            raise
        else:
            tresult['node_name'] = element
            # this function will find set of pre and post nodes for given Xpath
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### get element node for test operation ####
                    #### if length of pre node is less than post node, assign sample node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))
                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    # calculate value of any node mentioned inside info and
                    # error messages  ####
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    #### check only in postnode   ####
                    if postnode:

                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))
                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            self.logger_testop.debug(
                                jinja2.Template(
                                    info_mssg.replace(
                                        '-',
                                        '_')).render(
                                    iddict,
                                    pre=predict,
                                    post=postdict), extra=self.log_detail)
                    else:
                        res = False
                        self.logger_testop.info(
                            jinja2.Template(
                                err_mssg.replace(
                                    '-',
                                    '_')).render(
                                iddict,
                                pre=predict,
                                post=postdict), extra=self.log_detail)
        self.print_result('exists', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_exists(self, x_path, ele_list, err_mssg, info_mssg,
                   teston, iter, id_list, xml1, xml2):
        self.print_testmssg("not-exists")
        colorama.init(autoreset=True)
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "not-exists"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\n Error occurred while accessing test element: %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n Element is not specified for testing", extra=self.log_detail)
            raise
        else:
            tresult['node_name'] = element
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))
                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            res = False
                            self.logger_testop.info(
                                jinja2.Template(
                                    err_mssg.replace(
                                        '-',
                                        '_')).render(
                                    iddict,
                                    pre=predict,
                                    post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.debug(
                            jinja2.Template(
                                info_mssg.replace(
                                    '-',
                                    '_')).render(
                                iddict,
                                pre=predict,
                                post=postdict), extra=self.log_detail)
        self.print_result('not-exists', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def all_same(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("all-same")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['actual_node_value'] = []
        tresult['testoperation'] = "all-same"
        try:
            element = ele_list[0]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\nError occurred while accessing test element: %s" % e.message, extra=self.log_detail)
            raise
        else:
            tresult['node_name'] = element
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                if len(ele_list) >= 2:
                    vpath = x_path + ele_list[1] + '/' + ele_list[0]
                    value1 = xml2.xpath(vpath)
                    value = value1[0].text.strip() if len(
                        value1) != 0 else None
                    tresult['expected_node_value'] = value
                else:
                    value = xml2.xpath(
                        x_path +
                        '/' +
                        ele_list[0])[0].text.strip()
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            if post_nodevalue != value:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
        self.print_result('all-same', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("is-equal")
        res = True
        tresult = {}
        predict = {}
        postdict = {}
        iddict = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "is-equal"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\nError occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n'is-equal' test operator requires two parameter", extra=self.log_detail)
            raise
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = value
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            if post_nodevalue == value.strip():
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED+
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('is-equal', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)


    def not_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("not-equal")
        res = True
        tresult = {}
        predict = {}
        postdict = {}
        iddict = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "not-equal"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\nError occurred while accessing test element: %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n'not-equal' test operator requires two parameter", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = value
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            if post_nodevalue != value.strip():
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        # tresult['actual_node_value'].append(None)
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('not-equal', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def in_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("in-range")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "in-range"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            range1 = float(ele_list[1])
            range2 = float(ele_list[2])
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\nError occurred while accessing test element %s\n" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n'in-range' test operator requires two parameter", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = [range1, range2]
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(
                                float(post_nodevalue))
                            if (float(post_nodevalue) >= range1
                                    and float(post_nodevalue) <= range2):
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('in-range', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("not-range")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "not-range"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            range1 = float(ele_list[1])
            range2 = float(ele_list[2])
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\n Error occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n not-range test operator require two parameters", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = [range1, range2]
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(
                                float(post_nodevalue))
                            if float(post_nodevalue) <= range1 or float(
                                    post_nodevalue) >= range2:
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('not-range', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_gt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("is-gt")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "is-gt"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            val1 = float(ele_list[1])
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "Error occurred while accessing test element: %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "'is-gt' test operator require two parameters", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = val1
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for j in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if j >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[j], prenode[j])
                            tresult['actual_node_value'].append(
                                float(post_nodevalue))
                            if (float(post_nodevalue) > val1):
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('is-gt', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_lt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("is-lt")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "is-lt"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            val1 = float(ele_list[1])
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "Error occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "'is-lt' test operator require two parameters", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = val1
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(
                                float(post_nodevalue))
                            if (float(post_nodevalue) < val1):
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('is-lt', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def contains(self, x_path, ele_list, err_mssg, info_mssg,
                 teston, iter, id_list, xml1, xml2):
        self.print_testmssg("contains")
        predict = {}
        postdict = {}
        iddict = {}
        res = True
        tresult = {}
        tresult['actual_node_value'] = []
        tresult['xpath'] = x_path
        tresult['testoperation'] = "contains"
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "Error occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n'contains' require two parameters",
                extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = value
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))
                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict[
                                (element.replace('-', '_'))] = prenode[k].text
                            postdict[
                                (element.replace('-', '_'))] = postnode[k].text
                            tresult['actual_node_value'].append(
                                postnode[k].text)
                            if (postnode[k].text.find(value) == -1):
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!!, Node is not present in path given with test operator!!", extra=self.log_detail)
                        res = False
        self.print_result('contains', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def is_in(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("is-in")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "is-in"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            value_list = ele_list[1:]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "\nError occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "\n'is-in' test operator require two parameters", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = value_list
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            if (post_nodevalue in value_list):
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('is-in', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def not_in(self, x_path, ele_list, err_mssg,
               info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("not-in")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "not-in"
        tresult['actual_node_value'] = []
        try:
            element = ele_list[0]
            value_list = ele_list[1:]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "Error occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "'not-in' test operator require two parameters", extra=self.log_detail)
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = value_list
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!", extra=self.log_detail)
                res = False
            else:
                for i in range(len(post_nodes)):
                    #### if length of pre node is less than post node, assign sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            #### if length of pre node is less than post node, assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            tresult['actual_node_value'].append(post_nodevalue)
                            if (post_nodevalue not in value_list):
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                res = False
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR!! Node '%s' not found" %
                            element, extra=self.log_detail)
                        res = False
        self.print_result('not-in', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    ################## operator requiring two snapshots, pre and post ########
    def no_diff(self, x_path, ele_list, err_mssg,
                info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("no-diff")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "no-diff"
        tresult['node_name'] = ele_list[0]
        tresult['pre_node_value'] = []
        tresult['post_node_value'] = []
        tresult['id_miss_match'] = []
        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
        if re.match(ele_list[0], "no node"):
            self.logger_testop.error(colorama.Fore.RED +
                "ERROR!! 'no-diff' operator requires node value to test !!", extra=self.log_detail)
        else:
            if (not pre_nodes) or (not post_nodes):
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!",
                    extra=self.log_detail)
                res = False
            else:
                # assuming one iterator has unique set of ids, i.e only one node matching to id
                # making dictionary for id and its corresponding xpath
                # one xpath has only one set of id
                data1 = self._get_data(id_list, pre_nodes)
                data2 = self._get_data(id_list, post_nodes)
                for k in data1:
                    for length in range(len(k)):
                        iddict[
                            'id_' + str(length)] = [k[length][i].strip() for i in range(len(k[length]))]
                        #iddict['id_' + str(length)] = k[length].strip()
                    if k in data2:
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, data1[k], data2[k], x_path, ele_list[0], err_mssg)
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, data1[k], data2[k], x_path, ele_list[0], info_mssg)

                        ele_xpath1 = data1.get(k).xpath(ele_list[0])
                        ele_xpath2 = data2.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip() for element in ele_xpath1] if len(
                            ele_xpath1) != 0 else None
                        val_list2 = [element.text.strip() for element in ele_xpath2] if len(
                            ele_xpath2) != 0 else None

                        predict[ele_list[0].replace('-', '_')] = val_list1
                        postdict[ele_list[0].replace('-', '_')] = val_list2

                        if val_list1 != val_list2:
                            res = False
                            tresult['pre_node_value'].append(val_list1)
                            tresult['post_node_value'].append(val_list2)

                            self.logger_testop.info(
                                jinja2.Template(
                                    err_mssg.replace(
                                        '-',
                                        '_')).render(
                                    iddict,
                                    pre=predict,
                                    post=postdict), extra=self.log_detail)
                        else:
                            self.logger_testop.debug(
                                jinja2.Template(
                                    info_mssg.replace(
                                        '-',
                                        '_')).render(
                                    iddict,
                                    pre=predict,
                                    post=postdict), extra=self.log_detail)
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                            "ERROR, id miss match occurred!!! id list in pre snapshots is: %s" % iddict, extra=self.log_detail)
                        tresult['id_miss_match'].append(iddict.copy())
                        """
                        for kval in k:
                            self.logger_testop.error(
                                "Missing node: %s" %
                                kval.strip(), extra= self.log_detail)
                                """
                        res = False
        self.print_result('no-diff', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def list_not_less(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("list-not-less")
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "list-not-less"
        tresult['node_name'] = ele_list[0]
        iddict = {}
        predict = {}
        postdict = {}
        tresult['pre_node_value'] = []
        tresult['post_node_value'] = []
        tresult['id_miss_match'] = []
        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)

        if not pre_nodes or not post_nodes:
            self.logger_testop.error(colorama.Fore.RED +
                "ERROR!! Nodes are not present in given Xpath!!",
                extra=self.log_detail)
            res = False
        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath

            predata = self._get_data(id_list, pre_nodes)
            postdata = self._get_data(id_list, post_nodes)

            for k in predata:
                for length in range(len(k)):
                    iddict['id_' + str(length)] = [k[length][i].strip()
                                                   for i in range(len(k[length]))]

                if k in postdata:
                    if not re.match(ele_list[0], "no node"):
                        predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                                x_path, ele_list[0], err_mssg)
                        predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                                x_path, ele_list[0], info_mssg)
                        ele_xpath1 = predata.get(k).xpath(ele_list[0])
                        ele_xpath2 = postdata.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip()
                                     for element in ele_xpath1]
                        val_list2 = [element.text.strip()
                                     for element in ele_xpath2]
                        # tresult['pre_node_value'].append(val_list1)
                        # tresult['post_node_value'].append(val_list2)
                        for val1 in val_list1:
                            predict[ele_list[0].replace('-', '_')] = val1
                            tresult['pre_node_value'].append(val1)
                            if val1 not in val_list2:
                                # user can only ask for values which are in pre
                                # and not in post
                                tresult['post_node_value'].append(val1)
                                res = False
                                self.logger_testop.info("Missing node : %s for element tag %s and parent element %s" % (val1, ele_xpath1[0].tag,
                                                                                                                        ele_xpath1[0].getparent().tag), extra=self.log_detail)
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                        "ERROR, id miss match occurred!!! id list not in post snapshots is: %s" %
                        iddict, extra=self.log_detail)
                    tresult['id_miss_match'].append(iddict.copy())
                    # for kval in range(len(k)-1):
                    #    print "kval, k", kval,k
                    # self.logger_testop.error(
                    #    "Missing Ids in post snapshot: %s" %
                    #    k[kval].strip(), extra= self.log_detail)
                    res = False
        self.print_result('list-not-less', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def list_not_more(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("list-not-more")
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "list-not-more"
        tresult['node_name'] = ele_list[0]
        tresult['pre_node_value'] = []
        tresult['post_node_value'] = []
        tresult['id_miss_match'] = []
        iddict = {}
        predict = {}
        postdict = {}
        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
        if not pre_nodes or not post_nodes:
            self.logger_testop.error(colorama.Fore.RED +
                "ERROR!! Nodes are not present in given Xpath!!",
                extra=self.log_detail)
            res = False
        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath
            predata = self._get_data(id_list, pre_nodes)
            postdata = self._get_data(id_list, post_nodes)

            for k in postdata:
                for length in range(len(k)):
                    #iddict['id_' + str(length)] = k[length].strip()
                    iddict['id_' + str(length)] = [k[length][i].strip()
                                                   for i in range(len(k[length]))]

                if k in predata:
                    if not re.match(ele_list[0], "no node"):
                        predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                                x_path, ele_list[0], err_mssg)
                        predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                                x_path, ele_list[0], info_mssg)
                        ele_xpath1 = predata.get(k).xpath(ele_list[0])
                        ele_xpath2 = postdata.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip()
                                     for element in ele_xpath1]
                        val_list2 = [element.text.strip()
                                     for element in ele_xpath2]
                        # tresult['pre_node_value'].append(val_list1)
                        # tresult['post_node_value'].append(val_list2)
                        for val2 in val_list2:
                            postdict[ele_list[0].replace('-', '_')] = val2
                            tresult['post_node_value'].append(val2)
                            if val2 not in val_list1:
                                res = False
                                tresult['pre_node_value'].append(val2)
                                self.logger_testop.error("Missing node: %s for element tag: %s and parent element %s" % (val2, ele_xpath2[0].tag,
                                                                                                                         ele_xpath2[0].getparent().tag), extra=self.log_detail)
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                            else:
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)

                else:
                    tresult['id_miss_match'] = []
                    self.logger_testop.error(colorama.Fore.RED +
                        "ERROR, id miss match occurred !! id list not in pre snapshots is: %s" % iddict, extra=self.log_detail)
                    tresult['id_miss_match'].append(iddict.copy())
                    # for kval in range(len(k)-1):
                    #    self.logger_testop.error(
                    #        "Missing Ids in pre snapshots: %s" %
                    #        k[kval].strip(), extra= self.log_detail)
                    res = False
        self.print_result('list-not-more', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def delta(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2):
        self.print_testmssg("delta")
        res = True
        tresult = {}
        tresult['xpath'] = x_path
        tresult['testoperation'] = "delta"
        iddict = {}
        predict = {}
        postdict = {}
        tresult['pre_node_value'] = []
        tresult['post_node_value'] = []
        tresult['id_miss_match'] = []
        tresult['node_name'] = ele_list[0]
        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)

        try:
            node_name = ele_list[0]
            delta_val = ele_list[1]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                "Error occurred while accessing test element: %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                "'delta' test operator require two parameters", extra=self.log_detail)
        else:
            if not pre_nodes or not post_nodes:
                self.logger_testop.error(colorama.Fore.RED +
                    "ERROR!! Nodes are not present in given Xpath!!",
                    extra=self.log_detail)
                res = False

            else:
                # assuming one iterator has unique set of ids, i.e only one node matching to id
                # making dictionary for id and its corresponding xpath

                predata = self._get_data(id_list, pre_nodes)
                postdata = self._get_data(id_list, post_nodes)

                for k in predata:
                    # checking if id in first data set is present in second data
                    # set or not
                    for length in range(len(k)):
                        #iddict['id_' + str(length)] = k[length]
                        iddict[
                            'id_' + str(length)] = [k[length][i].strip() for i in range(len(k[length]))]

                    if k in postdata:
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, predata[k], postdata[k], x_path, node_name, err_mssg)
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, predata[k], postdata[k], x_path, node_name, info_mssg)
                        if ele_list is not None:
                            ele_xpath1 = predata.get(k).xpath(node_name)
                            ele_xpath2 = postdata.get(k).xpath(node_name)
                            if len(ele_xpath1) and len(ele_xpath2):
                                val1 = float(
                                    ele_xpath1[0].text)  # value of desired node for pre snapshot
                                val2 = float(
                                    ele_xpath2[0].text)  # value of desired node for post snapshot
                                del_val = delta_val
                                tresult['pre_node_value'].append(val1)
                                tresult['post_node_value'].append(val2)
                                predict[node_name.replace('-', '_')] = val1
                                postdict[node_name.replace('-', '_')] = val2

                                # for negative percentage
                                if re.search('%', del_val) and (
                                        re.search('-', del_val)):
                                    dvalue = abs(float(delta_val.strip('%')))
                                    mvalue = val1 - ((val1 * dvalue) / 100)
                                    if (val2 > val1 or val2 < mvalue):
                                        res = False
                                        self.logger_testop.info(
                                            jinja2.Template(
                                                err_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                                    else:
                                        self.logger_testop.debug(
                                            jinja2.Template(
                                                info_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)

                                # for positive percent change
                                elif re.search('%', del_val) and (re.search('/+', del_val)):
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue = val1 + ((val1 * dvalue) / 100)
                                    if (val2 < val1 or val2 > mvalue):
                                        res = False
                                        self.logger_testop.info(
                                            jinja2.Template(
                                                err_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                                    else:
                                        self.logger_testop.debug(
                                            jinja2.Template(
                                                info_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)

                                # absolute percent change
                                elif re.search('%', del_val):
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue1 = val1 - (val1 * dvalue) / 100
                                    mvalue2 = val1 + (val1 * dvalue) / 100
                                    if (val2 < mvalue1 or val2 > mvalue2):
                                        res = False
                                        self.logger_testop.info(
                                            jinja2.Template(
                                                err_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                                    else:
                                        self.logger_testop.debug(
                                            jinja2.Template(
                                                info_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)

                                # for negative change
                                elif re.search('-', del_val):
                                    dvalue = abs(float(delta_val.strip('%')))
                                    mvalue = val1 - dvalue
                                    if (val2 < mvalue or val2 > val1):
                                        res = False
                                        self.logger_testop.info(
                                            jinja2.Template(
                                                err_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                                    else:
                                        self.logger_testop.debug(
                                            jinja2.Template(
                                                info_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)

                                 # for positive change
                                elif re.search('\+', del_val):
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue = val1 + dvalue
                                    if (val2 >= mvalue or val2 <= val1):
                                        res = False
                                        self.logger_testop.info(
                                            jinja2.Template(
                                                err_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                                    else:
                                        self.logger_testop.debug(
                                            jinja2.Template(
                                                info_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)

                                else:
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue1 = val1 - dvalue
                                    mvalue2 = val1 + dvalue
                                    if (val2 < mvalue1 or val2 > mvalue2):
                                        res = False
                                        self.logger_testop.info(
                                            jinja2.Template(
                                                err_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                                    else:
                                        self.logger_testop.debug(
                                            jinja2.Template(
                                                info_mssg.replace(
                                                    '-',
                                                    '_')).render(
                                                iddict,
                                                pre=predict,
                                                post=postdict), extra=self.log_detail)
                            else:
                                self.logger_testop.error(colorama.Fore.RED +
                                    "ERROR!! Node '%s' not found" %
                                    node_name,
                                    extra=self.log_detail)
                                res = False

                    else:
                        self.logger_testop.error(colorama.Fore.RED + "\n ERROR!! id miss match occurred !! mismatched id from pre snapshot"
                                                 "is: %s" % iddict, extra=self.log_detail)
                        tresult['id_miss_match'].append(iddict.copy())

                        # for kval in k:
                        #    self.logger_testop.error(
                        #        "missing node: %s" %
                        #        kval.strip(), extra= self.log_detail)
                        res = False

        self.print_result('delta', res)
        tresult['result'] = res
        self.test_details[teston].append(tresult)

    def final_result(self, logs):
        """
        Print final result
        :param logs: dictionary containing details like hostname
        :return:
        """
        msg = " Final Result!! "
        finalmssg = (80 - len(msg) - 2) / 2 * '-' + \
            msg + (80 - len(msg) - 2) / 2 * '-'

        self.logger_testop.info(colorama.Fore.BLUE + finalmssg, extra=logs)
        self.logger_testop.info(
            colorama.Fore.GREEN +
            "Total No of tests passed: {}".format(
                self.no_passed), extra=logs)
        self.logger_testop.info(
            colorama.Fore.RED +
            "Total No of tests failed: {} ".format(
                self.no_failed), extra=logs)
        if (self.no_failed):
            self.logger_testop.info(
                colorama.Fore.RED +
                colorama.Style.BRIGHT +
                "Overall Tests failed!!! ", extra=logs)
            self.result = "Failed"
        elif (self.no_passed == 0 and self.no_failed == 0):
            self.logger_testop.info(
                colorama.Fore.RED +
                colorama.Style.BRIGHT +
                "None of the test cases executed !!! ", extra=logs)
        else:
            self.logger_testop.info(
                colorama.Fore.GREEN +
                colorama.Style.BRIGHT +
                "Overall Tests passed!!! ", extra=logs)
            self.result = "Passed"
