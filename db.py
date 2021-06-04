import mysql.connector
from flask import g

my_host = 'localhost'
my_database = 'cefim_datawarehouse'
my_user = 'root'
my_password = 'root'


def get_conn():
    """conn to database"""
    if 'conn' not in g:
        g.conn = mysql.connector.connect(my_host, my_database, my_user, my_password)
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


