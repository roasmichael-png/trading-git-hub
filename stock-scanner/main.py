"""Entry point — verifies connection and prints account summary."""
from scanner.client import get_client


def main():
    client = get_client()
    account = client.get_account()
    print(f"Account status : {account.status}")
    print(f"Equity         : ${float(account.equity):,.2f}")
    print(f"Cash           : ${float(account.cash):,.2f}")
    print(f"Buying power   : ${float(account.buying_power):,.2f}")


if __name__ == "__main__":
    main()
