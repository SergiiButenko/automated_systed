import logging
import os

import psycopg2
import psycopg2.extras
from commons.helpers.general import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    @retry(psycopg2.OperationalError, delay=15, logger=logger)
    def __init__(self):
        self.conn = None
        self.conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_DATABASE"],
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"],
        )
        self.conn.autocommit = False

        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def __del__(self):
        self.conn is not None and self.conn.close()

    def execute(self, query, params={}, method=None):
        try:
            self.cursor.execute(query, params)

            records = None
            if method is not None:
                records = getattr(self.cursor, method)()

            self.conn.commit()

            return records
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(
                "Error in transaction Reverting all other operations of a transaction ",
                error,
            )
            self.conn.rollback()
            raise error


DbProvider = Database()
