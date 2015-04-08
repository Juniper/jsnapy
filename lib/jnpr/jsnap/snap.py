from lxml import etree
import os
from jnpr.jsnap.sqlite_store import JsnapSqlite
import sys


class Parse:

    def _write_file(self, rpc_reply, format, output_file):
        if isinstance(rpc_reply, bool) and format == "text":
            print "ERROR!! requested node is not present"
        else:
            err = rpc_reply.xpath("//rpc-error")
            if len(err):
                print "\nERROR:"
                for err_node in err:
                    print err_node.findtext('.//error-message')
            else:
                with open(output_file, 'w') as f:
                    f.write(etree.tostring(rpc_reply))

    def _check_reply(self, rpc_reply, format):
        if isinstance(rpc_reply, bool) and format == "text":
            print "ERROR!! requested node is not present"
        else:
            err = rpc_reply.xpath("//rpc-error")
            if len(err):
                print "\nERROR:"
                for err_node in err:
                    print err_node.findtext('.//error-message')
            else:
                return etree.tostring(rpc_reply)
        return(False)

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
        if 'tests_include' in test_file:
            for t in test_file.get('tests_include'):
                self.test_included.append(t)
                if t in test_file:
                    if test_file.get(t) is not None and (
                            'command' in test_file[t][0]):
                        command = test_file[t][0].get(
                            'command',
                            "unknown command")
                        cmd_format = test_file[t][0].get('format', 'xml')

                        self.command_list.append(command)
                        name = '_'.join(command.split())
                        try:
                            print "\nTaking snapshot for %s ................" % command
                            rpc_reply_command = dev.rpc.cli(
                                command,
                                format=cmd_format)
                            # print "*********",
                            # etree.tostring(rpc_reply_command)
                        except Exception:
                            print "ERROR occurred ----!!!", sys.exc_info()[0]
                            print "\n**********Complete error message***********\n", sys.exc_info()
                        else:
                            filename = snap_files + '_' + \
                                name + '.' + cmd_format
                            output_file = os.path.join(
                                path,
                                'snapshots',
                                filename)
                            self._write_file(
                                rpc_reply_command,
                                cmd_format,
                                output_file)

                            # SQLiteChanges
                            if db['store_in_sqlite'] is True and self._check_reply(
                                    rpc_reply_command, cmd_format):
                                snap_name = snap_files.split('_')
                                host = snap_name[0]
                                snap_name.pop(0)
                                snap_name = '_'.join(snap_name)
                                sqlite_jsnap = JsnapSqlite(host, db['db_name'])
                                db_dict = dict()
                                db_dict['username'] = username
                                db_dict['cli_command'] = name
                                db_dict['snap_name'] = snap_name
                                db_dict['filename'] = filename
                                db_dict['format'] = cmd_format
                                db_dict['data'] = self._check_reply(
                                    rpc_reply_command,
                                    cmd_format)
                                sqlite_jsnap.insert_data(db_dict)
                            ###

                    elif test_file.get(t) is not None and 'rpc' in test_file[t][0]:
                        rpc = test_file[t][0].get('rpc', "unknown rpc")
                        self.rpc_list.append(rpc)
                        reply_format = test_file[t][0].get('format', 'xml')
                        if len(test_file[t]) >= 2 and 'args' in test_file[
                                t][1]:
                            kwargs = {
                                k.replace(
                                    '-',
                                    '_'): v for k,
                                v in test_file[t][1]['args'].items()}
                            if 'filter_xml' in kwargs:
                                from lxml.builder import E
                                filter_data = None
                                for tag in kwargs[
                                        'filter_xml'].split('/')[::-1]:
                                    filter_data = E(tag) if filter_data is None else E(
                                        tag,
                                        filter_data)
                                    kwargs['filter_xml'] = filter_data
                                if rpc == 'get-config':
                                    print "\nTaking snapshot of %s......." % rpc
                                    rpc_reply = getattr(
                                        dev.rpc,
                                        rpc.replace(
                                            '-',
                                            '_'))(options={'format': reply_format},
                                                  **kwargs)
                                else:
                                    print "ERROR!!, filtering rpc works only for 'get-config' rpc"

                            else:
                                try:
                                    print "\nTaking snapshot of %s......." % rpc
                                    rpc_reply = getattr(
                                        dev.rpc,
                                        rpc.replace(
                                            '-',
                                            '_'))({'format': reply_format},
                                                  **kwargs)
                                except Exception:
                                    print "ERROR occurred ----!!!", sys.exc_info()[0]
                                    print "\n**********Complete error message***********\n", sys.exc_info()
                        else:
                            try:
                                print "\nTaking snapshot of %s............" % rpc
                                if rpc == 'get-config':
                                    rpc_reply = getattr(
                                        dev.rpc,
                                        rpc.replace(
                                            '-',
                                            '_'))(options={'format': reply_format})
                                else:
                                    rpc_reply = getattr(
                                        dev.rpc,
                                        rpc.replace(
                                            '-',
                                            '_'))({'format': reply_format})
                            except Exception:
                                print "ERROR occurred ----!!!", sys.exc_info()[0]
                                print "\n**********Complete error message***********\n", sys.exc_info()

                        if 'rpc_reply' in locals():
                            filename = snap_files + '_' + \
                                rpc + '.' + reply_format
                            output_file = os.path.join(
                                path,
                                'snapshots',
                                filename)
                            self._write_file(
                                rpc_reply,
                                reply_format,
                                output_file)

                            # SQLiteChanges
                            if db['store_in_sqlite'] is True and self._check_reply(
                                    rpc_reply, reply_format):
                                snap_name = snap_files.split('_')
                                host = snap_name[0]
                                snap_name.pop(0)
                                snap_name = '_'.join(snap_name)
                                sqlite_jsnap = JsnapSqlite(host, db['db_name'])
                                db_dict2 = dict()
                                db_dict2['username'] = username
                                db_dict2['cli_command'] = rpc
                                db_dict2['snap_name'] = snap_name
                                db_dict2['filename'] = filename
                                db_dict2['format'] = reply_format
                                db_dict2['data'] = self._check_reply(
                                    rpc_reply,
                                    reply_format)
                                sqlite_jsnap.insert_data(db_dict2)
                        ###
                    else:
                        print "ERROR!!! Test case: '%s' not defined properly" % t
                else:
                    print "ERROR!!! Test case: '%s' not defined !!!!" % t
        else:
            print "\nERROR!! None of the test cases included"
