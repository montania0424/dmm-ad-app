from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

@app.route("/")
def index():
    keyword = request.args.get("q", "").strip()
    tag_filter = request.args.get("tag", "").strip()

    conn = sqlite3.connect("db/products.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if keyword:
        sql += " AND title LIKE ?"
        params.append(f"%{keyword}%")
    if tag_filter:
        sql += " AND tags LIKE ?"
        params.append(f"%{tag_filter}%")

    sql += " ORDER BY updated_at DESC LIMIT 100"
    cur.execute(sql, params)
    products = cur.fetchall()
    conn.close()

    return render_template("index.html", products=products, keyword=keyword, tag_filter=tag_filter)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
