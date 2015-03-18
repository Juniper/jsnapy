from lxml import etree
import os
from jnpr.jsnap.jsnap_sqlite import JsnapSqlite


class Parse:

    # generate snap files for devices based on given commands and rpc
    def generate_reply(self, test_file, dev, snap_files, use_sqlite, username,db_name):
        self.command_list = []
        self.rpc_list = []
        self.test_included = []
        path = os.getcwd()
        for t in test_file['tests_include']:
            self.test_included.append(t)
            if t in test_file:
                if ('command' in test_file[t][0]):
                    command = test_file[t][0]['command']
                    self.command_list.append(command)
                    name = '_'.join(command.split())
                    dev.open()
                    rpc_reply = dev.rpc.cli(command, format='xml')
                    print "rpc reply:", etree.tostring(rpc_reply)
                    filename = snap_files + '_' + name + '.' + 'xml'
                    output_file = os.path.join(path, 'snapshots', filename)

                    with open(output_file, 'w') as f:
                        f.write(etree.tostring(rpc_reply))

                    # SQLiteChanges
                    if use_sqlite:
                        a = snap_files.split('_')
                        sqlite_jsnap = JsnapSqlite(a[0], db_name)
                        sqlite_jsnap.insert_data(etree.tostring(rpc_reply), username, name, a[1], filename)
                        # sqlite_jsnap.print_result()

                    ###
                elif('rpc' in test_file[t][0]):
                    rpc = test_file[t][0]['rpc']
                    self.rpc_list.append(rpc)
                    dev.open()
                    rpc_reply = getattr(dev.rpc, rpc.replace('-', '_'))()
                    print "rpc reply:", etree.tostring(rpc_reply)
                    filename = snap_files + '_' + rpc + '.' + 'xml'
                    output_file = os.path.join(path, 'snapshots', filename)
                    with open(output_file, 'w') as f:
                        f.write(etree.tostring(rpc_reply))

                    # SQLiteChanges
                    if use_sqlite:
                        a = snap_files.split('_')
                        sqlite_jsnap = JsnapSqlite(a[0], db_name)
                        sqlite_jsnap.insert_data(etree.tostring(rpc_reply), username, name, a[1], filename)
                        # sqlite_jsnap.print_result()

                    ###
            else:
                print "Test case:  %s  not defined !!!!" % t
