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
    fixed_extra_questions = bool(
        column_exists(cursor, 'courses', 'fixed_extra_questions'))

    if not fixed_extra_questions:
        print "Adding missing column 'fixed_extra_questions'"
        cursor.execute(
            'ALTER TABLE %s ADD COLUMN %s TEXT' % (
                'courses', 'fixed_extra_questions'))
        conn.commit()
