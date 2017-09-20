# -*- coding: utf-8 -*-

import urlparse
import psycopg2
import sys
from datetime import timedelta
from psycopg2.extras import DictCursor


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
    ecursor = conn.cursor()
    ecursor.execute("ALTER TABLE criteria_answers DROP COLUMN IF EXISTS session_id")
    conn.commit()
