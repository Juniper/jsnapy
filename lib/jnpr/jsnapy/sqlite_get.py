import sqlite3
import sys
import os
import logging
import colorama
from jnpr.jsnapy import get_path

class SqliteExtractXml:

    def __init__(self, db_name):
        self.logger_sqlite = logging.getLogger(__name__)
        self.sqlite_logs= {'hostname': None}
        self.db_filename = os.path.join(get_path('DEFAULT', 'snapshot_path'), db_name)
        if not os.path.isfile(self.db_filename):
            self.logger_sqlite.error(
                colorama.Fore.RED +
                "Database %s does not exist." %
                db_name, extra= self.sqlite_logs)
            sys.exit(1)

    def get_xml_using_snapname(self, hostname, command_name, snap_name):
        self.sqlite_logs['hostname']= hostname
        table_name = 'table_' + hostname.replace('.', '__')
        with sqlite3.connect(self.db_filename) as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM sqlite_master WHERE name = :name and type='table'; ", {'name': table_name})
            try:
                cursor.execute("SELECT MIN(id), data_format, data FROM %s WHERE snap_name = :snap AND cli_command = :cli" % table_name,
                           {'snap': snap_name, 'cli': command_name})
                row = cursor.fetchone()
                idd, data_format, data = row
            except Exception as ex:
                self.logger_sqlite.error(colorama.Fore.RED + "ERROR!! Eror message is %s"%ex, extra= self.sqlite_logs)
            else:
                return str(data), data_format

    def get_xml_using_snap_id(self, hostname, command_name, snap_id):
        #print "\n get_xml_using snapid ========"
        self.sqlite_logs['hostname']= hostname
        table_name = 'table_' + hostname.replace('.', '__')
        with sqlite3.connect(self.db_filename) as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM sqlite_master WHERE name = :name and type='table'; ", {'name': table_name})
            try:
                cursor.execute("SELECT id, data_format, data FROM %s WHERE id = :id AND cli_command = :cli" % table_name,
                           {'id': snap_id, 'cli': command_name})
                row = cursor.fetchone()
                idd, data_format, data = row
            except Exception as ex:
                self.logger_sqlite.error(
                    colorama.Fore.RED +
                    "ERROR!! Error message is: %s"%ex, extra= self.sqlite_logs)
                return str(None), None


            else:
                #print "\n 9999999 inside else ========"
                return str(data), data_format
