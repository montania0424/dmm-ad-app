import sqlite3

def init_db():
    conn = sqlite3.connect("db/products.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            actress TEXT,
            genre TEXT,
            image_url TEXT,
            detail_url TEXT,
            price REAL,
            sale_price REAL,
            discount_rate INTEGER,
            score REAL,
            review_count INTEGER,
            tags TEXT,
            recommendation TEXT,
            source TEXT,
            updated_at DATETIME
        )
    """)

    conn.commit()
    conn.close()
    print("✅ データベース products.db を初期化しました。")

if __name__ == "__main__":
    init_db()
