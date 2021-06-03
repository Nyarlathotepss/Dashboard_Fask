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


