import yfinance as yf
import pandas as pd

# A known large-cap stock
TEST_TICKER = 'RELIANCE.NS'

print(f"--- Debugging with {TEST_TICKER} ---")

try:
    # Create a Ticker object
    stock = yf.Ticker(TEST_TICKER)

    # Fetch the info dictionary
    stock_info = stock.info

    print("\nFull 'info' dictionary returned by yfinance:")
    # Print the entire dictionary to see all available keys and their values
    for key, value in stock_info.items():
        print(f"  '{key}': {value}")

    # Specifically check for marketCap
    market_cap = stock_info.get('marketCap')
    print(f"\nValue of 'marketCap' key: {market_cap}")

    if market_cap:
        print(f"Market Cap is not None. Type: {type(market_cap)}")
        # Define the threshold for comparison
        threshold = 20000 * 10**7
        print(f"Threshold: {threshold:,.0f}")
        if market_cap > threshold:
            print(f"Comparison SUCCESS: {market_cap:,.0f} > {threshold:,.0f}")
        else:
            print(f"Comparison FAILED: {market_cap:,.0f} <= {threshold:,.0f}")
    else:
        print("\nMarket Cap is None or 0. The key might be missing or the value is empty.")

except Exception as e:
    print(f"\nAn error occurred: {e}")

print("\n--- Debugging CSV Ticker Reading ---")
try:
    df = pd.read_csv('Ticker_List_NSE_India.csv', usecols=['Yahoo_Equivalent_Code'])
    tickers = df['Yahoo_Equivalent_Code'].dropna().unique().tolist()
    print(f"Successfully read {len(tickers)} tickers.")
    print("First 5 tickers from CSV:")
    for t in tickers[:5]:
        # Print with quotes to see any hidden whitespace or characters
        print(f"  '{t.strip()}'")
except Exception as e:
    print(f"Could not read or parse CSV: {e}")
