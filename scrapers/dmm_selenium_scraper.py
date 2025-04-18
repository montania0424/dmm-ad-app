from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time

DB_PATH = "db/products.db"
BASE_URL = "https://video.dmm.co.jp/av/list/?sort=ranking&page="

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def handle_age_verification(driver):
    try:
        yes_button = driver.find_element(By.CLASS_NAME, "age-check__yes-button")
        yes_button.click()
        print("🔓 年齢確認ページを突破しました。")
        time.sleep(2)
    except:
        print("🔍 年齢確認ページは表示されませんでした。")
        pass

def close_popup_if_exists(driver):
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".popup, .modal, .overlay"))
        )
        close_btn = popup.find_element(By.CSS_SELECTOR, "button, .close, .btn-close")
        close_btn.click()
        print("🔕 ポップアップを閉じました。")
        time.sleep(1)
    except:
        pass

def close_alert_if_present(driver):
    try:
        alert = driver.switch_to.alert
        print(f"⚠️ アラート検出: {alert.text}")
        alert.accept()
        time.sleep(1)
        return True
    except:
        return False

def scrape_dmm_with_selenium(pages=2):
    driver = setup_driver()
    print("🔐 DMMログインページを開きます。ログイン後、Enterキーを押してください...")
    driver.get("https://www.dmm.co.jp/")
    input("➡ ログイン完了後に Enter を押してください：")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try: c.execute("ALTER TABLE products ADD COLUMN tags TEXT")
    except: pass
    try: c.execute("ALTER TABLE products ADD COLUMN review_text TEXT")
    except: pass

    for page in range(1, pages + 1):
        url = BASE_URL + str(page)
        print(f"📥 取得中: {url}")
        driver.get(url)
        time.sleep(3)
        handle_age_verification(driver)
        close_popup_if_exists(driver)
        close_alert_if_present(driver)
        time.sleep(2)

        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/detail/=/cid=']")
        print(f"🔍 ページ {page} 商品リンク数: {len(links)}")

        for link in links:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", link)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(link))
                link.click()

                close_alert_if_present(driver)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".price"))
                )
                close_popup_if_exists(driver)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                detail_url = driver.current_url
                product_id = detail_url.split("cid=")[-1].strip("/")

                title_tag = soup.select_one("img[alt]")
                title = title_tag["alt"].strip() if title_tag else "タイトル不明"

                image_tag = soup.select_one("img")
                image_url = image_tag["src"] if image_tag else ""

                price = None
                price_tag = soup.select_one(".price")
                if price_tag:
                    price_text = price_tag.get_text(strip=True).replace("円", "").replace(",", "")
                    try:
                        price = float(price_text)
                    except:
                        price = None

                review_count = None
                score = None
                try:
                    review_tag = soup.select_one(".review-count, .d-review__summary__count")
                    if review_tag:
                        review_count = int(review_tag.get_text(strip=True).replace("件", "").replace(",", ""))
                except:
                    pass
                try:
                    score_tag = soup.select_one(".review-point, .d-review__summary__average")
                    if score_tag:
                        score = float(score_tag.get_text(strip=True))
                except:
                    pass

                tags = ", ".join([t.get_text(strip=True) for t in soup.select(".d-item__label a")])
                review_text_tag = soup.select_one(".d-review__comment")
                review_text = review_text_tag.get_text(strip=True) if review_text_tag else ""

                actress = ""

                c.execute("""
                    INSERT OR REPLACE INTO products (
                        id, title, actress, image_url, detail_url,
                        price, updated_at, source, review_count, score, tags, review_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id, title, actress, image_url, detail_url,
                    price, datetime.now().isoformat(), "DMM", review_count, score, tags, review_text
                ))

                driver.back()
                close_alert_if_present(driver)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/detail/=/cid=']"))
                )
                time.sleep(2)

            except (StaleElementReferenceException, UnexpectedAlertPresentException) as e:
                print(f"⚠️ 一時エラー: {e}")
                close_alert_if_present(driver)
                driver.back()
            except Exception as e:
                print(f"⚠️ エラー: {e}")
                driver.back()

    conn.commit()
    conn.close()
    driver.quit()
    print("✅ Seleniumスクレイピング完了！")

if __name__ == "__main__":
    scrape_dmm_with_selenium(pages=2)