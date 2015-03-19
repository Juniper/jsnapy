import yaml
from lxml import etree
import testop
import os,sys
import subprocess
from jnpr.jsnap.sqlite_get import SqliteExtractXml


class Comparator:

    # Extract xpath and other values for comparing two snapshots and
    # testop.Operator methods to perform tests
    def compare_reply(self, op, tests, teston, check, snap1, snap2=None):
        tests = [i for i in tests if i.has_key('iterate')]
        for test in tests:
            x_path = test['iterate']['xpath']
            if 'id' in test['iterate']:
                id = test['iterate']['id']
                id_list= [val.strip() for val in id.split(',')]
            else:
                id_list = []
            for path in test['iterate']['tests']:
                values = ['err', 'info']
                testvalues = path.keys()
                testop = [
                    tvalue for tvalue in testvalues if tvalue not in values][0]
                ele = path[testop]
                if ele is not None:
                    ele_list = [elements.strip() for elements in ele.split(',')]
                err_mssg = path['err']
                info_mssg = path['info']
                if os.path.isfile(snap1):
                    xml1 = etree.parse(snap1)
                else:
                    print "ERROR, Pre snapshot file %s is not present in given path!!" %snap1
                    sys.exit(1)
                if testop in [
                        'no-diff', 'list-not-less', 'list-not-more', 'delta']:
                    if check is True:
                        if os.path.isfile(snap2):
                            xml2 = etree.parse(snap1)
                        else:
                            print "ERROR, Post snapshot File %s is not present in given path!!" %snap2
                            sys.exit(1)
                        op.define_operator(
                            testop,
                            x_path,
                            ele_list,
                            err_mssg,
                            info_mssg,
                            teston,
                            id_list,
                            xml1,
                            xml2)
                    else:
                        print "Test Operator %s is allowed only with --check" % testop

            # if test operators are other than above mentioned four operators
                else:
                    # if check is used with uni operand test operator then use
                    # second snapshot file
                    xmlfile = etree.parse(snap2) if check is True else etree.parse(snap1)
                    op.define_operator(
                        testop,
                        x_path,
                        ele_list,
                        err_mssg,
                        info_mssg,
                        teston,
                        id_list,
                        xmlfile)

# SQLite changes
    def compare_reply_sqlite(self, op, tests, teston, check, snapdata1, snapdata2=None):
        tests = [i for i in tests if i.has_key('iterate')]
        for test in tests:
            x_path = test['iterate']['xpath']
            if 'id' in test['iterate']:
                id = test['iterate']['id']
                id_list= [val.strip() for val in id.split(',')]
            else:
                id_list = []
            for path in test['iterate']['tests']:
                values = ['err', 'info']
                testvalues = path.keys()
                testop = [
                    tvalue for tvalue in testvalues if tvalue not in values][0]
                ele = path[testop]
                if ele is not None:
                    ele_list = [elements.strip() for elements in ele.split(',')]
                err_mssg = path['err']
                info_mssg = path['info']
                xml1 = etree.fromstring(snapdata1)
                if testop in [
                        'no-diff', 'list-not-less', 'list-not-more', 'delta']:
                    if check is True:
                        xml2 = etree.fromstring(snapdata2)
                        op.define_operator(
                            testop,
                            x_path,
                            ele_list,
                            err_mssg,
                            info_mssg,
                            teston,
                            id_list,
                            xml1,
                            xml2)
                    else:
                        print "Test Operator %s is allowed only with --check" % testop

            # if test operators are other than above mentioned four operators
                else:
                    # if check is used with uni operand test operator then use
                    # second snapshot file
                    xmlfile = etree.fromstring(snapdata2) if check is True else etree.fromstring(snapdata1)
                    op.define_operator(
                        testop,
                        x_path,
                        ele_list,
                        err_mssg,
                        info_mssg,
                        teston,
                        id_list,
                        xmlfile)
###


    def compare_diff(self, pre_snap_file, post_snap_file):
        #p= subprocess.Popen(["which", "icdiff"],stdout=subprocess.PIPE)
        #out, err = p.communicate()
        # print "output is", out
        p = subprocess.Popen(["/usr/local/bin/icdiff",
                              pre_snap_file,
                              post_snap_file],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        print "Difference in file is:", out


# generate names of snap files from hostname and out files given by user,
# tests are performed on values stored in these snap filesin which test is
# to be performed

    def generate_test_files(
            self, main_file, device, check, diff, use_sqlite, db_name, pre=None, post=None):
        op = testop.Operator()
        # print "pre, post are:", pre, post
        tests_files = []
        path = os.getcwd()
        # get the test files from config.yml
        if main_file.get('tests') is None:
            print "\n No testfile, Please mention test files !!"
        else:
            for tfiles in main_file.get('tests'):
                filename = os.path.join(os.getcwd(), 'configs', tfiles)
                testfile = open(filename, 'r')
                tfiles = yaml.load(testfile)
                tests_files.append(tfiles)
            for t in tests_files:
                tests_included = t['tests_include']
                print (40) * '*' + "\nPerforming test on Device: " + \
                    device + "\n" + (40) * '*'
                for val in tests_included:
                    print "\nTests Included: %s " % (val)
                    if t[val][0].keys()[0] == 'command':
                        command = t[val][0]['command']
                        print (40) * '*' + "\n Command is " + \
                            command + "\n" + (40) * '*'
                        name = '_'.join(command.split())
                        teston= command
                    else:
                        rpc = t[val][0]['rpc']
                        print (40) * '*' + "\n RPC is " + \
                            rpc + "\n" + (40) * '*'
                        name = rpc
                        teston= rpc
                    file1 = str(device) + '_' + pre + '_' + name + '.xml'
                    snapfile1 = os.path.join(path, 'snapshots', file1)

                    ### SQLite Changes
                    if use_sqlite is True:
                        a = SqliteExtractXml(db_name)
                        pre_snap_data = a.get_xml_using_snapname(str(device), name, pre)

                    if check is True:
                        if use_sqlite is True:
                            post_snap_data = a.get_xml_using_snapname(str(device), name, post)
                            self.compare_reply_sqlite(
                                op,
                                t[val],
                                teston,
                                check,
                                pre_snap_data,
                                post_snap_data)

                        else:
                            file2 = str(device) + '_' + post + '_' + name + '.xml'
                            snapfile2 = os.path.join(path, 'snapshots', file2)
                            self.compare_reply(
                                op,
                                t[val],
                                teston,
                                check,
                                snapfile1,
                                snapfile2)
                    elif(diff is True):
                        file2 = str(device) + '_' + post + '_' + name + '.xml'
                        snapfile2 = os.path.join(path, 'snapshots', file2)
                        self.compare_diff(snapfile1, snapfile2)
                    else:

                        if use_sqlite is True:
                            self.compare_reply_sqlite(
                                op,
                                t[val],
                                teston,
                                check,
                                pre_snap_data)
                        else:
                            self.compare_reply(
                                op,
                                t[val],
                                teston,
                                check,
                                snapfile1)
                    ###

            if (diff is not True):
                op.final_result()
                return op

