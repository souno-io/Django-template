from django.db import connections
from collections import namedtuple


class His:
    """
    本类为医院His数据库集成化操作类，提供对医院的常见数据库操作
    """

    def __init__(self, sql, params=()):
        self.conn = connections['his']
        self.cursor = self.conn.cursor()
        self.query_sql = sql
        self.query_params = params

    def __enter__(self):
        return self

    def get_cursor(self):
        return self.cursor

    def get_conn(self):
        return self.conn

    def execute(self):
        try:
            result = self.cursor.execute(self.query_sql)
        except Exception as e:
            result = str(e)
        return result

    def fetch_one(self):
        try:
            self.cursor.execute(self.query_sql, self.query_params)
            result = self.cursor.fetchone()
        except Exception as e:
            result = str(e)
        return result

    def fetch_all(self):
        try:
            self.cursor.execute(self.query_sql, self.query_params)
            result = self.cursor.fetchall()
        except Exception as e:
            result = str(e)
        return result

    def rows_as_dicts(self):
        try:
            self.cursor.execute(self.query_sql, self.query_params)
            col_names = [i[0] for i in self.cursor.description]
            result = [dict(zip(col_names, row)) for row in self.cursor]
        except Exception as e:
            result = str(e)
        return result

    def row_as_namedtuple(self):
        try:
            self.cursor.execute(self.query_sql, self.query_params)
            desc = self.cursor.description
            nt_result = namedtuple('Result', [col[0] for col in desc])
            result = [nt_result(*row) for row in self.cursor.fetchall()]
        except Exception as e:
            result = str(e)
        return result

    def commit(self):
        self.conn.commit()

    def close_cursor(self):
        self.cursor.close()

    def close_conn(self):
        self.conn.close()

    def close(self):
        self.close_cursor()
        self.close_conn()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
