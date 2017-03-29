# -*- coding: utf-8 -*-

import urlparse
import psycopg2
import sys
from datetime import timedelta
from psycopg2.extras import DictCursor


def column_exists(cursor, table, column):
    query = """SELECT EXISTS (SELECT 1 
    FROM information_schema.columns 
    WHERE table_name='%s' and column_name='%s')""" % (table, column)
    cursor.execute(query)
    exists = cursor.fetchone()
    if exists:
        return exists[0]
    return False


def iterate_table(cursor, table):
    query = """SELECT * FROM %s""" % table
    cursor.execute(query)
    return cursor


def describe_table(cursor, table):
    query = """SELECT *
    FROM information_schema.columns 
    WHERE table_name='%s'""" % table
    cursor.execute(query)
    return cursor.fetchall()


def connection_info(uri):
    result = urlparse.urlparse(uri)
    return (result.username,
            result.password,
            result.path[1:],
            result.hostname)


if __name__ == "__main__":
    dsn = sys.argv[1]
    username, password, database, hostname = connection_info(dsn)
    conn = psycopg2.connect(
        database = database,
        user = username,
        password = password,
        host = hostname)
    cursor = conn.cursor()

    enddate = bool(column_exists(cursor, 'sessions', 'enddate'))
    if not enddate:
        print "Adding missing column 'enddate'"
        cursor.execute(
            'ALTER TABLE %s ADD COLUMN %s DATE' % ('sessions', 'enddate'))
        conn.commit()

    duration = column_exists(cursor, 'sessions', 'duration')
    if enddate and not duration:
        raise RuntimeError('Migration seems to have already happen')

    elif duration:
        dcursor = conn.cursor(cursor_factory=DictCursor)
        for row in iterate_table(dcursor, 'sessions'):
            if row['enddate'] is None:
               enddate = row['startdate'] + timedelta(days=row['duration'])
               print "Adding missing enddate to session %s" % row['id']
               ecursor = conn.cursor()
               ecursor.execute(
                   "UPDATE %s SET %s='%s' WHERE id='%s'" %
                   ('sessions', 'enddate', str(enddate), row['id']))
               conn.commit()

        ecursor = conn.cursor()
        ecursor.execute("ALTER TABLE sessions DROP COLUMN IF EXISTS duration")
        conn.commit()
