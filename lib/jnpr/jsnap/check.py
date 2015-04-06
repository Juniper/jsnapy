import yaml
from lxml import etree
import jnpr.jsnap.testop
import os
import sys
from jnpr.jsnap.sqlite_get import SqliteExtractXml
import icdiff


class Comparator:

    # Extract xpath and other values for comparing two snapshots and
    # testop.Operator methods to perform tests
    def compare_reply(self, op, tests, teston, check, db, snap1, snap2=None):
        """
        call testop.Operator methods to compare snapshots based on given test cases
        :param op: testop.Operator object
        :param tests: test cases
        :param teston: command/rpc to perform test
        :param check: variable to check if --check is given
        :param db: database handler
        :param snap1: pre snapshot file name
        :param snap2: post snapshot file name
        :return:
        """
        tests = [t for t in tests if ('iterate' in t or 'item' in t)]
        for test in tests:
            if 'iterate' in test:
                x_path = test.get('iterate').get('xpath', "no_xpath")
                if 'id' in test.get('iterate'):
                    id = test.get('iterate').get('id')
                    id_list = [val.strip() for val in id.split(',')]
                else:
                    id_list = []
                testcases = test.get('iterate').get(
                    'tests', [{'Define test operator': 'tests not defined'}])
                iter = True

            elif 'item' in test:
                x_path = test.get('item').get('xpath', "no_xpath")
                if 'id' in test.get('item'):
                    id = test.get('item').get('id')
                    id_list = [val.strip() for val in id.split(',')]
                else:
                    id_list = []
                testcases = test['item']['tests']
                iter = False

            for path in testcases:
                values = ['err', 'info']
                testvalues = path.keys()
                # testop = [
                # tvalue for tvalue in testvalues if tvalue not in values][0]
                testop1 = [
                    tvalue for tvalue in testvalues if tvalue not in values]
                testop = testop1[0] if testop1 else "Define test operator"

                ele = path.get(testop)
                if ele is not None:
                    ele_list = [elements.strip()
                                for elements in ele.split(',')]
                else:
                    ele_list = ['no node']

                # set the default error and info message
                err_mssg = path.get(
                    'err',
                    "Test FAILED: " +
                    ele_list[0] +
                    " before was < {{pre['" +
                    ele_list[0] +
                    "']}} > now it is < {{post['" +
                    ele_list[0] +
                    "']}} > ")
                info_mssg = path.get(
                    'info',
                    "Test PASSED: " +
                    ele_list[0] +
                    " before was < {{pre['" +
                    ele_list[0] +
                    "']}} > now it is < {{post['" +
                    ele_list[0] +
                    "']}} > ")
                if db.get('check_from_sqlite') is True and check is True:
                    xml1 = etree.fromstring(snap1)
                else:
                    if os.path.isfile(snap1):
                        xml1 = etree.parse(snap1)
                    else:
                        print "ERROR, Pre snapshot file: %s is not present in given path !!" % snap1
                        sys.exit(1)
                if testop in [
                        'no-diff', 'list-not-less', 'list-not-more', 'delta']:
                    if check is True:
                        if db.get('check_from_sqlite') is True:
                            xml2 = etree.fromstring(snap2)
                        else:
                            if os.path.isfile(snap2):
                                xml2 = etree.parse(snap2)
                            else:
                                print "ERROR, Post snapshot File %s is not present in given path!!" % snap2
                                sys.exit(1)
                        op.define_operator(
                            testop,
                            x_path,
                            ele_list,
                            err_mssg,
                            info_mssg,
                            teston,
                            iter,
                            id_list,
                            xml1,
                            xml2)
                    else:
                        print "Test Operator %s is allowed only with --check" % testop

            # if test operators are other than above mentioned four operators
                else:
                    # if check is used with uni operand test operator then use
                    # second snapshot file
                    if db.get('check_from_sqlite') is True and check is True:
                        xmlfile1 = etree.fromstring(snap1)
                        xmlfile2 = etree.fromstring(snap2)

                    elif check is True:
                        xmlfile1 = etree.parse(snap1)
                        if os.path.isfile(snap2):
                            xmlfile2 = etree.parse(snap2)
                        else:
                            print "ERROR, --check require two snapfiles, file is not present in given path "
                            return

                    else:
                        xmlfile1 = None
                        # contains only one snapshot
                        xmlfile2 = etree.parse(snap1)

                    op.define_operator(
                        testop,
                        x_path,
                        ele_list,
                        err_mssg,
                        info_mssg,
                        teston,
                        iter,
                        id_list,
                        xmlfile1,
                        xmlfile2)

# not implemented for sqlite
    def compare_diff(self, pre_snap_file, post_snap_file):
        if os.path.isfile(pre_snap_file) and os.path.isfile(post_snap_file):
            icdiff.start(pre_snap_file, post_snap_file)
        else:
            print "ERROR!!! Files are not present in given path"

