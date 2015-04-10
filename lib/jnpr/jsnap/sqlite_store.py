import sqlite3
import os
import logging


class JsnapSqlite:

    def __init__(self, host, db_name):
        self.logger_storesqlite = logging.getLogger(__name__)
        host = host.replace('.', '__')
        self.table_name = "table_" + host
        # Creating Schema
        path = os.getcwd()
        self.db_filename = os.path.join(path, 'snapshots', db_name)
        with sqlite3.connect(self.db_filename) as conn:
            # print 'Creating schema if not exists'
            sqlstr = """create table if not exists %s (
                id           integer not null,
                filename     text,
                username	 text,
                cli_command  text,
                snap_name    text,
                data_format  text,
                data     text
            );""" % self.table_name
            conn.execute(sqlstr)

    # Inserting Data
    def insert_data(self, db):
        with sqlite3.connect(self.db_filename) as con:
            # print 'Inserting data'
            con.execute("""update %s set id = id + 1 where cli_command = :cli""" % self.table_name,
                        {'cli': db['cli_command']})
            con.execute("""delete from %s where id>49 AND cli_command = :cli""" % self.table_name,
                        {'cli': db['cli_command']})
            con.execute("""insert into %s (id, filename, username, cli_command, snap_name, data_format, data) values (0, :file,
                        :user, :cli, :snap, :format, :xml)""" % self.table_name, {'file': db['filename'], 'user': db['username'],
                                                                                  'cli': db['cli_command'], 'snap': db['snap_name'],
                                                                                  'format': db['format'], 'xml': db['data']})
            con.commit()

    # Verify database content
    def print_result(self):

        with sqlite3.connect(self.db_filename) as conn:

            cursor = conn.cursor()
            cursor.execute("""
            select * from %s
            """ % self.table_name)

            for row in cursor.fetchall():
                idd, filename, user, cli, snap, data_format, xml = row
                print idd
                print user
                print cli
                print snap
                print data_format
                print len(xml)
