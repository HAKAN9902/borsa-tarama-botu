script_content = '''import os
import pandas as pd
import requests
from google.colab import userdata # Import userdata for Colab secrets

# Ensure tradingview-screener is installed before import
!pip install tradingview-screener

from tradingview_screener import Query, Column # Import after ensuring installation

# --- CONFIGURATION ---
TOKEN = userdata.get('TELEGRAM_TOKEN')
CHAT_ID = userdata.get('TELEGRAM_CHAT_ID')
DB_FILE = "last_results.csv"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)

def borsa_taramasi():
    try:
        # 1. Get Data
        sorgu = (
            Query().set_markets('turkey')
            .select('name', 'close', 'change')
            .where(Column('RSI7').crosses_above(70))
            .get_scanner_data()
        )

        df_new = sorgu[1] # TradingView returns a tuple (count, data)
        if df_new.empty:
            return

        current_symbols = set(df_new['name'].tolist())

        # 2. Compare with previous run
        if os.path.exists(DB_FILE):
            df_old = pd.read_csv(DB_FILE)
            old_symbols = set(df_old['name'].tolist())
        else:
            old_symbols = set()

        # Find truly new signals (symbols in current but not in old)
        new_signals = current_symbols - old_symbols

        # 3. Alert and Save
        if new_signals:
            for ticker in new_signals:
                row = df_new[df_new['name'] == ticker].iloc[0]
                msg = f"🚀 YENİ SİNYAL: {ticker}\nFiyat: {row['close']}\nDeğişim: %{row['change']:.2f}"
                send_telegram(msg)

        # Save current state for next run
        df_new[['name']].to_csv(DB_FILE, index=False)

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    borsa_taramasi()'''

with open('main.py', 'w') as f:
    f.write(script_content)

print("Python script saved as main.py")
