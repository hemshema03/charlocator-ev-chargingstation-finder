import os
import mysql.connector


class Db:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "root123"),
            database=os.environ.get("DB_NAME", "ev_db4")
        )
        self.cur = self.cnx.cursor(dictionary=True, buffered=True)

    def select(self, q, params=None):
        self.cur.execute(q, params)
        return self.cur.fetchall()

    def selectOne(self, q, params=None):
        self.cur.execute(q, params)
        return self.cur.fetchone()

    def insert(self, q, params=None):
        self.cur.execute(q, params)
        self.cnx.commit()
        return self.cur.lastrowid

    def update(self, q, params=None):
        self.cur.execute(q, params)
        self.cnx.commit()
        return self.cur.rowcount

    def delete(self, q, params=None):
        self.cur.execute(q, params)
        self.cnx.commit()
        return self.cur.rowcount
