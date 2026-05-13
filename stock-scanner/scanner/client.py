import alpaca_trade_api as tradeapi
import config


def get_client() -> tradeapi.REST:
    return tradeapi.REST(
        key_id=config.ALPACA_API_KEY,
        secret_key=config.ALPACA_SECRET_KEY,
        base_url=config.ALPACA_BASE_URL,
    )
