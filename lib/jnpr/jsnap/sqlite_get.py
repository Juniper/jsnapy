import sqlite3
import sys
import os


class SqliteExtractXml:

    def __init__(self, db_name):
        path = os.getcwd()
        self.db_filename = os.path.join(path, 'snapshots', db_name)
        if not os.path.isfile(self.db_filename):
            print "Database %s does not exist." % db_name
            sys.exit(1)
    def get_xml_using_snapname(self, hostname, command_name, snap_name):
        table_name = 'table_' + hostname.replace('.', '__')
        with sqlite3.connect(self.db_filename) as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM sqlite_master WHERE name = :name and type='table'; ", {'name': table_name})
            if not cursor.fetchall():
                print"No previous snapshots exists for host %s" % hostname
                sys.exit(1)
            cursor.execute("SELECT MIN(id), data_format, data FROM %s WHERE snap_name = :snap AND cli_command = :cli" % table_name,
                           {'snap': snap_name, 'cli': command_name})
            row = cursor.fetchone()
            if not row:
                print"No previous snapshots exists with name = %s for command =" % snap_name, command_name.replace('_', ' ')
                sys.exit(1)
            else:
                idd, data_format, data = row
                if data is None:
                    print"No previous snapshots exists with name = %s for command =" % snap_name, command_name.replace('_', ' ')
                    sys.exit(1)
                else:
                    return str(data), data_format

    def get_xml_using_snap_id(self, hostname, command_name, snap_id):
        table_name = 'table_' + hostname.replace('.', '__')
        with sqlite3.connect(self.db_filename) as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM sqlite_master WHERE name = :name and type='table'; ", {'name': table_name})
            if not cursor.fetchall():
                print"No previous snapshots exists for host %s" % hostname
                sys.exit(1)
            cursor.execute("SELECT id, data_format, data FROM %s WHERE id = :id AND cli_command = :cli" % table_name,
                           {'id': snap_id, 'cli': command_name})
            row = cursor.fetchone()
            if not row:
                print"No previous snapshots exists with id = %s for command = " % snap_id, command_name.replace('_', ' ')
                sys.exit(1)
            else:
                idd, data_format, data = row
                return str(data), data_format
