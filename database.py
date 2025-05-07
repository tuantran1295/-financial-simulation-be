import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_pool()
        return cls._instance

    def _init_pool(self):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            host=os.getenv('PG_HOST', 'localhost'),
            port=os.getenv('PG_PORT', '5432'),
            database=os.getenv('PG_DATABASE', 'simulation_games')
        )

    @contextmanager
    def get_conn(self):
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    def close_all(self):
        self.connection_pool.closeall()


# Game 1 operations
def get_game1_terms(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM game1_terms ORDER BY id")
        return cur.fetchall()


def update_game1_term(conn, term, team, value):
    with conn.cursor() as cur:
        column = 'team1_value' if team == 1 else 'team2_approval'
        cur.execute(
            f"UPDATE game1_terms SET {column} = %s, last_updated = NOW() WHERE term = %s",
            (value, term)
        )
        conn.commit()


# Game 2 operations
def get_game2_terms(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM game2_terms ORDER BY id")
        return cur.fetchall()


def update_game2_term(conn, term, team, company, value):
    with conn.cursor() as cur:
        column = f"team{team}_company{company}"
        cur.execute(
            f"UPDATE game2_terms SET {column} = %s, last_updated = NOW() WHERE term = %s",
            (value, term)
        )
        conn.commit()