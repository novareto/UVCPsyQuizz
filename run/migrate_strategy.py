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

    strategy = bool(column_exists(cursor, 'sessions', 'strategy'))

    if not strategy:
        print "Adding missing column 'strategy'"
        cursor.execute(
            'ALTER TABLE public.%s ADD COLUMN %s character varying(20)' %
            ('sessions', 'strategy'))
        conn.commit()

        print "Setting default for 'strategy'"
        cursor.execute(
            "UPDATE %s SET %s = '%s' where id > 0" % (
                ('sessions', 'strategy', 'free')))
        conn.commit()

    else:
        print "Already migrated"
