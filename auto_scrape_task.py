import schedule
import time
import subprocess
import os

def run_scraper():
    script_path = os.path.join("scrapers", "dmm_selenium_scraper.py")
    print("🔁 スクレイピング開始...")
    subprocess.run(["python", script_path], check=False)

# 毎日午前4時に実行
schedule.every().day.at("04:00").do(run_scraper)

print("⏰ 毎朝4時に自動スクレイピングを実行します。待機中...")

while True:
    schedule.run_pending()
    time.sleep(60)
