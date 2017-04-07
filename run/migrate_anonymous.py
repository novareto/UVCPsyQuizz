# -*- coding: utf-8 -*-

import urlparse
import psycopg2
import sys


def column_exists(cursor, table, column):
    query = """SELECT EXISTS (SELECT 1 
    FROM information_schema.columns 
    WHERE table_name='%s' and column_name='%s')""" % (table, column)
    cursor.execute(query)
    exists = cursor.fetchone()
    if exists:
        return exists[0]
    return False


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

    anon = bool(column_exists(cursor, 'students', 'anonymous'))

    if not anon:
        print "Adding missing column 'anonymous'"
        cursor.execute(
            'ALTER TABLE %s ADD COLUMN %s Boolean DEFAULT FALSE' %
            ('students', 'anonymous'))
        conn.commit()
    else:
        print "Already migrated"
