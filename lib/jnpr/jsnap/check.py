import yaml
from lxml import etree
import testop
import os


class Comparator:

    def __init__(self):
        self.op = testop.Operator()

    # Extract xpath and other values for comparing two snapshots and
    # testop.Operator methods to perform tests
    def compare_reply(self, tests, teston, device, *args):
        for i in range(1, len(tests)):
            x_path = tests[i]['iterate']['xpath']
            id = tests[i]['iterate']['id']
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
                pre_snap_file = args[0]
                try:
                    xml1 = etree.parse(pre_snap_file)
                except IOError as e:
                    print "\n *********** Error occurred ************", e.message
                if testop in [
                        'no-diff', 'list-not-less', 'list-not-more', 'delta']:
                    try:
                        post_snap_file = args[1]
                        xml2 = etree.parse(post_snap_file)
                    except IndexError as e:
                        print "\n ******** Error Occurred ********", e.message
                        print "\n ******** test operator ", testop, " require two snap files ********\n"
                    except IOError as e:
                        print "\n ******** Error Occurred **********", e.message
                    else:
                        self.op.define_operator(
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
                    self.op.define_operator(
                        testop,
                        x_path,
                        ele_list,
                        err_mssg,
                        info_mssg,
                        teston,
                        id,
                        xml1)

# generate names of snap files from hostname and out files given by user,
# tests are performed on values stored in these snap filesin which test is
# to be performed

    def generate_test_files(self, main_file, devices, check, *args):
        tests_files = []
        path = os.getcwd()
        for tfiles in main_file['tests']:
            tfiles = open(tfiles, 'r')
            tfiles = yaml.load(tfiles)
            tests_files.append(tfiles)
        for t in tests_files:
            tests_included = t['tests_include']
            for d in devices:
                print "\n*****************************************************************\n"
                print " Performing test on Device: ", d
                print "\n*****************************************************************"
                for val in tests_included:
                    print "\nTests Included: %s " % (val)
                    if t[val][0].keys()[0] == 'command':
                        command = t[val][0]['command']
                        print "\n-------------------------------------------------------------"
                        print "      Command is: %s" % (command)
                        print "---------------------------------------------------------------\n"
                        name = '_'.join(command.split())
                        pre_snap_file = path + '/' + 'snapshots' + '/' + \
                            str(d) + '_' + args[0] + '_' + name + '.xml'
                        if (check is True):
                            print "args[1]", args[1]
                            post_snap_file = path + '/' + 'snapshots' + '/' + \
                                str(d) + '_' + args[1] + '_' + name + '.xml'

                            self.compare_reply(
                                t[val],
                                command,
                                d,
                                pre_snap_file,
                                post_snap_file)
                        else:
                            self.compare_reply(t[val], pre_snap_file)
                    else:
                        rpc = t[val][0]['rpc']
                        print "\n-------------------------------------------------------------"
                        print "      RPC is: %s" % (rpc)
                        print "---------------------------------------------------------------\n"
                        pre_snap_file = path + '/' + 'snapshots' + '/' + \
                            str(d) + '_' + args[0] + '_' + rpc + '.xml'
                        if (check is True):
                            post_snap_file = path + '/' + 'snapshots' + '/' + \
                                str(d) + '_' + args[1] + '_' + rpc + '.xml'
                            self.compare_reply(
                                t[val],
                                rpc,
                                d,
                                pre_snap_file,
                                post_snap_file)
                        else:
                            self.compare_reply(t[val], pre_snap_file)
