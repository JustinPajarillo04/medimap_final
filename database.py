import os
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self):
        self.host = "localhost"
        self.database = "medimap_db"
        self.user = "postgres"
        self.password = "pajarillo14"
        self.port = "5432"

    def connect(self):
        database_url = os.environ.get("DATABASE_URL")

        if database_url:
            return psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )

        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
            cursor_factory=RealDictCursor
        )