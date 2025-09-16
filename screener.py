import pandas as pd
import yfinance as yf
import time
import sys
import argparse

# Define the market cap threshold: 20,000 Crore INR = 2e11 INR
MARKET_CAP_THRESHOLD = 20000 * 10**7

# The name of the input CSV file and the output text file
INPUT_CSV = 'Ticker_List_NSE_India.csv'
OUTPUT_FILE = 'eligible_stocks.txt'

def screen_stocks(start_index, end_index):
    """
    Reads a list of NSE tickers, filters them by market cap,
    and appends the eligible tickers to a file.
    Processes a slice of the list from start_index to end_index.
    """
    print(f"--- Starting CHUNKED stock screening: {start_index} to {end_index} ---")

    try:
        df = pd.read_csv(INPUT_CSV, usecols=['Yahoo_Equivalent_Code'])
        tickers = df['Yahoo_Equivalent_Code'].dropna().unique().tolist()
    except Exception as e:
        print(f"FATAL: Error reading or parsing {INPUT_CSV}: {e}")
        return

    # Determine the slice of tickers to process
    if end_index > len(tickers):
        end_index = len(tickers)

    tickers_to_process = tickers[start_index:end_index]

    if not tickers_to_process:
        print("No tickers to process in this range.")
        return

    print(f"Processing {len(tickers_to_process)} tickers (from index {start_index} to {end_index}).")

    eligible_stocks = []

    for i, ticker_str in enumerate(tickers_to_process):
        ticker = str(ticker_str).strip(" ',")

        if not ticker or not ticker.endswith('.NS'):
            continue

        try:
            stock_info = yf.Ticker(ticker).info
            market_cap = stock_info.get('marketCap', 0)

            if market_cap and market_cap > MARKET_CAP_THRESHOLD:
                eligible_stocks.append(ticker)
                print(f"  [+] Found eligible stock: {ticker}")

            time.sleep(0.1)

        except Exception:
            # Silently skip tickers that fail to fetch
            pass

    print(f"\nChunk processing complete. Found {len(eligible_stocks)} eligible stocks in this chunk.")

    # Append the results to the file
    try:
        with open(OUTPUT_FILE, 'a') as f:
            for stock in eligible_stocks:
                f.write(f"{stock}\n")
        print(f"Successfully appended {len(eligible_stocks)} stocks to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error appending to {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Screen stocks by market cap in chunks.")
    parser.add_argument("--start", type=int, required=True, help="Start index of the ticker list to process.")
    parser.add_argument("--end", type=int, required=True, help="End index of the ticker list to process.")
    args = parser.parse_args()

    screen_stocks(args.start, args.end)
