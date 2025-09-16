import pandas as pd
import pandas_ta as ta
import yfinance as yf
import sys
import time
from datetime import datetime

# --- Configuration ---
TICKER_FILE = 'eligible_stocks.txt'
EMA_PERIOD = 200
# Timeframes to check, with yfinance intervals and human-readable names
TIMEFRames = {
    '1wk': 'Weekly',
    '1d': 'Daily',
    '1h': '4-Hour (resampled)', # We will fetch 1h and resample to 4h
    '1h_native': '1-Hour'
}
# Time to wait in seconds between full scans
SLEEP_INTERVAL = 1800 # 30 minutes

def get_tickers():
    """Reads tickers from the specified file."""
    try:
        with open(TICKER_FILE, 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded {len(tickers)} tickers from {TICKER_FILE}")
        return tickers
    except FileNotFoundError:
        print(f"ERROR: Ticker file not found at {TICKER_FILE}. Please run the screener first.")
        return []

def check_signal(ticker, interval, interval_name):
    """
    Checks a single ticker and timeframe for the 200 EMA touch signal.
    """
    try:
        data_period = "730d" if interval in ['1h', '1h_native'] else "5y"
        df = yf.download(ticker, interval=interval.replace('_native', ''), period=data_period, progress=False, auto_adjust=True)

        if df.empty:
            return

        if interval_name == '4-Hour (resampled)':
            df = df.resample('4H', base=1).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()

        df.ta.ema(length=EMA_PERIOD, append=True)
        df.dropna(inplace=True)

        if df.empty:
            return

        last_candle = df.iloc[-1]
        last_ema = last_candle[f'EMA_{EMA_PERIOD}']
        last_high = last_candle['High']
        last_low = last_candle['Low']
        last_close = last_candle['Close']

        if last_low <= last_ema <= last_high:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("\n" + "="*80)
            print(f"ALERT! [{timestamp}]")
            print(f"  Stock:    {ticker}")
            print(f"  Timeframe:{interval_name}")
            print(f"  Signal:   Price touched 200 EMA.")
            print(f"  Details:  Low ({last_low:.2f}) <= EMA ({last_ema:.2f}) <= High ({last_high:.2f})")
            print(f"  Close:    {last_close:.2f}")
            print("="*80 + "\n")

    except Exception:
        # Silently fail on purpose to keep the main loop running
        pass

def main():
    """
    Main function to run the monitor in a continuous loop.
    """
    print("Starting continuous trading signal monitor...")
    print(f"The script will scan all stocks and timeframes every {SLEEP_INTERVAL / 60:.0f} minutes.")
    print("Press Ctrl+C to exit.")

    while True:
        tickers = get_tickers()
        if not tickers:
            print("No tickers to process. Exiting.")
            break

        total_checks = len(tickers) * len(TIMEFRames)
        checks_done = 0

        scan_start_time = datetime.now()
        print(f"\n[{scan_start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting new scan...")

        for ticker in tickers:
            for interval, name in TIMEFRames.items():
                check_signal(ticker, interval, name)
                checks_done += 1
                sys.stdout.write(f"\rProgress: {checks_done}/{total_checks} checks completed...")
                sys.stdout.flush()

        scan_end_time = datetime.now()
        print(f"\n[{scan_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Scan complete. Duration: {scan_end_time - scan_start_time}")
        print(f"Sleeping for {SLEEP_INTERVAL / 60:.0f} minutes...")
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
