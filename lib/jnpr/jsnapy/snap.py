#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import re
import sys
import logging
import colorama
from lxml import etree
from jnpr.jsnapy import get_path
from jnpr.junos.exception import RpcError
from jnpr.jsnapy.sqlite_store import JsnapSqlite
import lxml


class Parser:

    def __init__(self):
        self.logger_snap = logging.getLogger(__name__)
        self.log_detail = {'hostname': None}
        self.reply = {}
        self.command_list = []
        self.rpc_list = []
        self.test_included = []

    def _write_file(self, rpc_reply, format, output_file):
        """
        Writing rpc reply in snap file
        :param rpc_reply: RPC reply
        :param format: xml/text
        :param output_file: name of file
        """
        ### pyEz returns true if there is no output of given command ###
        ### Ex. show configuration security certificates returns nothing if its not set


        if rpc_reply is True :
            with open(output_file, 'w') as f:
                f.write("")
            self.logger_snap.info(
                colorama.Fore.BLUE +
                "\nOutput of requested Command/RPC is empty", extra=self.log_detail)
        else:
            with open(output_file, 'w') as f:
                f.write(etree.tostring(rpc_reply))

    def _write_warning(
            self, reply, db, snap_file, hostname, cmd_name, cmd_format, output_file):
        with open(snap_file, 'w') as f:
            f.write(reply)
        if db['store_in_sqlite'] is True:
            self.store_in_sqlite(
                db,
                hostname,
                cmd_name,
                cmd_format,
                reply,
                output_file,
                warning=True)

    def _check_reply(self, rpc_reply, format):
        """
        Check rpc reply for errors
        :param rpc_reply: RPC reply
        :param format: xml/ text
        :return: return false if reply contains error ow return rpc reply
        """
        if rpc_reply is True :
            self.logger_snap.info(
                colorama.Fore.BLUE +
                "\nOutput of requested Command/RPC is empty", extra=self.log_detail)
            return ""
        else:
             return etree.tostring(rpc_reply)


    def generate_snap_file(self, output_file, hostname, name, cmd_format):
        """
        This will generate snapshot file name
        :param output_file: either complete file or file tag
        :param name: command or RPC
        :param cmd_format: xml/text
        :return: return output file
        """
        name = name.split('|')[0].strip()
        cmd_rpc = re.sub('/|\*|\.|-|\|', '_', name)
        if os.path.isfile(output_file):
            return output_file
        else:
            filename = hostname + '_' + output_file + \
                '_' + cmd_rpc + '.' + cmd_format
            output_file = os.path.join(
                get_path(
                    'DEFAULT',
                    'snapshot_path'),
                filename)
            return output_file

    def store_in_sqlite(
            self, db, hostname, cmd_rpc_name, reply_format, rpc_reply, snap_name, warning=False):
        """
        Store reply in database
        :param db: database name
        :param hostname: hostname
        :param cmd_rpc_name: Command/RPC
        :param reply_format: xml / text
        :param rpc_reply: RPC reply
        :param snap_name: snap filename
        """
        sqlite_jsnap = JsnapSqlite(hostname, db['db_name'])
        db_dict = dict()
        db_dict['cli_command'] = cmd_rpc_name
        db_dict['snap_name'] = snap_name
        db_dict['filename'] = hostname + '_' + snap_name + \
            '_' + cmd_rpc_name + '.' + reply_format
        db_dict['format'] = reply_format
        if warning is False:
            db_dict['data'] = self._check_reply(rpc_reply, reply_format)
        else:
            db_dict['data'] = rpc_reply
        sqlite_jsnap.insert_data(db_dict)

    def run_cmd(self, test_file, t, formats, dev, output_file, hostname, db):
        """
        This function takes snapshot for given command and write it in
        snapshot file or database
        """
        command = test_file[t][0].get('command', "unknown command")
        cmd_format = test_file[t][0].get('format', 'xml')
        cmd_format = cmd_format if cmd_format in formats else 'xml'
        self.command_list.append(command)
        cmd_name = command.split('|')[0].strip()
        cmd_name = '_'.join(cmd_name.split())
        self.logger_snap.debug(colorama.Fore.BLUE +
                               "Tests Included: %s " %t,
                               extra=self.log_detail)
        self.logger_snap.info(
            colorama.Fore.BLUE +
            "Taking snapshot of COMMAND: %s " %
            command,
            extra=self.log_detail)
        try:
            # self.logger_snap.info(
            #     colorama.Fore.BLUE +
            #     "Taking snapshot of COMMAND: %s " %
            #     command,
            #     extra=self.log_detail)
            ##### for commands containing "| display xml" only text format works in PyEz
            if re.search('\|\s+display\s+xml',command):
                rpc_reply_command = dev.rpc.cli(command, format='text')
            else:
                rpc_reply_command = dev.rpc.cli(command, format=cmd_format)
            self.reply[command] = rpc_reply_command

        except RpcError as err:
            snap_file = self.generate_snap_file(
                output_file,
                hostname,
                cmd_name,
                cmd_format)
            self._write_warning(
                etree.tostring(
                    err.rsp),
                db,
                snap_file,
                hostname,
                cmd_name,
                cmd_format,
                output_file)
            self.logger_snap.error(colorama.Fore.RED +
                                   "ERROR occurred %s" %
                                   str(sys.exc_info()[0]), extra=self.log_detail)
            self.logger_snap.error(colorama.Fore.RED +
                                   "\n**********Complete error message***********\n %s" %
                                   str(sys.exc_info()), extra=self.log_detail)
            return
        except Exception:
            self.logger_snap.error(colorama.Fore.RED +
                                   "ERROR occurred %s" %
                                   str(sys.exc_info()[0]), extra=self.log_detail)
            self.logger_snap.error(colorama.Fore.RED +
                                   "\n**********Complete error message***********\n %s" %
                                   str(sys.exc_info()), extra=self.log_detail)
            #raise Exception("Error in command")
            # sys.exc_clear()
            return
        else:
            snap_file = self.generate_snap_file(
                output_file,
                hostname,
                cmd_name,
                cmd_format)
            self._write_file(rpc_reply_command, cmd_format, snap_file)
            if db['store_in_sqlite'] is True:
                self.store_in_sqlite(
                    db,
                    hostname,
                    cmd_name,
                    cmd_format,
                    rpc_reply_command,
                    output_file)


    def run_rpc(self, test_file, t, formats, dev, output_file, hostname, db):
        """
        This function takes snapshot for given RPC and write it in
        snapshot file or database
        """
        rpc = test_file[t][0].get('rpc', "unknown rpc")
        self.rpc_list.append(rpc)
        reply_format = test_file[t][0].get('format', 'xml')
        reply_format = reply_format if reply_format in formats else 'xml'
        self.logger_snap.debug(colorama.Fore.BLUE +
                               "Tests Included : %s " %t,
                               extra=self.log_detail)
        self.logger_snap.info(colorama.Fore.BLUE +
                              "Taking snapshot of RPC: %s" %
                              rpc,
                              extra=self.log_detail)
        if len(test_file[t]) >= 2 and ('args' in test_file[t][1] or
                                       'kwargs' in test_file[t][1]):
            args_key = 'args' if 'args' in test_file[t][1] else 'kwargs'
            kwargs = {
                k.replace(
                    '-',
                    '_'): v for k,
                v in test_file[t][1][args_key].items()}
            if 'filter_xml' in kwargs:
                from lxml.builder import E
                filter_data = None
                for tag in kwargs['filter_xml'].split('/')[::-1]:
                    filter_data = E(tag) if filter_data is None else E(
                        tag,
                        filter_data)
                kwargs['filter_xml'] = filter_data
                if rpc == 'get-config':
                    # self.logger_snap.info(
                    #     colorama.Fore.BLUE +
                    #     "Taking snapshot of RPC: %s" %
                    #     rpc,
                    #     extra=self.log_detail)
                    rpc_reply = getattr(
                        dev.rpc,
                        rpc.replace(
                            '-',
                            '_'))(
                        options={
                            'format': reply_format},
                        **kwargs)
                else:
                    self.logger_snap.error(
                        colorama.Fore.RED +
                        "ERROR!!, filtering rpc works only for 'get-config' rpc")
            else:
                try:
                    # self.logger_snap.info(
                    #     colorama.Fore.BLUE +
                    #     "Taking snapshot of %s......." %
                    #     rpc,
                    #     extra=self.log_detail)
                    rpc_reply = getattr(
                        dev.rpc, rpc.replace('-', '_'))({'format': reply_format}, **kwargs)
                except RpcError as err:
                    snap_file = self.generate_snap_file(
                        output_file,
                        hostname,
                        rpc,
                        reply_format)
                    self._write_warning(
                        etree.tostring(
                            err.rsp),
                        db,
                        snap_file,
                        hostname,
                        rpc,
                        reply_format,
                        output_file)
                    self.logger_snap.error(colorama.Fore.RED +
                                           "ERROR occurred:\n %s" %
                                           str(sys.exc_info()[0]), extra=self.log_detail)
                    self.logger_snap.error(colorama.Fore.RED +
                                           "\n**********Complete error message***********\n%s" %
                                           str(sys.exc_info()), extra=self.log_detail)
                    return
                except Exception:
                    self.logger_snap.error(colorama.Fore.RED +
                                           "ERROR occurred:\n %s" %
                                           str(sys.exc_info()[0]), extra=self.log_detail)
                    self.logger_snap.error(colorama.Fore.RED +
                                           "\n**********Complete error message***********\n%s" %
                                           str(sys.exc_info()), extra=self.log_detail)
                    return
        else:
            try:
                # self.logger_snap.info(
                #     colorama.Fore.BLUE +
                #     "Taking snapshot of %s............" %
                #     rpc,
                #     extra=self.log_detail)
                if rpc == 'get-config':
                    rpc_reply = getattr(
                        dev.rpc,
                        rpc.replace(
                            '-',
                            '_'))(
                        options={
                            'format': reply_format})
                else:
                    rpc_reply = getattr(
                        dev.rpc, rpc.replace('-', '_'))({'format': reply_format})
            except RpcError as err:
                snap_file = self.generate_snap_file(
                    output_file,
                    hostname,
                    rpc,
                    reply_format)
                self._write_warning(
                    etree.tostring(
                        err.rsp),
                    db,
                    snap_file,
                    hostname,
                    rpc,
                    reply_format,
                    output_file)
                self.logger_snap.error(colorama.Fore.RED +
                                       "ERROR occurred: \n%s" %
                                       str(sys.exc_info()[0]), extra=self.log_detail)
                self.logger_snap.error(colorama.Fore.RED +
                                       "\n**********Complete error message***********\n%s" %
                                       str(sys.exc_info()), extra=self.log_detail)
                return
            except Exception:
                self.logger_snap.error(colorama.Fore.RED +
                                       "ERROR occurred: \n%s" %
                                       str(sys.exc_info()[0]), extra=self.log_detail)
                self.logger_snap.error(colorama.Fore.RED +
                                       "\n**********Complete error message***********\n%s" %
                                       str(sys.exc_info()), extra=self.log_detail)
                return

        if 'rpc_reply' in locals():
            snap_file = self.generate_snap_file(
                output_file,
                hostname,
                rpc,
                reply_format)
            self._write_file(rpc_reply, reply_format, snap_file)
            self.reply[rpc] = rpc_reply

        if db['store_in_sqlite'] is True:
            self.store_in_sqlite(
                db,
                hostname,
                rpc,
                reply_format,
                rpc_reply,
                output_file)

    def generate_reply(self, test_file, dev, output_file, hostname, db):
        """
        Analyse test file and call respective functions to generate rpc reply
        for commands and RPC in test file.
        """
        test_included = []
        formats = ['xml', 'text']
        self.log_detail['hostname'] = hostname

        if 'tests_include' in test_file:
            test_included = test_file.get('tests_include')
        else:
            for t in test_file:
                test_included.append(t)

        # adding test_included into global list
        self.test_included.extend(test_included)

        for t in test_included:
            if t in test_file:
                if test_file.get(t) is not None and (
                        'command' in test_file[t][0]):
                    #command = test_file[t][0].get('command',"unknown command")
                    self.run_cmd(
                        test_file,
                        t,
                        formats,
                        dev,
                        output_file,
                        hostname,
                        db)
                elif test_file.get(t) is not None and 'rpc' in test_file[t][0]:
                    self.run_rpc(
                        test_file,
                        t,
                        formats,
                        dev,
                        output_file,
                        hostname,
                        db)
                else:
                    self.logger_snap.error(
                        colorama.Fore.RED +
                        "ERROR!!! Test case: '%s' not defined properly" % t, extra=self.log_detail)
            else:
                self.logger_snap.error(
                    colorama.Fore.RED +
                    "ERROR!!! Test case: '%s' not defined !!!!" % t, extra=self.log_detail)
        return self
