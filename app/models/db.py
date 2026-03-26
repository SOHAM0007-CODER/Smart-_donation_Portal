try:
    import MySQLdb  # noqa: F401
except ModuleNotFoundError:
    import pymysql

    pymysql.install_as_MySQLdb()

from flask_mysqldb import MySQL

mysql = MySQL()


def query_db(query, args=(), one=False, commit=False):
    """Helper to run queries cleanly."""
    from flask import current_app, g
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    if commit:
        mysql.connection.commit()
        cur.close()
        return cur.lastrowid
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
