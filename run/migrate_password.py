# -*- coding: utf-8 -*-

import uuid
import hashlib
import urlparse
import psycopg2
from psycopg2.extras import DictCursor
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


def iterate_table(cursor, table):
    query = """SELECT * FROM %s""" % table
    cursor.execute(query)
    return cursor


def connection_info(uri):
    result = urlparse.urlparse(uri)
    return (result.username,
            result.password,
            result.path[1:],
            result.hostname)


def hash_password(pwd):
    salt = uuid.uuid4().hex
    return salt, hashlib.sha512(pwd + salt).hexdigest()


def create_column(cursor):
    salt = bool(column_exists(cursor, 'accounts', 'salt'))

    if not salt:
        print "Adding missing column 'salt'"
        cursor.execute(
            'ALTER TABLE %s ADD COLUMN %s character varying(40)' %
            ('accounts', 'salt'))
        conn.commit()
    else:
        print "Already migrated"


def migrate_passwords(conn):
    dcursor = conn.cursor(cursor_factory=DictCursor)
    for row in iterate_table(dcursor, 'accounts'):
        salt, hashed = hash_password(row['password'])
        cursor.execute('UPDATE accounts '
                       'SET salt=%s, password=%s '
                       'WHERE email=%s;', (salt, hashed, row['email']))
        conn.commit()


if __name__ == "__main__":
    dsn = sys.argv[1]
    username, password, database, hostname = connection_info(dsn)
    conn = psycopg2.connect(
        database = database,
        user = username,
        password = password,
        host = hostname)
    cursor = conn.cursor()
    create_column(cursor)
    migrate_passwords(conn)
