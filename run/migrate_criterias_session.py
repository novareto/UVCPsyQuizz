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
    return cursor.fetchall()


def get_student(cursor, sid):
    query = """SELECT *
    FROM  students
    WHERE access='%s'""" % sid
    cursor.execute(query)
    return cursor.fetchone()


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
    sessionid = bool(column_exists(cursor, 'criteria_answers', 'session_id'))
    if not sessionid:
        print "Adding missing column 'session_id'"
        cursor.execute(
            'ALTER TABLE %s ADD COLUMN %s INTEGER' % (
                'criteria_answers', 'session_id'))
        conn.commit()

    ccursor = conn.cursor(cursor_factory=DictCursor)
    for row in iterate_table(ccursor, 'criteria_answers'):
        if not row['session_id']:
            student_id, criteria_id = row['student_id'], row['criteria_id']
            scursor = conn.cursor(cursor_factory=DictCursor)
            student = get_student(scursor, student_id)
            session_id = student['session_id']
            if session_id is not None:
                print "Adding session to criteria_answer for %s" % student_id
                ecursor = conn.cursor()
                ecursor.execute(
                    "UPDATE criteria_answers SET session_id='%s' WHERE student_id='%s' AND criteria_id='%s'" % (session_id, student_id,  criteria_id)
                )
            else:
                print "Student %s has no session_id" % student_id

    conn.commit()
