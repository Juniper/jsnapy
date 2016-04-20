#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#
# License: Apache 2.0
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# * Neither the name of the Juniper Networks nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Juniper Networks, Inc. ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Juniper Networks, Inc. BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sqlite3
import logging
from jnpr.jsnapy import get_path


class JsnapSqlite:

    def __init__(self, host, db_name):
        self.logger_storesqlite = logging.getLogger(__name__)
        host = host.replace('.', '__')
        self.table_name = "table_" + host
        # Creating Schema
        self.db_filename = os.path.join(
            get_path(
                'DEFAULT',
                'snapshot_path'),
            db_name)
        try:
            with sqlite3.connect(self.db_filename) as conn:
                # Creating schema if it does not exists
                sqlstr = """create table if not exists %s (
                    id           integer not null,
                    filename     text,
                    cli_command  text,
                    snap_name    text,
                    data_format  text,
                    data     text
                );""" % self.table_name
                conn.execute(sqlstr)
        except Exception as ex:
            self.logger_storesqlite.error(
                "\nERROR occurred in database:    %s" %
                str(ex))

    def insert_data(self, db):
        """
        Function to Insert Data in database
        :param db: database name
        """
        with sqlite3.connect(self.db_filename) as con:
            con.execute("""update %s set id = id + 1 where cli_command = :cli""" % self.table_name,
                        {'cli': db['cli_command']})
            con.execute("""delete from %s where id>49 AND cli_command = :cli""" % self.table_name,
                        {'cli': db['cli_command']})
            con.execute("""insert into %s (id, filename, cli_command, snap_name, data_format, data) values (0, :file,
                         :cli, :snap, :format, :xml)""" % self.table_name, {'file': db['filename'],
                                                                            'cli': db['cli_command'], 'snap': db['snap_name'],
                                                                            'format': db['format'], 'xml': db['data']})
            con.commit()
