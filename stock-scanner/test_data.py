"""Test fetching a single symbol to see the raw error."""
from datetime import datetime, timedelta
from alpaca_trade_api.rest import TimeFrame
from scanner.client import get_client

client = get_client()
end = datetime.now()
start = end - timedelta(days=300)

print(f"Fetching AAPL bars from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}...")

try:
    bars = client.get_bars(
        "AAPL",
        TimeFrame.Day,
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        adjustment="raw",
        feed="iex",
    )
    df = bars.df
    print(f"Got {len(df)} rows")
    print(df.tail(3))
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
