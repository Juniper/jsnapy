from lxml import etree
import os
from jnpr.jsnap.sqlite_store import JsnapSqlite


class Parse:

    # generate snap files for devices based on given commands and rpc
    def generate_reply(self, test_file, dev, snap_files, db, username):
        """
        generate rpc reply based on given commands/ rpc

        :param test_file: test file containing test cases
        :param dev: device handler
        :param snap_files: files to store snapshots
        :param db: name of database
        :param username: device's username
        :return:
        """
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
                    try:
                        rpc_reply = dev.rpc.cli(command, format='xml')
                    except Exception as ex:
                        print "ERROR occurred!!!",ex
                    else:
                        filename = snap_files + '_' + name + '.' + 'xml'
                        output_file = os.path.join(path, 'snapshots', filename)
                        with open(output_file, 'w') as f:
                            f.write(etree.tostring(rpc_reply))

                        # SQLiteChanges
                        if db['store_in_sqlite'] is True:
                            a = snap_files.split('_')
                            host = a[0]
                            a.pop(0)
                            a = '_'.join(a)
                            sqlite_jsnap = JsnapSqlite(host, db['db_name'])
                            db_dict = dict()
                            db_dict['username'] = username
                            db_dict['cli_command'] = name
                            db_dict['snap_name'] = a
                            db_dict['filename'] = filename
                            db_dict['xml'] = etree.tostring(rpc_reply)
                            sqlite_jsnap.insert_data(db_dict)
                        ###

                elif 'rpc' in test_file[t][0]:
                    rpc = test_file[t][0]['rpc']
                    self.rpc_list.append(rpc)
                    if 'args' in test_file[t][1]:
                        kwargs = {
                            k.replace(
                                '-',
                                '_'): v for k,
                            v in test_file[t][1]['args'].items()}
                        if 'filter_xml' in kwargs:
                            from lxml.builder import E
                            filter_data = None
                            for tag in kwargs['filter_xml'].split('/')[::-1]:
                                filter_data = E(tag) if filter_data is None else E(
                                    tag,
                                    filter_data)
                                kwargs['filter_xml'] = filter_data
                        try:
                            rpc_reply = getattr(
                                        dev.rpc,
                                        rpc.replace(
                                        '-',
                                        '_'))(
                                        **kwargs)
                        except Exception as ex:
                            print "ERROR occurred!!!", ex

                    else:
                        try:
                            rpc_reply = getattr(dev.rpc, rpc.replace('-', '_'))()
                        except Exception as ex:
                            print "ERROR occurred!!!", ex
                    if 'rpc_reply' in locals():
                        filename = snap_files + '_' + rpc + '.' + 'xml'
                        output_file = os.path.join(path, 'snapshots', filename)
                        with open(output_file, 'w') as f:
                            f.write(etree.tostring(rpc_reply))

                        # SQLiteChanges

                        if db['store_in_sqlite'] is True:
                            a = snap_files.split('_')
                            host = a[0]
                            a.pop(0)
                            a = '_'.join(a)
                            sqlite_jsnap = JsnapSqlite(host, db['db_name'])
                            db_dict2 = dict()
                            db_dict2['username'] = username
                            db_dict2['cli_command'] = rpc
                            db_dict2['snap_name'] = a
                            db_dict2['filename'] = filename
                            db_dict2['xml'] = etree.tostring(rpc_reply)
                            sqlite_jsnap.insert_data(db_dict2)
                    ###
            else:
                print "Test case:  %s  not defined !!!!" % t
