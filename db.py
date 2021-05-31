import mysql.connector
from flask import g


def get_conn():
    if 'conn' not in g:
        g.conn = mysql.connector.connect(host='localhost', database='cefim_datawarehouse', user='root', password='Masterball41')
    return g.conn

def close_conn(e=None):
    conn = g.pop('conn', None)
    if conn is not None:
         conn.close()

def init_app(app):
    app.teardown_appcontext(close_conn)


