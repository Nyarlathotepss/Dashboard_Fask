import mysql.connector
from flask import g


def get_conn():
    """conn to database"""
    if 'conn' not in g:
        my_host = 'localhost'
        my_database = 'cefim'
        my_user = 'root'
        my_password = 'root'
        g.conn = mysql.connector.connect(host=my_host, database=my_database, user=my_user, password=my_password)
    return g.conn


def close_conn(e=None):
    conn = g.pop('conn', None)
    if conn is not None:
         conn.close()


def init_app(app):
    app.teardown_appcontext(close_conn)

def collection(sql, values=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, values)
    row_headers = [x[0] for x in cur.description]
    rows = cur.fetchall()
    cur.close()
    return [dict(zip(row_headers, row)) for row in rows]
