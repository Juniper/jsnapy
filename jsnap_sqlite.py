
import sqlite3
import os

class JsnapSqlite:

    def __init__(self, host, db_name):
        host = host.replace('.', '_')
        self.table_name = "table_" + host
        # Creating Schema
        path = os.getcwd()
        self.db_filename = os.path.join(path, 'snapshots', db_name)
        with sqlite3.connect(self.db_filename) as conn:
            # print 'Creating schema if not exists'
            sqlstr = """create table if not exists %s (
                key          integer not null primary key autoincrement,
                id           integer not null,
                filename     text,
                username	 text,
                cli_command  text,
                snap_name    text,
                xml_data     text
            );""" % self.table_name
            conn.execute(sqlstr)

    # Inserting Data
    def insert_data(self, xml_string, user, command_name, snap_name,filename):
        with sqlite3.connect(self.db_filename) as con:
            # print 'Inserting data'
            con.execute("""update %s set id = id + 1 where cli_command = :cli""" % self.table_name, {'cli': command_name})
            con.execute("""delete from %s where id>49 AND cli_command = :cli""" % self.table_name, {'cli': command_name})
            con.execute("""delete from %s where snap_name = :snap AND cli_command = :cli""" % self.table_name,
                        {'snap': snap_name, 'cli': command_name})
            con.execute("""insert into %s (id, filename, username, cli_command, snap_name, xml_data) values (0, :file,
                        :user, :cli, :snap, :xml)""" % self.table_name, {'file': filename, 'user': user,
                        'cli': command_name, 'snap': snap_name, 'xml': xml_string})
            con.commit()

    # Verify database content
    def print_result(self):

        with sqlite3.connect(self.db_filename) as conn:

            cursor = conn.cursor()
            cursor.execute("""
            select * from %s
            """ % self.table_name)

            for row in cursor.fetchall():
                key, id, filename, user, cli, snap, xml = row
                print id
                print user
                print cli
                print snap
                print len(xml)
