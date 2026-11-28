"""Read-only shared MKD market price adapter for fundamental research."""
from datetime import datetime, timezone, date
from decimal import Decimal
from uuid import UUID

def latest_price(connection, instrument_id, *, currency, as_of):
    if currency not in ("EUR","USD") or not isinstance(as_of,datetime) or as_of.utcoffset() is None or as_of > datetime.now(timezone.utc):
        raise ValueError("EUR/USD and aware cutoff required")
    instrument_id=UUID(str(instrument_id))
    with connection.cursor() as c:
        c.execute("""SELECT close,session_date,currency,quality_status,published_at,first_available_at
            FROM public.eod_bars WHERE instrument_id=%s AND provider='yahoo'
            AND currency=%s AND published_at<=%s AND first_available_at<=%s
            AND session_date<=%s
            ORDER BY session_date DESC,revision DESC LIMIT 1""",
            (instrument_id,currency,as_of,as_of,as_of.date()))
        row=c.fetchone()
    if not row or row[2]!=currency or row[3]!="valid" or type(row[1]) is not date or not all(isinstance(t,datetime) and t.utcoffset() is not None for t in row[4:6]) or not row[4]<=row[5]<=as_of or row[1]>row[4].date():
        raise ValueError("qualified MKD price unavailable")
    price=Decimal(str(row[0]))
    if not price.is_finite() or price<=0 or not 0<=(as_of.date()-row[1]).days<=4:
        raise ValueError("invalid or stale MKD price")
    return {"price":price,"currency":currency,"session_date":row[1],"source":"MKD","paper_eligible":False}
