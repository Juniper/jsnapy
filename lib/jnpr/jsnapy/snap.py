from lxml import etree
import os
from jnpr.jsnapy.sqlite_store import JsnapSqlite
import sys
import logging
import colorama

class Parse:

    def __init__(self):
        self.logger_snap = logging.getLogger(__name__)
        colorama.init(autoreset=True)

    def _write_file(self, rpc_reply, format, output_file):
        if isinstance(rpc_reply, bool) and format == "text":
            self.logger_snap.error(
                colorama.Fore.RED +
                "ERROR!! requested node is not present")
        else:
            err = rpc_reply.xpath("//rpc-error")
            if len(err):
                self.logger_snap.error(colorama.Fore.RED + "\nERROR:")
                for err_node in err:
                    self.logger_snap.error(
                        err_node.findtext(
                            colorama.Fore.RED +
                            './/error-message'))
            else:
                with open(output_file, 'w') as f:
                    f.write(etree.tostring(rpc_reply))
                    self.logger_snap.debug(
                        colorama.Fore.BLUE +
                        etree.tostring(rpc_reply))

    def _check_reply(self, rpc_reply, format):
        if isinstance(rpc_reply, bool) and format == "text":

            self.logger_snap.error(
                colorama.Fore.RED +
                "ERROR!! requested node is not present")
        else:
            err = rpc_reply.xpath("//rpc-error")
            if len(err):
                self.logger_snap.error(colorama.Fore.RED + "\nERROR:")
                for err_node in err:
                    self.logger_snap.error(
                        err_node.findtext(
                            colorama.Fore.RED +
                            './/error-message'))
            else:
                return etree.tostring(rpc_reply)
        return(False)

    def generate_snap_file(self, output_file, hostname, name, cmd_format):
        if os.path.isfile (output_file):
            return output_file
        else:
            filename = hostname + '_' + output_file + '_' + name + '.' + cmd_format
            output_file = os.path.join('/etc','jsnapy', 'snapshots', filename)
            return output_file

    def store_in_sqlite(self, db, hostname, username, cmd_rpc_name, reply_format, rpc_reply, snap_name):
        sqlite_jsnap = JsnapSqlite(hostname, db['db_name'])
        db_dict = dict()
        db_dict['username'] = username
        db_dict['cli_command'] = cmd_rpc_name
        db_dict['snap_name'] = snap_name
        db_dict['filename'] = snap_name + '_' + cmd_rpc_name + '.' + reply_format
        db_dict['format'] = reply_format
        db_dict['data'] = self._check_reply(rpc_reply, reply_format)
        sqlite_jsnap.insert_data(db_dict)

    def run_cmd(self, test_file, t, formats, dev, output_file, hostname, username, db ):
        command = test_file[t][0].get('command',"unknown command")
        cmd_format = test_file[t][0].get('format', 'xml')
        cmd_format = cmd_format if cmd_format in formats else 'xml'
        self.command_list.append(command)
        cmd_name = '_'.join(command.split())
        try:
            self.logger_snap.info(colorama.Fore.BLUE +"\nTaking snapshot for %s ................" %command)
            rpc_reply_command = dev.rpc.cli(command, format=cmd_format)
        except Exception:
            self.logger_snap.error(colorama.Fore.RED + "ERROR occurred %s" % str(sys.exc_info()[0]))
            self.logger_snap.error(colorama.Fore.RED +"\n**********Complete error message***********\n %s" % str(sys.exc_info()))
        else:
            snap_file = self.generate_snap_file(output_file, hostname, cmd_name, cmd_format)
            self._write_file(rpc_reply_command, cmd_format, snap_file)
            if db['store_in_sqlite'] is True and self._check_reply(rpc_reply_command, cmd_format):
                self.store_in_sqlite(db, hostname, username, cmd_name, cmd_format, rpc_reply_command, output_file)


    def run_rpc(self, test_file, t, formats, dev, output_file, hostname, username, db):
        rpc = test_file[t][0].get('rpc', "unknown rpc")
        self.rpc_list.append(rpc)
        reply_format = test_file[t][0].get('format', 'xml')
        reply_format = reply_format if reply_format in formats else 'xml'
        if len(test_file[t]) >= 2 and 'args' in test_file[t][1]:
            kwargs = {k.replace('-','_'): v for k,v in test_file[t][1]['args'].items()}
            if 'filter_xml' in kwargs:
                from lxml.builder import E
                filter_data = None
                for tag in kwargs['filter_xml'].split('/')[::-1]:
                    filter_data = E(tag) if filter_data is None else E(tag,filter_data)
                    kwargs['filter_xml'] = filter_data
                    if rpc == 'get-config':
                        self.logger_snap.info(colorama.Fore.BLUE + "\nTaking snapshot of %s......." %rpc)
                        rpc_reply = getattr(dev.rpc, rpc.replace('-','_'))(options={'format': reply_format},**kwargs)
                    else:
                        self.logger_snap.error(colorama.Fore.RED +"ERROR!!, filtering rpc works only for 'get-config' rpc")
            else:
                try:
                    self.logger_snap.info(colorama.Fore.BLUE + "\nTaking snapshot of %s......." %rpc)
                    rpc_reply = getattr(dev.rpc, rpc.replace('-','_'))({'format': reply_format},**kwargs)
                except Exception:
                    self.logger_snap.error(colorama.Fore.RED +"ERROR occurred:\n %s" % str(sys.exc_info()[0]))
                    self.logger_snap.error(colorama.Fore.RED +"\n**********Complete error message***********\n%s" % str(sys.exc_info()))
        else:
            try:
                self.logger_snap.info(colorama.Fore.BLUE +"\nTaking snapshot of %s............" % rpc)
                if rpc == 'get-config':
                    rpc_reply = getattr(dev.rpc, rpc.replace('-','_'))(options={'format': reply_format})
                else:
                    rpc_reply = getattr(dev.rpc, rpc.replace('-','_'))({'format': reply_format})
            except Exception:
                self.logger_snap.error(colorama.Fore.RED + "ERROR occurred: \n%s" % str(sys.exc_info()[0]))
                self.logger_snap.error(colorama.Fore.RED +"\n**********Complete error message***********\n%s" % str(sys.exc_info()))

        if 'rpc_reply' in locals():
            snap_file = self.generate_snap_file(output_file, hostname, rpc, reply_format)
            self._write_file(rpc_reply, reply_format, snap_file)

        if db['store_in_sqlite'] is True and self._check_reply(rpc_reply, reply_format):
            self.store_in_sqlite(self, db, hostname, username, rpc, reply_format, rpc_reply, output_file)

    # generate snap files for devices based on given commands and rpc
    def generate_reply(self, test_file, dev, output_file, hostname, db, username):
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
        formats = ['xml', 'text']
        if 'tests_include' in test_file:
            for t in test_file.get('tests_include'):
                self.test_included.append(t)
                if t in test_file:
                    if test_file.get(t) is not None and ('command' in test_file[t][0]):
                        command = test_file[t][0].get('command',"unknown command")
                        cmd_format = test_file[t][0].get('format', 'xml')
                        cmd_format = cmd_format if cmd_format in formats else 'xml'
                        self.command_list.append(command)
                        cmd_name = '_'.join(command.split())
                        self.run_cmd(test_file, t, formats, dev, output_file, hostname, username, db)
                        test_file, t, formats, dev, output_file, hostname, username, db
                    elif test_file.get(t) is not None and 'rpc' in test_file[t][0]:
                        self.run_rpc(test_file, t, formats, dev, output_file, hostname, username, db)
                    else:
                        self.logger_snap.error(
                            colorama.Fore.RED +
                            "ERROR!!! Test case: '%s' not defined properly" % t)
                else:
                    self.logger_snap.error(
                        colorama.Fore.RED +
                        "ERROR!!! Test case: '%s' not defined !!!!" % t)
        else:
            self.logger_snap.error(
                colorama.Fore.RED +
                "\nERROR!! None of the test cases included")
