# -*- coding: utf-8 -*-

import urlparse
import psycopg2
import sys
from psycopg2 import sql


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

    order = bool(column_exists(cursor, 'criterias_courses', 'order'))

    if not order:
        print "Adding missing column 'order'"
        cursor.execute(
            sql.SQL("ALTER TABLE criterias_courses ADD COLUMN {} Integer").format(
            sql.Identifier('order')))
        conn.commit()
    else:
        print "Already migrated"
