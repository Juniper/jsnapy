#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import re
import sys
import colorama
import logging
import yaml
from lxml import etree
from jnpr.jsnapy.operator import Operator
from jnpr.jsnapy.sqlite_get import SqliteExtractXml
from icdiff import diff, codec_print, get_options, ConsoleDiff
from jnpr.jsnapy.xml_comparator import XmlComparator
from jnpr.jsnapy import get_path


class Comparator:

    def __init__(self):
        self.logger_check = logging.getLogger(__name__)
        self.log_detail = {'hostname': None}
    

    def is_op(self, op):
        """
        Checks if the passed op is an operator or not
        """
        if op.lower() in ['and','not','or']:
            return True
        return False


    def is_unary_op(self, op):
        """
        Checks if the given op is unary or not
        """
        if op.lower() in ['not']:
            return True
        return False


    def is_binary_op(self, op):
        """
        Checks if the given op is binary or not
        """
        if op.lower() in ['and','or']:
            return True
        return False


    def generate_snap_file(self, device, prefix, name, reply_format):
        """
        This function generates name of snapshot files
        """
        if os.path.isfile(prefix):
            return prefix
        else:
            cmd_rpc_name = re.sub('/|\*|\.|-', '_', name)
            sfile = str(device) + '_' + prefix + '_' + \
                cmd_rpc_name + '.' + reply_format
            snapfile = os.path.join(
                get_path(
                    'DEFAULT',
                    'snapshot_path'),
                sfile)
            return snapfile
    
    def splitter(self,value):
        f = lambda x: x.split(']')[1].count(',') if '[' in x and ']' in x else x.count(',')
        value_list = [x[::-1].strip() for x in value[::-1].split(",",f(value))][::-1]
        return value_list

    def get_err_mssg(self, path, ele_list):
        """
        This function generates error message, if nothing is given then it will generate default error message
        """
        path_keys = ['err', 'info', 'ignore-null']
        value_list = []
        for key, value in path.items():
            if key not in path_keys and value:
                value_list = self.splitter(value)
        val = path.get('err')
        regex = r"\$(\d+)"
        i = 0
        if len(value_list) > 1 and val :
            for i in range(1,len(value_list)):
                val = re.sub(regex,value_list[i],val,count=1)
                i = i + 1
            path['err'] = val
        err_mssg = path.get('err', "Test FAILED: " +
                            ele_list[
                                0] + " before was < {{pre['" + ele_list[0] + "']}} >"
                            " now it is < {{post['" + ele_list[0] + "']}} > ")
        return err_mssg


    def get_info_mssg(self, path, ele_list):
        """
        This function generates info message, if nothing is given then it will generate default info message
        """
        path_keys = ['err', 'info', 'ignore-null']
        value_list = []
        for key, value in path.items():
            if key not in path_keys and value:
                value_list = self.splitter(value)
        val = path.get('info')
        regex = r"\$(\d+)"
        i = 0
        if len(value_list) > 1 and val :
            for i in range(1,len(value_list)):
                val = re.sub(regex,value_list[i],val,count=1)
                i = i + 1
            path['info'] = val
        info_mssg = path.get('info', "Test PASSED: " + ele_list[0] +
                             " before was < {{pre['" +
                             ele_list[0] +
                             "']}} > now it is < {{post['" +
                             ele_list[0] +
                             "']}} > ")
        return info_mssg


    def get_xml_reply(self, db, snap):
        """
        function is used to extract values from either xml file or from database
        :param db: name of database
        :param snap: snapfile
        :return: parsed snapshot
        """
        if db.get('check_from_sqlite') is True:
            if snap != str(None):
                xml_value = etree.fromstring(snap)
            else:
                self.logger_check.error(
                    colorama.Fore.RED +
                    "ERROR, Database for either pre or post snapshot is not present in given path !!",
                    extra=self.log_detail)
                return
        elif os.path.isfile(snap) and os.stat(snap).st_size > 0:
            xml_value = etree.parse(snap)
        ##### sometimes snapshot files are empty, when cmd/rpc reply do not contain any value
        elif os.path.isfile(snap) and os.stat(snap).st_size <= 0:
            self.logger_check.error(
                colorama.Fore.RED +
                "ERROR, Snapshot file is empty !!",
                extra=self.log_detail)
            return
        else:
            self.logger_check.error(
                colorama.Fore.RED +
                "ERROR, Snapshot file %s is not present in given path !!"%snap,
                extra=self.log_detail)
            return
        return xml_value

    def _get_testop(self, elem_list):
        exclusion_list = ['err', 'info', 'ignore-null']
        testop = [key.lower() for key in elem_list if key.lower() not in exclusion_list]
        testop = testop[0] if testop else "Define test operator"
        return testop

    def expression_evaluator(self, elem_test, op, x_path, id_list, iter, teston,
                                check, db, test_name, snap1, snap2=None, action=None, top_ignore_null=None):
        """
        Analyze the given elementary test case and call the appopriate operator
        like is_equal() or no_diff()
        call operator.Operator methods to compare snapshots based on given test cases
        :param elem_test: elementary test operation dictionary 
        :param op: operator.Operator object
        :param x_path: xpath for the command/rpc 
        :param id_list: id list of elements to use while matching up in different snapshots
        :param iter: True if iterate is specified in the test file
        :param teston: command/rpc to perform test
        :param check: variable to check if --check is given
        :param db: database handler
        :param snap1: pre snapshot file name
        :param snap2: post snapshot file name
        :param action: action taken in JSNAPy module version
        :param top_ignore_null: top level ignore-null value
        """
        # analyze individual test case and extract element list, info and
        # err message ####
        testop = self._get_testop(elem_test)

        ele = elem_test.get(testop)
        if ele is not None:
            ele_list = [elements.strip()
                        for elements in ele.split(',')]
        else:
            ele_list = ['no node']

        # extract err and info messages , if not given then set the
        # default error and info message
        err_mssg = self.get_err_mssg(elem_test, ele_list)
        info_mssg = self.get_info_mssg(elem_test, ele_list)
        ignore_null = elem_test.get('ignore-null') or top_ignore_null
        # check test operators, below mentioned four are allowed only
        # with --check ####
        is_skipped = False
        if testop in [
                'no-diff', 'list-not-less', 'list-not-more', 'delta']:
            if check is True or action is "check":
                xml1 = self.get_xml_reply(db, snap1)
                xml2 = self.get_xml_reply(db, snap2)
                if xml2 is None:
                    is_skipped = True
                else:
                    op.define_operator(
                        self.log_detail,
                        testop,
                        x_path,
                        ele_list,
                        err_mssg,
                        info_mssg,
                        teston,
                        iter,
                        id_list,
                        test_name,
                        xml1,
                        xml2,
                        ignore_null)
            else:
                self.logger_check.error(
                    colorama.Fore.RED +
                    "Test Operator %s is allowed only with --check" % testop, extra=self.log_detail)
                is_skipped = True
        # if test operators are other than above mentioned four operators
        else:
            # if check is used with uni operand test operator then use
            # second snapshot file
            if check is True or action is "check":
                pre_snap = self.get_xml_reply(db, snap1)
                post_snap = self.get_xml_reply(db, snap2)
            else:
                pre_snap = None
                post_snap = self.get_xml_reply(db, snap1)

            if post_snap is None:
                is_skipped = True
            else:
                op.define_operator(
                    self.log_detail,
                    testop,
                    x_path,
                    ele_list,
                    err_mssg,
                    info_mssg,
                    teston,
                    iter,
                    id_list,
                    test_name,
                    pre_snap,
                    post_snap,
                    ignore_null)
        if is_skipped:
            op.test_details[teston].append({'result': None})


    def expression_builder(self, sub_expr, parent_op=None, **kwargs):
        """
        Recursively builds the boolean expression of the provided sub_expr for evaluation
        :param sub_expr: dictionary object of the sub_expr that needs to be converted
        :param parent_op: parent operator of the sub_expr
        :param kwargs: dictionary of arguments required by function Comparator.expression_evaluator 
        :return: str object of the boolean expression formed of the provided sub_expr
        """
        ret_expr = []
        #perform validation
        if parent_op and (( len(sub_expr) > 1 and self.is_unary_op(parent_op) ) \
                or ( len(sub_expr) < 2 and self.is_binary_op(parent_op))):
            self.logger_check.info(
                    colorama.Fore.RED +
                    "ERROR!!! Malformed sub-expression", extra=self.log_detail)  
            return 
        for elem in sub_expr:
            keys = list(elem.keys())
            #this list helps us differentiate b/w conditional and elementary operation
            op_list = [k for k in keys if self.is_op(k)]
            if len(op_list) == 1:
                op = op_list[0]
                sub_expression = elem[op]
                sub_expr_ret = self.expression_builder(sub_expression, op, **kwargs)
                if sub_expr_ret is None or sub_expr_ret == str(None):
                    continue
                ret_expr.append(str(sub_expr_ret))
            elif len(op_list) == 0:
                #supposed to be the elementary operation
                self.expression_evaluator(elem,**kwargs)
                res = None
                #this should be guaranteed by the operator function, never use try-catch here
                last_test_instance = kwargs['op'].test_details[kwargs['teston']][-1]
                res = last_test_instance['result']

                testop = self._get_testop(elem)
                #for skipping cases
                if res is None or (last_test_instance['count']['pass'] == 0 and
                                   last_test_instance['count']['fail'] == 0 and
                                   testop not in ['no-diff',
                                                  'list-not-less',
                                                  'list-not-more'
                                                  ]):
                    continue
                    
                ret_expr.append(str(res))
                if res and parent_op and parent_op.lower() == 'or':
                    break
                if res is False and parent_op and parent_op.lower() == 'and':
                    break
            else:
                self.logger_check.info(
                    colorama.Fore.RED +
                    "ERROR!!! Malformed sub-expression", extra=self.log_detail)  
                continue  

        expr = ''
        if parent_op is None:
            if len(ret_expr) > 1:
                expr = ' and '.join(ret_expr)
            elif len(ret_expr) == 1 :
                expr = ret_expr[0]
        
        else:
            parent_op = str(parent_op).lower()

            if len(ret_expr) == 1 and self.is_unary_op(parent_op):
                expr = '{0} {1}'.format(parent_op,ret_expr[0])
            elif len(ret_expr) >= 1 :
                expr = ' {0} '.format(parent_op).join(ret_expr)
            if expr is not '':    
                expr  = '(' +expr+ ')'
        return expr
    

    def compare_reply(
            self, op, tests, test_name, teston, check, db, snap1, snap2=None, action=None):
        """
        Analyse test files and call respective methods in operator file
        like is_equal() or no_diff()
        call operator.Operator methods to compare snapshots based on given test cases
        Extract xpath and other values for comparing two snapshots and
        operator.Operator methods to perform tests
        :param op: operator.Operator object
        :param tests: test cases
        :param test_name: name of the test seequence as specified in the file
        :param teston: command/rpc to perform test
        :param check: variable to check if --check is given
        :param db: database handler
        :param snap1: pre snapshot file name
        :param snap2: post snapshot file name
        :param action: action taken in JSNAPy module version
        """

        top_ignore_null = False
        ignore_null_list = [t for t in tests if 'ignore-null' in t]
        if ignore_null_list:
            top_ignore_null =  ignore_null_list[0].get('ignore-null')
        ####     extract all test cases in given test file     ####
        tests = [t for t in tests if ('iterate' in t or 'item' in t)]
        if not len(tests) and (check is True or action is "check"):
            res = self.compare_xml(op, db, teston, snap1, snap2)
            if res is False:
                op.no_failed = op.no_failed + 1
            else:
                op.no_passed = op.no_passed + 1
        else:
            #this result is going to be associated with the whole test case   
            final_result = None

            for test in tests:
                if 'iterate' in test:
                    x_path = test.get('iterate').get('xpath', "no_xpath")
                    if 'id' in test.get('iterate'):
                        ids = test.get('iterate').get('id')
                        if isinstance(ids, list):
                            id_list = ids
                        else:
                            id_list = [val.strip() for val in ids.split(',')]
                    else:
                        id_list = []
                    testcases = test.get('iterate').get(
                        'tests', [{'Define test operator': 'tests not defined'}])
                    iter = True

                elif 'item' in test:
                    x_path = test.get('item').get('xpath', "no_xpath")
                    if 'id' in test.get('item'):
                        ids = test.get('item').get('id')
                        if isinstance(ids, list):
                            id_list = ids
                        else:
                            id_list = [val.strip() for val in ids.split(',')]
                    else:
                        id_list = []
                    testcases = test['item']['tests']
                    iter = False
      
                kwargs = {'op': op,
                          'x_path': x_path, 
                          'id_list': id_list, 
                          'iter': iter,
                          'teston': teston,
                          'check': check,
                          'db': db,
                          'test_name': test_name,
                          'snap1': snap1,
                          'snap2': snap2,
                          'action': action,
                          'top_ignore_null': top_ignore_null
                          }
                final_boolean_expr = self.expression_builder(testcases, None, **kwargs)
                #for cases where skip was encountered due to ignore-null 
                if final_boolean_expr is '' or final_boolean_expr is None or final_boolean_expr == str(None): 
                    continue

                result = eval(final_boolean_expr)
                if result is None:
                    continue
                if final_result is None:
                    final_result = True # making things normal
                final_result = final_result and result
            
            op.result_dict[test_name] = final_result

    def compare_diff(self, pre_snap_file, post_snap_file, check_from_sqlite):
        """
        This function is called when --diff is used
        """
        if check_from_sqlite:
            lines_a = pre_snap_file.splitlines(True)
            lines_b = post_snap_file.splitlines(True)
            headers = ("Snap_1", "Snap_2")
            options = get_options()[0]
            cd = ConsoleDiff(cols=int(options.cols),
                     show_all_spaces=options.show_all_spaces,
                     highlight=options.highlight,
                     no_bold=options.no_bold,
                     line_numbers=options.line_numbers,
                     tabsize=int(options.tabsize))
            for line in cd.make_table(
                    lines_a, lines_b, headers[0], headers[1],
                    context=(not options.whole_file),
                    numlines=int(options.unified)):
                codec_print(line, options)
                sys.stdout.flush()
        else:
            if os.path.isfile(pre_snap_file) and os.path.isfile(
                    post_snap_file):
                diff(pre_snap_file, post_snap_file)
            else:
                self.logger_check.info(
                    colorama.Fore.RED +
                    "ERROR!!! Files are not present in given path", extra=self.log_detail)


    def compare_xml(self, op, db, teston, pre_snap_value, post_snap_value):
        """
        This function is called when no testoperator is given and --check is used
        Compare two snapshots node by node without any pre defined criteria
        :param pre_snap_file: pre snapshots
        :param post_snap_file: post snapshots
        :return: True if no difference in files, false if there is difference
        """
        self.logger_check.info(
            colorama.Fore.BLUE +
            30 *
            '-' +
            "Performing --diff without any test operator" +
            30 *
            '-',
            extra=self.log_detail)
        pre_snap = self.get_xml_reply(db, pre_snap_value)
        post_snap = self.get_xml_reply(db, post_snap_value)
        flag = False

        # check if snapshots need to be taken from sqlite or from local system
        # ####
        try:
            if db.get('check_from_sqlite') is True:
                pre_root = pre_snap
                post_root = post_snap
            else:
                pre_root = pre_snap.getroot()
                post_root = post_snap.getroot()
        except Exception as ex:
            self.logger_check.error(
                colorama.Fore.RED +
                "Error!! from pre or post snap file: %s" %
                ex,
                extra=self.log_detail)
        else:
            result = []
            xml_comp = XmlComparator()
            if pre_root is not None and post_root is not None:
                tres = xml_comp.xml_compare(pre_root, post_root, result.append)
                self.logger_check.info(
                    colorama.Fore.BLUE +
                    (20) *
                    '-' +
                    "Performing --diff without test Operation " +
                    (20) *
                    '-',
                    extra=self.log_detail)
                self.logger_check.info(
                    colorama.Fore.BLUE +
                    "Difference in pre and post snap file", extra=self.log_detail)
                flag = tres['result']
            else:
                tres = {}
                result = []
                flag = False
                self.logger_check.error(
                    colorama.Fore.RED +
                    "Final result of --diff without test operator: FAILED",
                    extra=self.log_detail)
            if len(result) == 0 and flag is True:
                self.logger_check.info(
                    colorama.Fore.BLUE +
                    "    No difference   ",
                    extra=self.log_detail)
                self.logger_check.info(
                    colorama.Fore.GREEN +
                    "Final result of --diff without test operator: PASSED",
                    extra=self.log_detail)
            else:
                for index, res in enumerate(result):
                    self.logger_check.info(
                        colorama.Fore.RED +
                        str(index) +
                        "] " +
                        res,
                        extra=self.log_detail)
            op.test_details[teston].append(tres)
        return flag


    def generate_test_files(
            self, main_file, device, check, diff, db, snap_del, pre=None, action=None, post=None):
        """
        generate names of snap files from hostname and out files given by user,
        tests are performed on values stored in these snap files, in which test is
        to be performed
        :param main_file: main config file, to extract test files user wants to run
        :param device: device name
        :param check: variable to check if --check option is given or not
        :param diff: variable to check if --diff option is given or not
        :param db: database object
        :param snap_del: if --snapcheck operator is used without any test file name
                        it will create temprory file and then will delete it at the end
        :param pre: file name of pre snapshot
        :param post: file name of post snapshot
        :param action: given by module version, either snap, snapcheck or check
        :return: object of operator.Operator containing test details
        """
        op = Operator()
        op.device = device
        tests_files = []
        self.log_detail['hostname'] = device
        # get the test files from config.yml
        if main_file.get('tests') is None:
            self.logger_check.error(
                colorama.Fore.RED +
                "\nERROR!! No test file found, Please mention test files !!", extra=self.log_detail)
        else:
            # extract test files, first search in path given in jsnapy.cfg
            for tfile in main_file.get('tests'):
                if not os.path.isfile(tfile):
                    tfile = os.path.join(
                        get_path(
                            'DEFAULT',
                            'test_file_path'),
                        tfile)
                if os.path.isfile(tfile):
                    test_file = open(tfile, 'r')
                    tests_files.append(yaml.load(test_file))
                else:
                    self.logger_check.error(
                        colorama.Fore.RED +
                        "ERROR!! File %s not found for testing" %
                        tfile,
                        extra=self.log_detail)

            # check what all test cases need to be included, if nothing given
            # then include all test cases ####
            for tests in tests_files:
                tests_included = []
                if 'tests_include' in tests:
                    tests_included = tests.get('tests_include')
                else:
                    for t in tests:
                        tests_included.append(t)
                message= self._print_testmssg("Device: "+device, "*")
                self.logger_check.info(colorama.Fore.BLUE + message, extra=self.log_detail)
                for val in tests_included:
                    self.logger_check.info(
                        "Tests Included: %s " %
                        (val),
                        extra=self.log_detail)
                    try:
                        if 'command' in list(tests[val][0].keys()):
                            command = tests[val][0].get('command').split('|')[0].strip()
                            reply_format = tests[val][0].get('format', 'xml')
                            message = self._print_testmssg("Command: "+command, "*")
                        
                            self.logger_check.info(
                                colorama.Fore.BLUE +
                                message,
                                extra=self.log_detail)
                        
                            name = '_'.join(command.split())
                            teston = command
                        else:
                            rpc = tests[val][0]['rpc']
                            reply_format = tests[val][0].get('format', 'xml')
                            self.logger_check.info(colorama.Fore.BLUE + (25) * "*" + "RPC is " +
                                                   rpc + (25) * '*', extra=self.log_detail)
                            name = rpc
                            teston = rpc
                    except KeyError:
                        self.logger_check.error(
                            colorama.Fore.RED +
                            "ERROR occurred, test keys 'command' or 'rpc' not defined properly", extra=self.log_detail)
                    except Exception as ex:
                        self.logger_check.error(
                            colorama.Fore.RED +
                            "ERROR Occurred: %s" % str(ex), extra=self.log_detail)
                    else:
                        # extract snap files, if check from sqlite is true t
                        if db.get(
                                'check_from_sqlite') is True and (check is True or diff is True or action in ["check", "diff"]):
                            a = SqliteExtractXml(db.get('db_name'))
                            # while checking from database, preference is given
                            # to id and then snap name
                            if (db['first_snap_id'] is not None) and (
                                    db['second_snap_id'] is not None):
                                snapfile1, data_format1 = a.get_xml_using_snap_id(
                                    str(device), name, db['first_snap_id'])
                                snapfile2, data_format2 = a.get_xml_using_snap_id(
                                    str(device), name, db['second_snap_id'])
                            else:
                                snapfile1, data_format1 = a.get_xml_using_snapname(
                                    str(device), name, pre)
                                snapfile2, data_format2 = a.get_xml_using_snapname(
                                    str(device), name, post)
                            if reply_format != data_format1 or reply_format != data_format2:
                                self.logger_check.error(colorama.Fore.RED + "ERROR!! Data stored in database is not in %s format."
                                                        % reply_format, extra=self.log_detail)
                                pass
                                # sys.exit(1)
                        ###### taking snapshot for --snapcheck operation ####
                        elif db.get('check_from_sqlite') is True:
                            a = SqliteExtractXml(db.get('db_name'))
                            snapfile1, data_format1 = a.get_xml_using_snapname(
                                str(device), name, pre)
                            if reply_format != data_format1:
                                self.logger_check.error(
                                    colorama.Fore.RED +
                                    "ERROR!! Data stored in database is not in %s format." %
                                    reply_format,
                                    extra=self.log_detail)
                                pass
                                # sys.exit(1)
                        else:
                            snapfile1 = self.generate_snap_file(
                                device,
                                pre,
                                name,
                                reply_format)

                        # if check is true then call function to compare two
                        # snapshots ####
                        if (check is True or action is "check") and reply_format == 'xml':
                            if db.get('check_from_sqlite') is False:
                                snapfile2 = self.generate_snap_file(
                                    device,
                                    post,
                                    name,
                                    reply_format)
                            self.compare_reply(
                                op,
                                tests[val],
                                val,
                                teston,
                                check,
                                db,
                                snapfile1,
                                snapfile2,
                                action)

                        # if --diff is true then call compare_diff to compare
                        # two snapshots word by word ####
                        elif(diff is True):
                            if db.get('check_from_sqlite') is False:
                                snapfile2 = self.generate_snap_file(
                                    device,
                                    post,
                                    name,
                                    reply_format)
                            self.compare_diff(
                                snapfile1,
                                snapfile2,
                                db.get('check_from_sqlite'))

                        # else call --snapcheck test operation, it works only
                        # for xml reply format   ####
                        elif (reply_format == 'xml'):
                            self.compare_reply(
                                op,
                                tests[val],
                                val,
                                teston,
                                check,
                                db,
                                snapfile1,
                                action)
                            ######## bug here ############
                            # multiple testcases for single command and same device, its deleting that file
                            ####################
                            """
                            if snap_del is True:
                                snapfile1 = snapfile1 if os.path.isfile(snapfile1) else self.generate_snap_file(device, pre, name, reply_format)
                                os.remove(snapfile1)
                                """
                        else:
                            # give error message if snapshot in text format is
                            # used with operations other than --diff  ####
                            self.logger_check.error(
                                colorama.Fore.RED +
                                "ERROR!! for checking snapshots in text format use '--diff' option ", extra=self.log_detail)

            # print final result, if operation is --diff then message gets
            # printed compare_diff function only ####
            if (diff is not True):
                op.final_result(self.log_detail)

        return op


    def _print_testmssg(self, msg, delimiter):
        """
        Print info and error messages
        :param testname: test operation like "no-diff", "is-equal"
        """
        msg = ' '+msg+' '
        ln = int((80 - len(msg) - 2) / 2)
        testmssg = (ln * delimiter) + msg + (ln * delimiter)
        return testmssg
