"""Lib for generating classes etc"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import mysql.connector

CONFIG = ConfigParser.SafeConfigParser()

def get_db_connection(section):
    """Get DB Connection """
    CONFIG.read('config.cfg')
    dbconfig = {}
    dbconfig['user'] = CONFIG.get(section, 'user')
    dbconfig['password'] = CONFIG.get(section, 'password')
    dbconfig['host'] = CONFIG.get(section, 'host')
    dbconfig['database'] = CONFIG.get(section, 'database')
    cnx = mysql.connector.connect(
        user=dbconfig['user']
        , password=dbconfig['password']
        , host=dbconfig['host']
        , database=dbconfig['database']
        , charset='utf8'
        , auth_plugin='mysql_native_password')
    return cnx

def get_cols_for_tbl(tablename, section):
    """Get Column Information from DB metadata """
    cols = []
    cnx = get_db_connection(section)
    cursor = cnx.cursor()
    stmt = "SHOW COLUMNS FROM `%s`" % (tablename)
    cursor.execute(stmt)
    for row in cursor:
        cols.append({'name':row[0], 'type':row[1], 'default':row[4]})
    cursor.close()
    cnx.close()
    return cols
