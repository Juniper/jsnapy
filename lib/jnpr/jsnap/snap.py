from lxml import etree
import os
from jnpr.jsnap.sqlite_store import JsnapSqlite


class Parse:

    # generate snap files for devices based on given commands and rpc
    def generate_reply(self, test_file, dev, snap_files, use_sqlite, username, db_name):
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
                    rpc_reply = dev.rpc.cli(command, format='xml')
                    filename = snap_files + '_' + name + '.' + 'xml'
                    output_file = os.path.join(path, 'snapshots', filename)
                    with open(output_file, 'w') as f:
                        f.write(etree.tostring(rpc_reply))

                    # SQLiteChanges
                    if use_sqlite is True:
                        a = snap_files.split('_')
                        sqlite_jsnap = JsnapSqlite(a[0], db_name)
                        sqlite_jsnap.insert_data(etree.tostring(rpc_reply), username, name, a[1], filename)

                    ###

                elif 'rpc' in test_file[t][0]:
                    rpc = test_file[t][0]['rpc']
                    self.rpc_list.append(rpc)
                    if test_file[t][1].has_key('args'):
                        kwargs = {k.replace('-', '_'):v for k,v in test_file[t][1]['args'].items()}
                        rpc_reply = getattr(dev.rpc, rpc.replace('-', '_'))(**kwargs)
                    else:
                        rpc_reply = getattr(dev.rpc, rpc.replace('-', '_'))()
                    filename = snap_files + '_' + rpc + '.' + 'xml'
                    output_file = os.path.join(path, 'snapshots', filename)
                    with open(output_file, 'w') as f:
                        f.write(etree.tostring(rpc_reply))

                    # SQLiteChanges
                    if use_sqlite is True:
                        a = snap_files.split('_')
                        sqlite_jsnap = JsnapSqlite(a[0], db_name)
                        sqlite_jsnap.insert_data(etree.tostring(rpc_reply), username, rpc, a[1], filename)
                    ###
            else:
                print "Test case:  %s  not defined !!!!" % t
