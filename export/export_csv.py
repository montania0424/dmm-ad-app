import sqlite3
import pandas as pd
import os

# データベースパス
DB_PATH = os.path.join("db", "products.db")
CSV_PATH = os.path.join("export", "products.csv")

# フォルダ作成
os.makedirs("export", exist_ok=True)

# データ抽出とCSV保存
def export_products_to_csv():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM products ORDER BY updated_at DESC", conn)
    conn.close()
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ CSVエクスポート完了: {CSV_PATH}")

if __name__ == "__main__":
    export_products_to_csv()
