from scanner.client import get_client
from scanner.scan import run_scan


def print_account():
    client = get_client()
    account = client.get_account()
    print(f"Account status : {account.status}")
    print(f"Equity         : ${float(account.equity):,.2f}")
    print(f"Cash           : ${float(account.cash):,.2f}")
    print(f"Buying power   : ${float(account.buying_power):,.2f}\n")


if __name__ == "__main__":
    print_account()
    hits = run_scan()

    if not hits:
        print("No setups found today.")
    else:
        print(f"\n{'='*70}")
        print(f"  {len(hits)} SETUP(S) FOUND")
        print(f"{'='*70}")
        print(f"{'SYM':<6} {'CLOSE':>8} {'SMA200':>8} {'%FROM':>7} {'K':>6} {'D':>6} {'MACD':>8} {'SIG':>8}")
        print(f"{'-'*70}")
        for h in hits:
            print(
                f"{h['symbol']:<6} {h['close']:>8.2f} {h['sma200']:>8.2f} "
                f"{h['pct_from_200']:>6.1f}% {h['srsi_k']:>6.1f} {h['srsi_d']:>6.1f} "
                f"{h['macd']:>8.2f} {h['macd_signal']:>8.2f}"
            )
