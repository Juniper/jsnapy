#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import re
import colorama
import jinja2
import logging
import lxml
from collections import defaultdict
from lxml import etree
from copy import deepcopy
import traceback

class Operator:

    def __init__(self):
        self.result = None
        self.no_failed = 0
        self.no_passed = 0
        self.device = None
        self.log_detail = {'hostname': None}
        self.test_details = defaultdict(list)
        self.logger_testop = logging.getLogger(__name__)
        self.result_dict = {} #unlike test_details this is keyed on test_name

    @property
    def test_results(self):
        return dict(self.test_details)

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
                                     "ERROR!! AttributeError \nComplete Message: %s" % e.message, extra=self.log_detail)
            self.no_failed = self.no_failed + 1
        except etree.XPathEvalError as ex:
            self.logger_testop.error(colorama.Fore.RED + "Error in evaluating XPATH, \nComplete Message: %s" % ex.message, extra=self.log_detail )
            self.no_failed = self.no_failed + 1
        except Exception as ex:
            self.logger_testop.error(colorama.Fore.RED +
                                     "ERROR!! %s \nComplete Message: %s" % (type(ex).__name__, str(ex)), extra=self.log_detail)
            self.no_failed = self.no_failed + 1

    def _print_result(self, testmssg, result):
        if result is False:
            self.no_failed = self.no_failed + 1
            self.logger_testop.info(colorama.Fore.RED +
                                    'FAIL | ' + testmssg, extra=self.log_detail)
        elif result is True:
            self.no_passed = self.no_passed + 1
            self.logger_testop.info(
                colorama.Fore.GREEN +
                'PASS | ' + testmssg, extra=self.log_detail)

    def print_testmssg(self, testname):
        """
        Print info and error messages
        :param testname: test operation like "no-diff", "is-equal"
        """
        msg = "Performing %s Test Operation" % testname
        testmssg = (80 - len(msg) - 2) / 2 * '-' + \
            msg + (80 - len(msg) - 2) / 2 * '-'
        self.logger_testop.debug(
            colorama.Fore.BLUE +
            testmssg,
            extra=self.log_detail)

    def _print_message(self, mssg, iddict, predict, postdict, mode="info"):
        getattr(
            self.logger_testop,
            mode)(
            jinja2.Template(mssg).render(
                iddict,
                pre=predict,
                post=postdict),
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
        id_val = {}
        for j in range(len(id_list)):
            val = post_node.xpath(
                id_list[j])[0].text.strip() if post_node.xpath(
                id_list[j]) else None
            iddict[
                'id_' +
                str(j)] = val
            id_val[id_list[j]] = val

        return iddict, prenode, postnode, id_val

    def _find_value(self, predict, postdict, element, postnode, prenode):
        """
        get value of element node for test operation
        in case of attributes, attribute values are given directly
        in case of element node, need to use text to get node value
        """
        if isinstance(postnode, lxml.etree._Element):
            post_nodevalue = postnode.text.strip(
            ) if postnode.text is not None else None
        else:
            post_nodevalue = postnode
        if isinstance(prenode, lxml.etree._Element):
            pre_nodevalue = prenode.text.strip(
            ) if prenode.text is not None else None
        else:
            pre_nodevalue = prenode
        predict[element] = pre_nodevalue
        postdict[element] = post_nodevalue
        return predict, postdict, post_nodevalue, pre_nodevalue

    def _get_data(self, id_list, nodes, ignore_null=None):
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
            xlist = []
            for id in id_list:
                id_nodes = path.findall(id)
                if self._is_ignore_null(ignore_null) and not id_nodes:
                    continue
                xlist.append(id_nodes)
            # xlist = [path.findall(id) for id in id_list]
            val = []
            for values in xlist:
                if values is not None:
                    if isinstance(values, list):
                        val1 = [v.text for v in values]
                        val.append(tuple(val1))
                    else:
                        val.append(values.text)
          #  val.append(i)
            if val:
                data[tuple(val)] = path
        
        return data

    def _get_nodevalue(
            self, predict, postdict, pre_nodes, post_nodes, x_path, element, mssg):
        """
        Used to calculate value of any node mentioned inside info and error messages
        """
        mssg = re.findall('{{\s?(.*?)\s?}}', mssg)
        for e in mssg:
            if (e.startswith("post") or e.startswith("Post")):
                val = e[6:-2]
                if val not in [x_path, element]:
                    postdict[val] = post_nodes.findtext(
                        val).strip()if post_nodes.findtext(val) is not None else None

            if (e.startswith("pre") or e.startswith("PRE")):
                val = e[5:-2]
                if val not in [x_path, element]:
                    predict[val] = pre_nodes.findtext(
                        val).strip() if pre_nodes.findtext(val) is not None else None
        return predict, postdict


    def _is_ignore_null(self, ignore_null):
        if ignore_null and ((type(ignore_null) is bool and ignore_null is True) \
                or  (type(ignore_null) is str and ignore_null.lower() == 'true')):
            return True
        return False


    def exists(self, x_path, ele_list, err_mssg, info_mssg,
               teston, iter, id_list, xml1, xml2, ignore_null=None):
        """
        Calculate if node value is present in given snapshot
        """
        self.print_testmssg("exists")
        res = True
        predict = {}
        postdict = {}
        iddict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': 'exists',
            'passed': [],
            'failed': [],
        #     'pre_xml': xml1,
        #     'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}> ".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    #### get element node for test operation ####
                    # if length of pre node is less than post node, assign
                    # sample node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))
                    iddict, prenode, postnode, id_val = self._find_element(
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
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])

                            node_value_passed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'actual_node_value': post_nodevalue}
                            tresult['passed'].append(
                                deepcopy(node_value_passed))
                            self._print_message(
                                info_mssg,
                                iddict,
                                predict,
                                postdict,
                                "debug")
                            count_pass = count_pass + 1
                    else:
                        res = False
                        self._print_message(
                            err_mssg,
                            iddict,
                            predict,
                            postdict,
                            "info")
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict}
                        tresult['failed'].append(deepcopy(node_value_failed))

        if res is False:
            msg = 'All "%s" do not exists at xpath "%s" [ %d matched / %d failed ]' % (
                element, x_path, count_pass, count_fail)
            self._print_result(msg, res)
        elif res is True:
            msg = 'All "%s" exists at xpath "%s" [ %d matched ]' % (
                element, x_path, count_pass)
            self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def not_exists(self, x_path, ele_list, err_mssg, info_mssg,
                   teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("not-exists")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "not-exists",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))
                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            res = False
                            self._print_message(
                                err_mssg,
                                iddict,
                                predict,
                                postdict,
                                "info")
                            count_fail = count_fail + 1
                            node_value_failed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'actual_node_value': post_nodevalue}
                            tresult['failed'].append(
                                deepcopy(node_value_failed))
                    else:
                        self._print_message(
                            info_mssg,
                            iddict,
                            predict,
                            postdict,
                            "debug")
                        count_pass = count_pass + 1
                        node_value_passed = {
                            'id': id_val,
                            'PRE': predict,
                            'POST': postdict}
                        tresult['passed'].append(deepcopy(node_value_passed))
        if res is False:
            msg = ' "%s" exists at xpath "%s" [ %d matched / %d failed ]' % (
                element, x_path, count_pass, count_fail)
            self._print_result(msg, res)
        elif res is True:
            msg = 'All "%s" do not exists at xpath "%s" [ %d matched ]' % (
                element, x_path, count_pass)
            self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def all_same(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("all-same")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "all-same",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                if len(ele_list) >= 2:
                    vpath = x_path + ele_list[1] + '/' + ele_list[0]
                    value1 = xml2.xpath(vpath)
                    value = value1[0].text.strip() if len(
                        value1) != 0 else None
                else:
                    nodes_found = xml2.xpath(
                                    x_path +
                                    '/' +
                                    ele_list[0])
                    value = nodes_found[0].text.strip() if nodes_found else None
                #if value is None, then no nodes were found. Illogical to continue when ignore_null is None
                if value is None:
                    if self._is_ignore_null(ignore_null):
                        self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path + '/' + ele_list[0]),
                                    extra=self.log_detail)
                        res = None
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                                "ERROR!! Nodes are not present in given Xpath: <{}>".format(
                                    x_path +'/' +ele_list[0]), 
                                    extra=self.log_detail)

                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': iddict,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None,
                            'xpath_error': True}
                        tresult['failed'].append(deepcopy(node_value_failed))

                else:
                    
                    tresult['expected_node_value'] = value
                    for i in range(len(post_nodes)):
                        # if length of pre node is less than post node, assign
                        # sample xml element node
                        if i >= len(pre_nodes):
                            pre_nodes.append(etree.XML('<sample></sample>'))

                        iddict, prenode, postnode, id_val = self._find_element(
                            id_list, iddict, element, pre_nodes[i], post_nodes[i])
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                        if postnode:
                            for k in range(len(postnode)):
                                # if length of pre node is less than post node,
                                # assign sample node
                                if k >= len(prenode):
                                    prenode.append(etree.XML('<sample></sample>'))

                                predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                    predict, postdict, element, postnode[k], prenode[k])
                                if post_nodevalue != value:
                                    res = False
                                    count_fail = count_fail + 1
                                    self._print_message(
                                        err_mssg,
                                        iddict,
                                        predict,
                                        postdict,
                                        "info")
                                    node_value_failed = {
                                        'id': id_val,
                                        'pre': predict,
                                        'post': postdict,
                                        'actual_node_value': post_nodevalue}
                                    tresult['failed'].append(
                                        deepcopy(node_value_failed))
                                else:
                                    count_pass = count_pass + 1
                                    self._print_message(
                                        info_mssg,
                                        iddict,
                                        predict,
                                        postdict,
                                        "debug")
                                    node_value_passed = {
                                        'id': id_val,
                                        'pre': predict,
                                        'post': postdict,
                                        'actual_node_value': post_nodevalue}
                                    tresult['passed'].append(
                                        deepcopy(node_value_passed))
                        else:
                            #this condition arises when certain parent nodes don't have the searched child node.
                            #If ignore-null is True then we skip those cases else raise an error
                            if self._is_ignore_null(ignore_null):
                                self.logger_testop.debug(colorama.Fore.YELLOW +
                                            "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                                element, 
                                                x_path, 
                                                id_val),
                                            extra=self.log_detail)
                                is_skipped = True
                                continue
                            
                            self.logger_testop.error(colorama.Fore.RED +
                                                    "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path, id_val), extra=self.log_detail)
                            node_value_failed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'actual_node_value': None}
                            tresult['failed'].append(deepcopy(node_value_failed))
                            res = False
                            count_fail = count_fail + 1


        if not( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'Value of all "%s" at xpath "%s" is not same [ %d matched / %d failed ]' % (
                    element, x_path, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'Value of all "%s" at xpath "%s" is same [ %d matched ]' % (
                    element, x_path, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def is_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("is-equal")
        res = True
        is_skipped=False
        predict = {}
        postdict = {}
        iddict = {}
        count_pass = 0
        count_fail = 0
        tresult = {
            'xpath': x_path,
            'testoperation': "is-equal",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        try:
            element = ele_list[0]
            value = ele_list[1].strip()
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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>O".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node

                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])

                            if post_nodevalue == value:
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                                count_pass = count_pass + 1
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                            else:
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                                res = False
                                count_fail = count_fail + 1
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                    else:
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path, 
                                            id_val),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue

                        self.logger_testop.error(colorama.Fore.RED +
                                                 "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path, id_val), extra=self.log_detail)
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))
                        res = False
                        count_fail = count_fail + 1
        
        if not( is_skipped is True and count_pass==0 and count_fail==0 ):
            if res is False:
                msg = 'All "%s" is not equal to "%s" [ %d matched / %d failed ]' % (
                    element, value, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" is equal to "%s" [ %d matched ]' % (
                    element, value, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def not_equal(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("not-equal")
        res = True
        is_skipped = False
        predict = {}
        postdict = {}
        iddict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "not-equal",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
        try:
            element = ele_list[0]
            value = ele_list[1].strip()
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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            if post_nodevalue != value:
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                count_pass = count_pass + 1
                            else:
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                                res = False
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                count_fail = count_fail + 1
                    else:
                        # tresult['actual_node_value'].append(None)
                        
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path,
                                            id_val),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue
                        
                        self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                    id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))

        if not( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "%s" is equal to "%s" [ %d matched / %d failed ]' % (
                    element, value, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" is not equal to "%s" [ %d matched ]' % (
                    element, value, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def in_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("in-range")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "in-range",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
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
            if range1 > range2:
                self.logger_testop.error(
                    colorama.Fore.RED +
                    "Range values are not valid, start range must be less than end range",
                    extra=self.log_detail)
                res = False
            else:
                tresult['node_name'] = element
                tresult['expected_node_value'] = [range1, range2]
                pre_nodes, post_nodes = self._find_xpath(
                    iter, x_path, xml1, xml2)
                if not post_nodes:
                    if self._is_ignore_null(ignore_null):
                        self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                        res = None
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                                                "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': iddict,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None,
                            'xpath_error': True}
                        tresult['failed'].append(deepcopy(node_value_failed))

                else:
                    for i in range(len(post_nodes)):
                        # if length of pre node is less than post node, assign
                        # sample xml element node
                        if i >= len(pre_nodes):
                            pre_nodes.append(etree.XML('<sample></sample>'))

                        iddict, prenode, postnode, id_val = self._find_element(
                            id_list, iddict, element, pre_nodes[i], post_nodes[i])
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                        if postnode:
                            for k in range(len(postnode)):
                                # if length of pre node is less than post node,
                                # assign sample node
                                if k >= len(prenode):
                                    prenode.append(
                                        etree.XML('<sample></sample>'))

                                predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                    predict, postdict, element, postnode[k], prenode[k])
                                if (float(post_nodevalue) >= range1
                                        and float(post_nodevalue) <= range2):
                                    self._print_message(
                                        info_mssg,
                                        iddict,
                                        predict,
                                        postdict,
                                        "debug")
                                    count_pass = count_pass + 1
                                    node_value_passed = {
                                        'id': id_val,
                                        'pre': predict,
                                        'post': postdict,
                                        'actual_node_value': post_nodevalue}
                                    tresult['passed'].append(
                                        deepcopy(node_value_passed))
                                else:
                                    res = False
                                    self._print_message(
                                        err_mssg,
                                        iddict,
                                        predict,
                                        postdict,
                                        "info")
                                    count_fail = count_fail + 1
                                    node_value_failed = {
                                        'id': id_val,
                                        'pre': predict,
                                        'post': postdict,
                                        'actual_node_value': post_nodevalue}
                                    tresult['failed'].append(
                                        deepcopy(node_value_failed))

                        else:
                            ##
                            if self._is_ignore_null(ignore_null):
                                self.logger_testop.debug(colorama.Fore.YELLOW +
                                            "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                                element, 
                                                x_path, 
                                                id_val),
                                            extra=self.log_detail)
                                is_skipped = True
                                continue
                            
                            self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                        id_val), extra=self.log_detail)
                            res = False
                            count_fail = count_fail + 1
                            node_value_failed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'actual_node_value': None}
                            tresult['failed'].append(
                                deepcopy(node_value_failed))
        
        if not ( is_skipped and count_fail == 0 and count_pass == 0 ): 
            if res is False:
                msg = 'All "%s" is not in range:  "%f - %f" [ %d matched / %d failed ]' % (
                    element, range1, range2, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" is in range "%f - %f" [ %d matched ]' % (
                    element, range1, range2, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def not_range(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("not-range")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "not-range",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
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
            if range1 > range2:
                self.logger_testop.error(
                    colorama.Fore.RED +
                    "Range values are not valid, start range must be less than end range",
                    extra=self.log_detail)
                res = False
            else:
                tresult['node_name'] = element
                tresult['expected_node_value'] = [range1, range2]
                pre_nodes, post_nodes = self._find_xpath(
                    iter, x_path, xml1, xml2)
                if not post_nodes:
                    
                    if self._is_ignore_null(ignore_null):
                        self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                        res = None
                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                                                "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': iddict,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None,
                            'xpath_error': True}
                        tresult['failed'].append(deepcopy(node_value_failed))

                else:
                    for i in range(len(post_nodes)):
                        # if length of pre node is less than post node, assign
                        # sample xml element node
                        if i >= len(pre_nodes):
                            pre_nodes.append(etree.XML('<sample></sample>'))

                        iddict, prenode, postnode, id_val = self._find_element(
                            id_list, iddict, element, pre_nodes[i], post_nodes[i])
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                        predict, postdict = self._get_nodevalue(
                            predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                        if postnode:
                            for k in range(len(postnode)):
                                # if length of pre node is less than post node,
                                # assign sample node
                                if k >= len(prenode):
                                    prenode.append(
                                        etree.XML('<sample></sample>'))

                                predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                    predict, postdict, element, postnode[k], prenode[k])
                                if float(post_nodevalue) <= range1 or float(
                                        post_nodevalue) >= range2:
                                    count_pass = count_pass + 1
                                    self._print_message(
                                        info_mssg,
                                        iddict,
                                        predict,
                                        postdict,
                                        "debug")
                                    node_value_passed = {
                                        'id': id_val,
                                        'pre': predict,
                                        'post': postdict,
                                        'actual_node_value': post_nodevalue}
                                    tresult['passed'].append(
                                        deepcopy(node_value_passed))
                                else:
                                    res = False
                                    count_fail = count_fail + 1
                                    self._print_message(
                                        err_mssg,
                                        iddict,
                                        predict,
                                        postdict,
                                        "info")
                                    node_value_failed = {
                                        'id': id_val,
                                        'pre': predict,
                                        'post': postdict,
                                        'actual_node_value': post_nodevalue}
                                    tresult['failed'].append(
                                        deepcopy(node_value_failed))
                        else:
                            ##
                            if self._is_ignore_null(ignore_null):
                                self.logger_testop.debug(colorama.Fore.YELLOW +
                                            "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                                element, 
                                                x_path, 
                                                id_val),
                                            extra=self.log_detail)
                                is_skipped = True
                                continue
                            
                            
                            self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                        id_val), extra=self.log_detail)
                            res = False
                            count_fail = count_fail + 1
                            node_value_failed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'actual_node_value': None}
                            tresult['failed'].append(
                                deepcopy(node_value_failed))
        
        if not ( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "%s" is in range:  "%f - %f" [ %d matched / %d failed ]' % (
                    element, range1, range2, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" is not in range "%f - %f" [ %d matched ]' % (
                    element, range1, range2, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def is_gt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("is-gt")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "is-gt",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
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
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                    x_path),
                                extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for j in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if j >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[j], prenode[j])
                            if (float(post_nodevalue) > val1):
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                count_pass = count_pass + 1
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                            else:
                                res = False
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                count_fail = count_fail + 1
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))

                    else:
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element,
                                            x_path, 
                                            id_val),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue

                        self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                    id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))

        if not ( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "%s" is not greater than  "%d" [ %d matched / %d failed ]' % (
                    element, val1, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" is greater than %d" [ %d matched ]' % (
                    element, val1, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def is_lt(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("is-lt")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "is-lt",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0

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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                    x_path),
                                extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))
            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            if (float(post_nodevalue) < val1):
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                count_pass = count_pass + 1
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                            else:
                                res = False
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                count_fail = count_fail + 1
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                    else:
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path, 
                                            id_val),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue
                        
                        self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                    id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))

        if not ( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "%s" is not less than %d" [ %d matched / %d failed ]' % (
                    element, val1, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" is less than %d [ %d matched ]' % (
                    element, val1, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def contains(self, x_path, ele_list, err_mssg, info_mssg,
                 teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("contains")
        predict = {}
        postdict = {}
        iddict = {}
        res = True
        is_skipped = False
        tresult = {
            'xpath': x_path,
            'testoperation': "contains",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0

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
               
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(x_path),
                                extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED + "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))
                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict[element] = prenode[k].text
                            postdict[element] = postnode[k].text
                            if (postnode[k].text.find(value) == -1):
                                res = False
                                count_fail = count_fail + 1
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': postnode[k].text}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                            else:
                                count_pass = count_pass + 1
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': postnode[k].text}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                    else:
                        
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path, 
                                            id_val
                                            ),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue
                        
                        self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                    id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))
        
        if not ( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "%s" do not contains %s" [ %d matched / %d failed ]' % (
                    element, value, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" contains %s [ %d matched ]' % (
                    element, value, count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def is_in(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("is-in")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "is-in",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0

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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                    x_path
                                    ),
                                extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            if (post_nodevalue in value_list):
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                count_pass = count_pass + 1
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                            else:
                                res = False
                                count_fail = count_fail + 1
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                    else:
                        
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path, 
                                            id_val
                                            ),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue
                            
                        self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                    id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))

        if not( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "{0}" is not in list {1} [ {2} matched / {3} failed ]'.format(
                    element,
                    value_list,
                    count_pass,
                    count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "{0}" is in list {1}  [ {2} matched ]'.format(
                    element,
                    value_list,
                    count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def not_in(self, x_path, ele_list, err_mssg,
               info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("not-in")
        res = True
        is_skipped = False
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "not-in",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0

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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                    x_path
                                    ),
                                extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(x_path), extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)

                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])
                            if (post_nodevalue not in value_list):
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                count_pass = count_pass + 1
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                            else:
                                res = False
                                count_fail = count_fail + 1
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                    else:
                        
                        ##
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path, 
                                            id_val
                                            ),
                                        extra=self.log_detail)
                            is_skipped = False
                            continue
                        self.logger_testop.error(colorama.Fore.RED + "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path,
                                                                                                                                    id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))

        if not( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = '"{0}" is in list {1} [ {2} matched / {3} failed ]'.format(
                    element,
                    value_list,
                    count_pass,
                    count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "{0}" is not in list {1}  [ {2} matched ]'.format(
                    element,
                    value_list,
                    count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    ################## operator requiring two snapshots, pre and post ########
    def no_diff(self, x_path, ele_list, err_mssg,
                info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("no-diff")
        res = True
        iddict = {}
        predict = {}
        postdict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "no-diff",
            'node_name': ele_list[0],
            'failed': [],
            'passed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_pass = 0
        count_fail = 0
        id_val = {}

        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
        if re.match(ele_list[0], "no node"):
            self.logger_testop.error(colorama.Fore.RED +
                                     "ERROR!! 'no-diff' operator requires node value to test !!", extra=self.log_detail)
        else:
            if (not pre_nodes) or (not post_nodes):

                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(
                                                x_path),
                                            extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))

            else:
                # assuming one iterator has unique set of ids, i.e only one node matching to id
                # making dictionary for id and its corresponding xpath
                # one xpath has only one set of id
                data1 = self._get_data(id_list, pre_nodes, ignore_null)
                data2 = self._get_data(id_list, post_nodes, ignore_null)
                # making union of id keys
                data1_key = set(data1.keys())
                data2_key = set(data2.keys())
                keys_union = data1_key.union(data2_key)

                if not keys_union:
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present for given IDs: {}".format(
                                        id_list),
                                    extra=self.log_detail)
                    res = None
                # iterating through ids which are present either in pre
                # snapshot or post snapshot or both
                for k in keys_union:
                    for length in range(len(k)):
                        # making dictionary of ids for given xpath, ex id_0,
                        # id_1 ..etc
                        iddict[
                            'id_' + str(length)] = [k[length][i].strip() for i in range(len(k[length]))]
                    if k in data1 and k in data2:
                        # mapping id name to its value
                        for length in range(len(k)):
                            id_val[id_list[length]] = k[length][0].strip()

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

                        predict[ele_list[0]] = val_list1
                        postdict[ele_list[0]] = val_list2

                        if val_list1 != val_list2:
                            res = False
                            count_fail = count_fail + 1
                            self._print_message(
                                err_mssg,
                                iddict,
                                predict,
                                postdict,
                                "info")
                            node_value_failed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'pre_node_value': val_list1,
                                'post_node_value': val_list2}
                            tresult['failed'].append(
                                deepcopy(node_value_failed))

                        else:
                            count_pass = count_pass + 1
                            self._print_message(
                                info_mssg,
                                iddict,
                                predict,
                                postdict,
                                "debug")
                            node_value_passed = {
                                'id': id_val,
                                'pre': predict,
                                'post': postdict,
                                'pre_node_value': val_list1,
                                'post_node_value': val_list2}
                            tresult['passed'].append(
                                deepcopy(node_value_passed))

                    else:
                        self.logger_testop.error(colorama.Fore.RED +
                                                 "ID gone missing!!!", extra=self.log_detail)
                        # mapping id name to its value
                        for length in range(len(k)):
                            id_val[id_list[length]] = k[length][0].strip()
                        if k in data1:
                            self.logger_testop.error(
                                "ID list '%s' is not present in post snapshot" %
                                iddict, extra=self.log_detail)
                            tresult['failed'].append(
                                {'id_missing_post': deepcopy(id_val)})
                        else:
                            self.logger_testop.error(
                                "ID list '%s' is not present in pre snapshot" %
                                iddict, extra=self.log_detail)
                            tresult['failed'].append(
                                {'id_missing_pre': deepcopy(id_val)})
                        # tresult['id_miss_match'].append(iddict.copy())
                        self.logger_testop.debug(colorama.Fore.RED +
                                                 jinja2.Template(
                                                     err_mssg).render(
                                                     iddict,
                                                     pre=predict,
                                                     post=postdict), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
        if res is False:
            msg = 'All "{0}" is not same in pre and post snapshot [ {1} matched / {2} failed ]'.format(
                tresult['node_name'],
                count_pass,
                count_fail)
            self._print_result(msg, res)
        elif res is True:
            msg = 'All "{0}" is same in pre and post snapshot [ {1} matched ]'.format(
                tresult['node_name'],
                count_pass)
            self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def list_not_less(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("list-not-less")
        res = True
        tresult = {
            'xpath': x_path,
            'testoperation': "list-not-less",
            'node_name': ele_list[0],
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        iddict = {}
        predict = {}
        postdict = {}
        count_pass = 0
        count_fail = 0
        id_val = {}

        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)

        if not pre_nodes or not post_nodes:
           
            if self._is_ignore_null(ignore_null):
                self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                res = None
            else:
                self.logger_testop.error(colorama.Fore.RED +
                                        "ERROR!! Nodes are not present in given Xpath: <{}>".format(
                                            x_path),
                                        extra=self.log_detail)
                res = False
                count_fail = count_fail + 1
                node_value_failed = {
                    'id': iddict,
                    'pre': predict,
                    'post': postdict,
                    'actual_node_value': None,
                    'xpath_error': True}
                tresult['failed'].append(deepcopy(node_value_failed))
        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath

            predata = self._get_data(id_list, pre_nodes, ignore_null)
            postdata = self._get_data(id_list, post_nodes, ignore_null)

            if not predata:
                self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present for given IDs: {}".format(
                                        id_list),
                                    extra=self.log_detail)
                res = None

            for k in predata:
                for length in range(len(k)):
                    iddict['id_' + str(length)] = [k[length][i].strip()
                                                   for i in range(len(k[length]))]
                for length in range(len(k)):
                    id_val[id_list[length]] = k[length][0].strip()

                if k in postdata:
                    predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                            x_path, ele_list[0], err_mssg)
                    predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                            x_path, ele_list[0], info_mssg)

                    if not re.match(ele_list[0], "no node"):
                        # predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                        #                                        x_path, ele_list[0], err_mssg)
                        # predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                        # x_path, ele_list[0], info_mssg)
                        ele_xpath1 = predata.get(k).xpath(ele_list[0])
                        ele_xpath2 = postdata.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip()
                                     for element in ele_xpath1]
                        val_list2 = [element.text.strip()
                                     for element in ele_xpath2]
                        # tresult['pre_node_value'].append(val_list1)
                        # tresult['post_node_value'].append(val_list2)
                        for val1 in val_list1:
                            predict[ele_list[0]] = val1
                            if val1 not in val_list2:
                                # user can only ask for values which are in pre
                                # and not in post
                                res = False
                                count_fail = count_fail + 1
                                self.logger_testop.info("Missing node : %s for element tag %s and parent element %s" % (val1, ele_xpath1[0].tag,
                                                                                                                        ele_xpath1[0].getparent().tag), extra=self.log_detail)
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'pre_node_value': val1,
                                    'post_node_value': ''}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))

                            else:
                                count_pass = count_pass + 1
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'pre_node_value': val1,
                                    'post_node_value': val1}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                    else:
                        count_pass = count_pass + 1
                        self._print_message(
                            info_mssg,
                            iddict,
                            predict,
                            postdict)
                        node_value_passed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict}
                        tresult['passed'].append(deepcopy(node_value_passed))
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                             "ID gone missing !! ", extra=self.log_detail)
                    for length in range(len(k)):
                        id_val[id_list[length]] = k[length][0].strip()
                    self.logger_testop.error(
                        "ID list ' %s ' is not present in post snapshots " %
                        iddict, extra=self.log_detail)
                    # tresult['id_miss_match'].append(iddict.copy())
                    tresult['failed'].append(
                        {'id_missing_post': deepcopy(id_val)})
                    self._print_message(
                        err_mssg,
                        iddict,
                        predict,
                        postdict,
                        "info")
                    res = False
                    count_fail = count_fail + 1
        if res is False:
            msg = 'All "{0}" in pre snapshot is not present in post snapshot [ {1} matched / {2} failed ]'.format(
                tresult['node_name'],
                count_pass,
                count_fail)
            self._print_result(msg, res)
        elif res is True:
            msg = 'All "{0}" in pre snapshot is present in post snapshot [ {1} matched ]'.format(
                tresult['node_name'],
                count_pass)
            self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def list_not_more(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("list-not-more")
        res = True
        tresult = {
            'xpath': x_path,
            'testoperation': "list-not-more",
            'node_name': ele_list[0],
            'failed': [],
            'passed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        iddict = {}
        predict = {}
        postdict = {}
        count_pass = 0
        count_fail = 0
        id_val = {}

        pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
        if not pre_nodes or not post_nodes:
            
            if self._is_ignore_null(ignore_null):
                self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                res = None
            else:
                self.logger_testop.error(colorama.Fore.RED +
                                        "ERROR!! Nodes are not present in given Xpath: <{}>".format(
                                            x_path),
                                        extra=self.log_detail)
                res = False
                count_fail = count_fail + 1
                node_value_failed = {
                    'id': iddict,
                    'pre': predict,
                    'post': postdict,
                    'actual_node_value': None,
                    'xpath_error': True}
                tresult['failed'].append(deepcopy(node_value_failed))
        else:
            # assuming one iterator has unique set of ids, i.e only one node matching to id
            # making dictionary for id and its corresponding xpath
            predata = self._get_data(id_list, pre_nodes, ignore_null)
            postdata = self._get_data(id_list, post_nodes, ignore_null)

            if not predata:
                self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present for given IDs: {}".format(
                                        id_list),
                                    extra=self.log_detail)
                res = None
            
            for k in postdata:
                for length in range(len(k)):
                    #iddict['id_' + str(length)] = k[length].strip()
                    iddict['id_' + str(length)] = [k[length][i].strip()
                                                   for i in range(len(k[length]))]
                for length in range(len(k)):
                    id_val[id_list[length]] = k[length][0].strip()

                if k in predata:
                    predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                            x_path, ele_list[0], err_mssg)
                    predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                                                            x_path, ele_list[0], info_mssg)

                    if not re.match(ele_list[0], "no node"):
                        #                        predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                        #                                                                x_path, ele_list[0], err_mssg)
                        #                        predict, postdict = self._get_nodevalue(predict, postdict, predata[k], postdata[k],
                        # x_path, ele_list[0], info_mssg)
                        ele_xpath1 = predata.get(k).xpath(ele_list[0])
                        ele_xpath2 = postdata.get(k).xpath(ele_list[0])
                        val_list1 = [element.text.strip()
                                     for element in ele_xpath1]
                        val_list2 = [element.text.strip()
                                     for element in ele_xpath2]
                        for val2 in val_list2:
                            postdict[ele_list[0]] = val2
                            if val2 not in val_list1:
                                res = False
                                count_fail = count_fail + 1
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'pre_node_value': '',
                                    'post_node_value': val2}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                                self.logger_testop.error("Missing node: %s for element tag: %s and parent element %s" % (val2, ele_xpath2[0].tag,
                                                                                                                         ele_xpath2[0].getparent().tag), extra=self.log_detail)
                                self._print_message(
                                    err_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "info")
                            else:
                                count_pass = count_pass + 1
                                self._print_message(
                                    info_mssg,
                                    iddict,
                                    predict,
                                    postdict,
                                    "debug")
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'pre_node_value': val2,
                                    'post_node_value': val2}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))
                    else:
                        count_pass = count_pass + 1
                        self._print_message(
                            info_mssg,
                            iddict,
                            predict,
                            postdict,
                            "debug")
                        node_value_passed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict}
                        tresult['passed'].append(deepcopy(node_value_passed))
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                             "ID gone missing!!", extra=self.log_detail)
                    for length in range(len(k)):
                        id_val[id_list[length]] = k[length][0].strip()
                    self.logger_testop.error(
                        "\nID list ' %s ' is not present in pre snapshots" %
                        iddict, extra=self.log_detail)
                    tresult['failed'].append(
                        {'id_missing_pre': deepcopy(id_val)})
                    # tresult['id_miss_match'].append(iddict.copy())
                    self._print_message(
                        err_mssg,
                        iddict,
                        predict,
                        postdict,
                        "info")
                    res = False
                    count_fail = count_fail + 1

        if res is False:
            msg = 'All "{0}" in post snapshot is not present in pre snapshot [ {1} matched / {2} failed ]'.format(
                tresult['node_name'],
                count_pass,
                count_fail)
            self._print_result(msg, res)
        elif res is True:
            msg = 'All "{0}" in post snapshot is present in pre snapshot [ {1} matched ]'.format(
                tresult['node_name'],
                count_pass)
            self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def delta(self, x_path, ele_list, err_mssg,
              info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("delta")
        res = True
        is_skipped = False
        tresult = {
            'xpath': x_path,
            'testoperation': "delta",
            'passed': [],
            'failed': [],
            'node_name': ele_list[0],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        iddict = {}
        predict = {}
        postdict = {}
        count_pass = 0
        count_fail = 0
        id_val = {}

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
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present in given Xpath: <{}>".format(
                                        x_path),
                                    extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in given Xpath: <{}>".format(
                                                x_path),
                                            extra=self.log_detail)
                    res = False
                    count_fail = count_fail + 1
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))
            else:
                # assuming one iterator has unique set of ids, i.e only one node matching to id
                # making dictionary for id and its corresponding xpath

                predata = self._get_data(id_list, pre_nodes, ignore_null)
                postdata = self._get_data(id_list, post_nodes, ignore_null)

                predata_keys = set(predata.keys())
                postdata_keys = set(postdata.keys())
                keys_union = predata_keys.union(postdata_keys)

                if not keys_union:
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                    "SKIPPING!! Nodes are not present for given IDs: {}".format(
                                        id_list),
                                    extra=self.log_detail)
                    res = None
                    is_skipped = True

                for k in keys_union:
                    # checking if id in first data set is present in second data
                    # set or not
                    for length in range(len(k)):
                        #iddict['id_' + str(length)] = k[length]
                        iddict[
                            'id_' + str(length)] = [k[length][i].strip() for i in range(len(k[length]))]

                    for length in range(len(k)):
                        id_val[id_list[length]] = k[length][0].strip()

                    if k in predata and k in postdata:
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
                                predict[node_name] = val1
                                postdict[node_name] = val2

                                # for negative percentage
                                if re.search('%', del_val) and (
                                        re.search('-', del_val)):
                                    dvalue = abs(float(delta_val.strip('%')))
                                    mvalue = val1 - ((val1 * dvalue) / 100)
                                    if (val2 > val1 or val2 < mvalue):
                                        res = False
                                        count_fail = count_fail + 1
                                        self._print_message(
                                            err_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "info")
                                        node_value_failed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['failed'].append(
                                            deepcopy(node_value_failed))
                                    else:
                                        count_pass = count_pass + 1
                                        self._print_message(
                                            info_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "debug")
                                        node_value_passed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['passed'].append(
                                            deepcopy(node_value_passed))

                                # for positive percent change
                                elif re.search('%', del_val) and (re.search('/+', del_val)):
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue = val1 + ((val1 * dvalue) / 100)
                                    if (val2 < val1 or val2 > mvalue):
                                        res = False
                                        count_fail = count_fail + 1
                                        self._print_message(
                                            err_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "info")
                                        node_value_failed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['failed'].append(
                                            deepcopy(node_value_failed))

                                    else:
                                        count_pass = count_pass + 1
                                        self._print_message(
                                            info_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "debug")
                                        node_value_passed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['passed'].append(
                                            deepcopy(node_value_passed))

                                # absolute percent change
                                elif re.search('%', del_val):
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue1 = val1 - (val1 * dvalue) / 100
                                    mvalue2 = val1 + (val1 * dvalue) / 100
                                    if (val2 < mvalue1 or val2 > mvalue2):
                                        res = False
                                        count_fail = count_fail + 1
                                        self._print_message(
                                            err_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "info")
                                        node_value_failed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['failed'].append(
                                            deepcopy(node_value_failed))
                                    else:
                                        count_pass = count_pass + 1
                                        self._print_message(
                                            info_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "debug")
                                        node_value_passed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['passed'].append(
                                            deepcopy(node_value_passed))

                                # for negative change
                                elif re.search('-', del_val):
                                    dvalue = abs(float(delta_val.strip('%')))
                                    mvalue = val1 - dvalue
                                    if (val2 < mvalue or val2 > val1):
                                        res = False
                                        count_fail = count_fail + 1
                                        self._print_message(
                                            err_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "info")
                                        node_value_failed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['failed'].append(
                                            deepcopy(node_value_failed))
                                    else:
                                        count_pass = count_pass + 1
                                        self._print_message(
                                            info_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "debug")
                                        node_value_passed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['passed'].append(
                                            deepcopy(node_value_passed))

                                 # for positive change
                                elif re.search('\+', del_val):
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue = val1 + dvalue
                                    if (val2 >= mvalue or val2 <= val1):
                                        res = False
                                        count_fail = count_fail + 1
                                        self._print_message(
                                            err_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "info")
                                        node_value_failed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['failed'].append(
                                            deepcopy(node_value_failed))
                                    else:
                                        count_pass = count_pass + 1
                                        self._print_message(
                                            info_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "debug")
                                        node_value_passed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['passed'].append(
                                            deepcopy(node_value_passed))
                                else:
                                    dvalue = float(delta_val.strip('%'))
                                    mvalue1 = val1 - dvalue
                                    mvalue2 = val1 + dvalue
                                    if (val2 < mvalue1 or val2 > mvalue2):
                                        res = False
                                        count_fail = count_fail + 1
                                        self._print_message(
                                            err_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "info")
                                        node_value_failed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['failed'].append(
                                            deepcopy(node_value_failed))
                                    else:
                                        count_pass = count_pass + 1
                                        self._print_message(
                                            info_mssg,
                                            iddict,
                                            predict,
                                            postdict,
                                            "debug")
                                        node_value_passed = {
                                            'id': id_val,
                                            'pre': predict,
                                            'post': postdict,
                                            'pre_node_value': val1,
                                            'post_node_value': val2}
                                        tresult['passed'].append(
                                            deepcopy(node_value_passed))
                            else:
                                
                                if self._is_ignore_null(ignore_null):
                                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                                "SKIPPING!! Node <{}> not found at xpath <{}> ".format(
                                                    node_name,
                                                    x_path),
                                                extra=self.log_detail)
                                    is_skipped = True
                                    continue
                                
                                self.logger_testop.error(
                                    colorama.Fore.RED +
                                    "ERROR!! Node <{}> not found at xpath <{}> ".format(
                                        node_name,
                                        x_path),
                                    extra=self.log_detail)
                                res = False
                                count_fail = count_fail + 1
                    else:
                        
                        for length in range(len(k)):
                            id_val[id_list[length]] = k[length][0].strip()

                        self.logger_testop.error(
                            colorama.Fore.RED +
                            "\nID gone missing!!",
                            extra=self.log_detail)
                        if k in predata:
                            self.logger_testop.error(
                                "ID list '%s' is not present in post snapshot" %
                                iddict, extra=self.log_detail)
                            tresult['failed'].append(
                                {'id_missing_post': deepcopy(id_val)})
                        else:
                            self.logger_testop.error(
                                "ID list '%s' is not present in pre snapshot" %
                                iddict, extra=self.log_detail)
                            tresult['failed'].append(
                                {'id_missing_pre': deepcopy(id_val)})
                        self._print_message(
                            err_mssg,
                            iddict,
                            predict,
                            postdict,
                            "info")
                        res = False
                        count_fail = count_fail + 1
        
        if not( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "{0}" is not with in delta difference of {1} [ {2} matched / {3} failed ]'.format(
                    node_name,
                    delta_val,
                    count_pass,
                    count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "{0}" is with in delta difference of {1} [ {2} matched ]'.format(
                    node_name,
                    delta_val,
                    count_pass)
                self._print_result(msg, res)

        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
        self.test_details[teston].append(tresult)

    def regex(
            self, x_path, ele_list, err_mssg, info_mssg, teston, iter, id_list, xml1, xml2, ignore_null=None):
        self.print_testmssg("regex")
        res = False
        is_skipped = False
        predict = {}
        postdict = {}
        iddict = {}
        tresult = {
            'xpath': x_path,
            'testoperation': "regex",
            'passed': [],
            'failed': [],
            # 'pre_xml': xml1,
            # 'post_xml': xml2
        }
        count_fail = 0
        count_pass = 0
        try:
            element = ele_list[0]
            value = ele_list[1]
        except IndexError as e:
            self.logger_testop.error(colorama.Fore.RED +
                                     "\nError occurred while accessing test element %s" % e.message, extra=self.log_detail)
            self.logger_testop.error(colorama.Fore.RED +
                                     "\n'regex' test operator requires two parameter", extra=self.log_detail)
            raise
        else:
            tresult['node_name'] = element
            tresult['expected_node_value'] = value
            pre_nodes, post_nodes = self._find_xpath(iter, x_path, xml1, xml2)
            if not post_nodes:
                
                if self._is_ignore_null(ignore_null):
                    self.logger_testop.debug(colorama.Fore.YELLOW +
                                "SKIPPING!! Nodes are not present in Xpath <%s> !!".format(
                                    x_path),
                                extra=self.log_detail)
                    res = None
                else:
                    self.logger_testop.error(colorama.Fore.RED +
                                            "ERROR!! Nodes are not present in Xpath <%s> !!" % x_path, extra=self.log_detail)
                    count_fail = count_fail + 1
                    res = False
                    node_value_failed = {
                        'id': iddict,
                        'pre': predict,
                        'post': postdict,
                        'actual_node_value': None,
                        'xpath_error': True}
                    tresult['failed'].append(deepcopy(node_value_failed))
            else:
                for i in range(len(post_nodes)):
                    # if length of pre node is less than post node, assign
                    # sample xml element node
                    if i >= len(pre_nodes):
                        pre_nodes.append(etree.XML('<sample></sample>'))

                    iddict, prenode, postnode, id_val = self._find_element(
                        id_list, iddict, element, pre_nodes[i], post_nodes[i])
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, err_mssg)
                    predict, postdict = self._get_nodevalue(
                        predict, postdict, pre_nodes[i], post_nodes[i], x_path, element, info_mssg)
                    if postnode:
                        for k in range(len(postnode)):
                            # if length of pre node is less than post node,
                            # assign sample node
                            if k >= len(prenode):
                                prenode.append(etree.XML('<sample></sample>'))

                            predict, postdict, post_nodevalue, pre_nodevalue = self._find_value(
                                predict, postdict, element, postnode[k], prenode[k])

                            if re.search(value, post_nodevalue):
                                res = True
                                count_pass = count_pass + 1
                                self.logger_testop.debug(
                                    jinja2.Template(
                                        info_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                                node_value_passed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['passed'].append(
                                    deepcopy(node_value_passed))

                            else:
                                res = False
                                count_fail = count_fail + 1
                                self.logger_testop.info(
                                    jinja2.Template(
                                        err_mssg.replace(
                                            '-',
                                            '_')).render(
                                        iddict,
                                        pre=predict,
                                        post=postdict), extra=self.log_detail)
                                node_value_failed = {
                                    'id': id_val,
                                    'pre': predict,
                                    'post': postdict,
                                    'actual_node_value': post_nodevalue}
                                tresult['failed'].append(
                                    deepcopy(node_value_failed))
                    else:
                        
                        if self._is_ignore_null(ignore_null):
                            self.logger_testop.debug(colorama.Fore.YELLOW +
                                        "SKIPPING!! Node <{}> not found at xpath <{}> for IDs: {}".format(
                                            element, 
                                            x_path, 
                                            id_val),
                                        extra=self.log_detail)
                            is_skipped = True
                            continue  
                        
                        self.logger_testop.error(colorama.Fore.RED +
                                                 "ERROR!! Node <{}> not found at xpath <{}> for IDs: {}".format(element, x_path, id_val), extra=self.log_detail)
                        res = False
                        count_fail = count_fail + 1
                        node_value_failed = {
                            'id': id_val,
                            'pre': predict,
                            'post': postdict,
                            'actual_node_value': None}
                        tresult['failed'].append(deepcopy(node_value_failed))
        
        if not( is_skipped and count_fail == 0 and count_pass == 0 ):
            if res is False:
                msg = 'All "%s" do not match with regex  "%s" [ %d matched / %d failed ]' % (
                    element, value, count_pass, count_fail)
                self._print_result(msg, res)
            elif res is True:
                msg = 'All "%s" matches with regex "%s" [ %d matched ]' % (
                    element, value, count_pass)
                self._print_result(msg, res)
            
        #tresult['info'] = info_mssg
        #tresult['err'] = err_mssg
        tresult['result'] = res
        tresult['count'] = {'pass': count_pass, 'fail': count_fail}
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
        for test_name in self.result_dict:
            color = colorama.Fore.YELLOW
            res = "Skipped"
            if self.result_dict[test_name] is True:
                color = colorama.Fore.GREEN
                res = "Passed"
            elif self.result_dict[test_name] is False:
                color = colorama.Fore.RED
                res = "Failed"
            self.logger_testop.info(
                color + 
                "{} : {}".format(
                    test_name,
                    res
                ), extra=logs
            )
        self.logger_testop.info(
            colorama.Fore.GREEN +
            "Total No of tests passed: {}".format(
                self.no_passed), extra=logs)
        self.logger_testop.info(
            colorama.Fore.RED +
            "Total No of tests failed: {} ".format(
                self.no_failed), extra=logs)
        
        evaluated_result = True
        for result in self.result_dict:
            if self.result_dict[result] is False:
                evaluated_result = False
                break
            
        
        if evaluated_result is False:
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
        elif evaluated_result is True:
            self.logger_testop.info(
                colorama.Fore.GREEN +
                colorama.Style.BRIGHT +
                "Overall Tests passed!!! ", extra=logs)
            self.result = "Passed"
