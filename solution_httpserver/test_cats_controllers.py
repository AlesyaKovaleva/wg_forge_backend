import os
import unittest

import psycopg2
from mock import patch
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from cats_controllers import cats, ping, post_cats
from cats_sqlalhemy import Cats, db_session
from settings import DB_HOST, DB_PASSWORD, DB_USER as USER


DB_NAME = "test_wg_forge_db"
DB_USER = "postgres"

TEST_DB_PATH = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


def setUpModule():
    engine = create_engine(TEST_DB_PATH)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)

    conn = psycopg2.connect(
        dbname=DB_NAME, user=USER, password=DB_PASSWORD, host=DB_HOST
    )
    cursor = conn.cursor()

    with open(
        os.path.join(
            os.path.dirname(__file__), "../task_wg_forge_backend/wg_forge_init.sql"
        )
    ) as f:
        initial_sql = f.read()

    cursor.execute(initial_sql)
    cursor.close()
    conn.commit()
    conn.close()


def tearDownModule():
    engine = create_engine(TEST_DB_PATH)
    if database_exists(engine.url):
        drop_database(engine.url)


class PingTestCase(unittest.TestCase):
    def test_ping(self):
        status_code, data, headers = ping()
        self.assertEqual(status_code, 200)
        self.assertEqual(data, "Cats Service. Version 0.1")
        self.assertDictEqual(headers, {"Content-type": "text/html"})


class CatTestCase(unittest.TestCase):
    def test_cats_order(self):
        with patch("cats_sqlalhemy.DB_PATH", new=TEST_DB_PATH):
            with db_session() as session:
                status_code, data, headers = cats(
                    {"attribute": ["name"], "order": ["desc"]}, session
                )

        self.assertEqual(status_code, 200)
        self.assertEqual(len(data), 27)

        # check first and last cats
        self.assertDictEqual(
            data[-1],
            {
                "name": "Amur",
                "color": "black & white",
                "tail_length": 20,
                "whiskers_length": 11,
            },
        )
        self.assertDictEqual(
            data[0],
            {
                "name": "Yasha",
                "color": "red & white",
                "tail_length": 18,
                "whiskers_length": 12,
            },
        )

    def test_cats_offset(self):
        with patch("cats_sqlalhemy.DB_PATH", new=TEST_DB_PATH):
            with db_session() as session:
                status_code, data, headers = cats({"offset": ["7"]}, session)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(data), 20)

        self.assertDictEqual(
            data[0],
            {
                "name": "Vika",
                "color": "black",
                "tail_length": 14,
                "whiskers_length": 10,
            },
        )
        self.assertDictEqual(
            data[-1],
            {
                "name": "Nemo",
                "color": "red & white",
                "tail_length": 17,
                "whiskers_length": 13,
            },
        )

    def test_cats_limit(self):
        with patch("cats_sqlalhemy.DB_PATH", new=TEST_DB_PATH):
            with db_session() as session:
                status_code, data, headers = cats({"limit": ["1"]}, session)

        self.assertEqual(status_code, 200)
        self.assertEqual(len(data), 1)

        self.assertDictEqual(
            data[0],
            {
                "name": "Tihon",
                "color": "red & white",
                "tail_length": 15,
                "whiskers_length": 12,
            },
        )

    def test_cats(self):
        with patch("cats_sqlalhemy.DB_PATH", new=TEST_DB_PATH):
            with db_session() as session:
                status_code, data, headers = cats(
                    {
                        "attribute": ["tail_length"],
                        "order": ["asc"],
                        "offset": ["26"],
                        "limit": ["1"],
                    },
                    session,
                )

        self.assertEqual(status_code, 200)
        self.assertEqual(len(data), 1)

        self.assertDictEqual(
            data[0],
            {
                "name": "Kelly",
                "color": "red & white",
                "tail_length": 26,
                "whiskers_length": 11,
            },
        )


class PostCats(unittest.TestCase):
    def test_post_cats(self):
        with patch("cats_sqlalhemy.DB_PATH", new=TEST_DB_PATH):
            with db_session() as session:
                data = '{"name": "Zzz", "color": "red & white", "tail_length": 28, "whiskers_length": 20}'
                post_cats(data, session)

                new_cat = session.query(Cats).filter(Cats.name == "Zzz").one()

                self.assertEqual(("Zzz, red & white, 28, 20"), str(new_cat))


if __name__ == "__main__":
    unittest.main(verbosity=2)
