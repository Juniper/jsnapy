__author__ = 'palash'

import sqlite3
import sys
import os

class SqliteExtractXml:

    def __init__(self, db_name):
        path = os.getcwd()
        self.db_filename = os.path.join(path, 'snapshots', db_name)


    def get_xml_using_snapname(self, hostname, command_name, snap_name):
        table_name = 'table_' + hostname.replace('.','_')
        with sqlite3.connect(self.db_filename) as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM sqlite_master WHERE name = :name and type='table'; ", {'name': table_name})
            if not cursor.fetchall():
                print"No previous snapshots exists for host %s" % hostname
                sys.exit(1)
            cursor.execute("SELECT id,xml_data FROM %s WHERE snap_name = :snap AND cli_command = :cli" % table_name, {'snap': snap_name, 'cli': command_name})
            row = cursor.fetchone()
            if not row:
                print"No previous snapshots exists with name = %s for command =  " % snap_name , command_name
                sys.exit(1)
            else:
                idd, xml_string = row
                return str(xml_string)



    def get_xml_using_snap_id(self, hostname, command_name, snap_id):
        table_name = 'table_' + hostname.replace('.','_')
        with sqlite3.connect(self.db_filename) as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM sqlite_master WHERE name = :name and type='table'; ", {'name': table_name})
            if not cursor.fetchall():
                print"No previous snapshots exists for host %s" % hostname
                sys.exit(1)
            cursor.execute("SELECT id, xml_data FROM %s WHERE id = :id AND cli_command = :cli" % table_name, {'id': snap_id, 'cli': command_name})
            row = cursor.fetchone()
            if not row:
                print"No previous snapshots exists with id = %s for command = %s " % snap_id, command_name
                sys.exit(1)
            else:
                idd, xml_string = row
                return str(xml_string)

