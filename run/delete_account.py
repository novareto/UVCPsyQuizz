# -*- coding: utf-8 -*-

import uuid
import hashlib
import urlparse
import psycopg2
import sys


def delete_account(conn, email):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE email=%s;', [email])
    conn.commit()


if __name__ == "__main__":
    dsn = sys.argv[1]
    email = sys.argv[2]
    username, password, database, hostname = connection_info(dsn)
    conn = psycopg2.connect(
        database = database,
        user = username,
        password = password,
        host = hostname)
    delete_account(conn, email)
