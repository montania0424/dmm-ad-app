import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from datetime import datetime
import time

DB_PATH = "db/products.db"
BASE_URL = "https://video.dmm.co.jp/av/list/?sort=ranking&page="

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_dmm_ranking(pages=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for page in range(1, pages + 1):
        url = BASE_URL + str(page)
        print(f"📥 取得中: {url}")
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.content, "html.parser")

        items = soup.select(".d-item")
        print(f"🔍 ページ {page} で {len(items)} 件の作品を検出しました。")

        for item in items:
            try:
                # 商品IDをURLから取得
                link = item.select_one("a")
                if not link:
                    continue
                detail_url = link["href"]
                id_match = re.search(r"/cid=(.+?)/", detail_url)
                product_id = id_match.group(1) if id_match else detail_url.split("/")[-2]

                title = item.select_one(".d-item__title").get_text(strip=True)
                image_url = item.select_one("img")["src"]

                # 価格
                price_tag = item.select_one(".d-item__price")
                price = float(price_tag.get_text(strip=True).replace("円", "").replace(",", "").strip()) if price_tag else None

                # 女優名
                actress = ""
                actress_tag = item.select_one(".d-item__actress")
                if actress_tag:
                    actress = actress_tag.get_text(strip=True)

                # DBに保存（upsert）
                c.execute("""
                    INSERT OR REPLACE INTO products (
                        id, title, actress, image_url, detail_url,
                        price, updated_at, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id, title, actress, image_url, detail_url,
                    price, datetime.now(), "DMM"
                ))

            except Exception as e:
                print(f"⚠️ エラー発生：{e}")

        time.sleep(1)

    conn.commit()
    conn.close()
    print("✅ スクレイピング完了しました。")

if __name__ == "__main__":
    scrape_dmm_ranking(pages=2)