# generate names of snap files from hostname and out files given by user,
# tests are performed on values stored in these snap filesin which test is
# to be performed

    def generate_test_files(
            self, main_file, device, check, diff, db, pre=None, post=None):
        """
        generate pre and post snapshot file name to store snapshots and call compare_reply function

        :param main_file: main config file, to extract test files user wants to run
        :param device: device name
        :param check: variable to check if --check option is given or not
        :param diff: variable to check if --diff option is given or not
        :param db: database object
        :param pre: file name of pre snapshot
        :param post: file name of post snapshot
        :return:
        """
        op = testop.Operator()
        tests_files = []
        path = os.getcwd()
        # get the test files from config.yml
        if main_file.get('tests') is None:
            print "\nNo test file, Please mention test files !!"
        else:
            for tfiles in main_file.get('tests'):
                filename = os.path.join(os.getcwd(), 'configs', tfiles)
                if os.path.isfile(filename):
                    testfile = open(filename, 'r')
                    tfiles = yaml.load(testfile)
                    tests_files.append(tfiles)
                else:
                    print "File %s not found" % filename
            for t in tests_files:
                tests_included = t.get('tests_include')
                print (40) * '*' + "\nPerforming test on Device: " + \
                    device + "\n" + (40) * '*'
                if tests_included is not None:
                    for val in tests_included:
                        print "\nTests Included: %s " % (val)
                        try:
                            if t[val][0].keys()[0] == 'command':
                                command = t[val][0].get('command')
                                reply_format = t[val][0].get('format', 'xml')
                                print (40) * '*' + "\n Command is " + \
                                    command + "\n" + (40) * '*'
                                name = '_'.join(command.split())
                                teston = command
                            else:
                                rpc = t[val][0]['rpc']
                                reply_format = t[val][0].get('format', 'xml')
                                print (40) * '*' + "\n RPC is " + \
                                    rpc + "\n" + (40) * '*'
                                name = rpc
                                teston = rpc
                        except KeyError:
                            print "ERROR occurred, test keys 'command' or 'rpc' not defined properly"
                        except Exception as ex:
                            print "ERROR Occurred: ", ex
                        else:
                            if db.get(
                                    'check_from_sqlite') is True and check is True and reply_format == 'xml':
                                a = SqliteExtractXml(db.get('db_name'))
                                if (db['first_snap_id'] is not None) and (
                                        db['second_snap_id'] is not None):
                                    snapfile1, data_format = a.get_xml_using_snap_id(
                                        str(device),
                                        name,
                                        db['first_snap_id'])
                                else:
                                    snapfile1, data_format = a.get_xml_using_snapname(
                                        str(device),
                                        name,
                                        pre)
                                if data_format != 'xml':
                                    print "ERROR!! Data stored in database is not in xml format. " \
                                          "For checking snapshots in text format use '--diff' option "
                                    exit(1)
                            else:
                                file1 = str(device) + '_' + pre + \
                                    '_' + name + '.'+reply_format
                                snapfile1 = os.path.join(
                                    path,
                                    'snapshots',
                                    file1)

                            if check is True and reply_format == 'xml':
                                if db.get('check_from_sqlite') is True:
                                    if (db['first_snap_id'] is not None) and (
                                            db['second_snap_id'] is not None):
                                        snapfile2, data_format = a.get_xml_using_snap_id(
                                            str(device),
                                            name,
                                            db['second_snap_id'])
                                    else:
                                        snapfile2, data_format = a.get_xml_using_snapname(
                                            str(device),
                                            name,
                                            post)
                                    if data_format != 'xml':
                                        print "ERROR!! Data stored in database is not in xml format. " \
                                            "For checking snapshots in text format use '--diff' option "
                                        exit(1)
                                else:

                                    print str(device), post, name
                                    file2 = str(device) + '_' + post + \
                                        '_' + name + '.'+reply_format
                                    snapfile2 = os.path.join(
                                        path,
                                        'snapshots',
                                        file2)
                                self.compare_reply(
                                    op,
                                    t[val],
                                    teston,
                                    check,
                                    db,
                                    snapfile1,
                                    snapfile2)

                            # as of now diff is not implemented for diff
                            elif(diff is True):
                                file2 = str(device) + '_' + \
                                post + '_' + name + '.' + reply_format
                                snapfile2 = os.path.join(
                                    path,
                                    'snapshots',
                                    file2)
                                self.compare_diff(snapfile1, snapfile2)

                            elif (reply_format == 'xml'):
                                self.compare_reply(
                                    op,
                                    t[val],
                                    teston,
                                    check,
                                    db,
                                    snapfile1)
                            else:
                                print "ERROR!! for checking snapshots in text format use '--diff' option "
                else:
                    print "ERROR!!! None of the tests cases included"

            if (diff is not True):
                op.final_result()
                return op
