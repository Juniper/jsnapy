import yaml
from lxml import etree
import testop
import os
import sys
import subprocess
import shlex


class Comparator:

    # Extract xpath and other values for comparing two snapshots and
    # testop.Operator methods to perform tests
    def compare_reply(self, op, tests, teston, check, snap1, snap2=None):
        for i in range(1, len(tests)):
            x_path = tests[i]['iterate']['xpath']
            # print "tests[i]['iterate']:", tests[i]['iterate']
            if 'id' in tests[i]['iterate']:
                id = tests[i]['iterate']['id']
            else:
                id = 0
            for path in tests[i]['iterate']['tests']:
                values = ['err', 'info']
                testvalues = path.keys()
                testop = [
                    tvalue for tvalue in testvalues if tvalue not in values][0]
                ele = path[testop]
                if ele is not None:
                    ele_list = [i.strip() for i in ele.split(',')]
                err_mssg = path['err']
                info_mssg = path['info']
                snap_file1 = snap1
                # print "snap_file1", snap_file1
                try:
                    xml1 = etree.parse(snap_file1)
                except IOError as e:
                    print "\n Error occurred ", e.message
                if testop in [
                        'no-diff', 'list-not-less', 'list-not-more', 'delta']:
                    if check is True:
                        try:
                            snap_file2 = snap2
                            xml2 = etree.parse(snap_file2)
                        except IndexError as e:
                            print "\n Error Occurred ", e.message
                            print "\n test operator ", testop, " require two snap files\n"
                        except IOError as e:
                            print "\n Error Occurred ", e.message

                        op.define_operator(
                            testop,
                            x_path,
                            ele_list,
                            err_mssg,
                            info_mssg,
                            teston,
                            id,
                            xml1,
                            xml2)
                    else:
                        print "Testoperator %s is allowed only with --check" % testop
            # if test operators are other than above mentioned four operators
                else:
                    # if check is used with uni operand test operator then use
                    # second snapshot file
                    if check is True:
                        try:
                            snap_file2 = snap2
                            xml2 = etree.parse(snap_file2)
                        except IndexError as e:
                            print "\n Error Occurred ", e.message
                            print "\n test operator ", testop, " require two snap files\n"
                        except IOError as e:
                            print "\n Error Occurred ", e.message
                        else:
                            op.define_operator(
                                testop,
                                x_path,
                                ele_list,
                                err_mssg,
                                info_mssg,
                                teston,
                                id,
                                xml2)
                    else:
                        op.define_operator(
                            testop,
                            x_path,
                            ele_list,
                            err_mssg,
                            info_mssg,
                            teston,
                            id,
                            xml1)

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
            self, main_file, device, check, diff, pre=None, post=None):
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
                # print "testfile name is",filename
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
                        file1 = str(device) + '_' + pre + '_' + name + '.xml'
                        snapfile1 = os.path.join(path, 'snapshots', file1)

                        if post is not None:
                            file2 = str(device) + '_' + post + \
                                '_' + name + '.xml'
                            snapfile2 = os.path.join(path, 'snapshots', file2)
                        if (check is True):
                            try:
                                self.compare_reply(
                                    op,
                                    t[val],
                                    command,
                                    check,
                                    snapfile1,
                                    snapfile2)
                            except UnboundLocalError as e:
                                print "\n Error Occurred ", e.message
                                print "\n --check require two snap files\n"
                                sys.exit()
                        elif(diff is True):
                            self.compare_diff(snapfile1, snapfile2)
                        else:
                            self.compare_reply(
                                op,
                                t[val],
                                command,
                                check,
                                snapfile1)

                    else:
                        rpc = t[val][0]['rpc']
                        print (40) * '*' + "\n RPC is " + \
                            rpc + "\n" + (40) * '*'
                        file1 = str(device) + '_' + pre + '_' + rpc + '.xml'
                        snapfile1 = os.path.join(path, 'snapshots', file1)
                        if post is not None:
                            file2 = str(device) + '_' + post + \
                                '_' + rpc + '.xml'
                            snapfile2 = os.path.join(path, 'snapshots', file2)
                        if (check is True):
                            try:
                                self.compare_reply(
                                    op,
                                    t[val],
                                    rpc,
                                    check,
                                    snapfile1,
                                    snapfile2)
                            except UnboundLocalError as e:
                                print "\n Error Occurred ", e.message
                                print "\n --check require two snap files\n"
                                sys.exit()
                        elif(diff is True):
                            self.compare_diff(snapfile1, snapfile2)
                        else:
                            self.compare_reply(
                                op,
                                t[val],
                                rpc,
                                check,
                                snapfile1)

            if (diff is not True):
                op.final_result()
                return op
