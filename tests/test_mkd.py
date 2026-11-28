import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone, date
from uuid import uuid4
from buffettvalue.mkd import latest_price

class MkdTests(unittest.TestCase):
    def test_scope_and_quality(self):
        conn=MagicMock()
        cur=conn.cursor.return_value.__enter__.return_value
        now=datetime(2026,11,27,tzinfo=timezone.utc)
        cur.fetchone.return_value=(10,date(2026,11,26),"EUR","valid",now,now)
        self.assertEqual(latest_price(conn,uuid4(),currency="EUR",as_of=now)["price"],10)
        with self.assertRaises(ValueError):
            latest_price(conn,uuid4(),currency="GBP",as_of=now)
        cur.fetchone.return_value=(10,date(2026,11,26),"EUR","legacy_unverified",now,now)
        with self.assertRaises(ValueError):
            latest_price(conn,uuid4(),currency="EUR",as_of=now)
        cur.fetchone.return_value=(10,date(2026,11,26),"EUR","valid",now,datetime(2026,11,26,tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            latest_price(conn,uuid4(),currency="EUR",as_of=now)
