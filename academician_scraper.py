import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

warnings.filterwarnings("ignore", category=DeprecationWarning)

# WebDriver başlatma
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Arka planda çalışması için
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

base_url = "https://fen.ege.edu.tr/tr-8623/akademik_kadromuz.html"
driver.get(base_url)

data = []

try:
    time.sleep(5)  # Sayfanın yüklenmesini bekle

    # Ana sayfadan bölümlerin linklerini çek
    department_links = driver.find_elements(By.CSS_SELECTOR, "article p a")
    departments = [(link.text, link.get_attribute("href")) for link in department_links]

    print("Bölümler kontrol ediliyor...\n")
    for department_name, department_url in departments:
        print(f"Bölüm linkine gidiliyor: {department_url}")
        driver.get(department_url)
        time.sleep(3)

        try:
            # Akademisyen linklerini al
            academician_links = driver.find_elements(By.CSS_SELECTOR, "td a[href^='https://unisis.ege.edu.tr/researcher']")
            academicians = [(link.text, link.get_attribute("href")) for link in academician_links]

            print(f"\n{department_name} için akademisyen linkleri kontrol ediliyor:")
            for academician_name, academician_url in academicians:
                print(f"Akademisyen linkine gidiliyor: {academician_url}")
                try:
                    driver.get(academician_url)
                    time.sleep(2)

                    # Sayfanın kaynağını al ve BeautifulSoup ile işle
                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, 'html.parser')

                    # Akademisyen bilgilerini çek
                    researcher_name_div = soup.find("div", class_="col-12 fw-bold text-center fs-16 h1")
                    researcher_name = researcher_name_div.text.strip() if researcher_name_div else "Bilgi bulunamadı"

                    # Bölüm ve ana bilim dalı bilgilerini çek
                    department_div = soup.find("div", text="Bölüm")
                    department = department_div.find_next("div").text.strip() if department_div else "Bilgi bulunamadı"

                    discipline_div = soup.find("div", text="Ana bilim dalı")
                    discipline = discipline_div.find_next("div").text.strip() if discipline_div else "Bilgi bulunamadı"

                    # Anahtar kelimeleri çek
                    keywords = []
                    try:
                        keyword_divs = soup.find_all("div", class_="ant-space-item")
                        for keyword_div in keyword_divs:
                            keyword_span = keyword_div.find("span", class_="ant-tag ant-tag-has-color css-1v613y0")
                            if keyword_span:
                                keywords.append(keyword_span.text.strip())
                    except Exception as e:
                        print(f"Anahtar kelimeler alınamadı: {e}")

                    # Yayınları çek
                    publication_titles = []
                    try:
                        publications_tab = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Yayınlar')]"))
                        )
                        publications_tab.click()

                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//p[@class='fs-14 text-wrap search-item-header']"))
                        )

                        html_content = driver.page_source
                        soup = BeautifulSoup(html_content, 'html.parser')
                        publications = soup.find_all("p", class_="fs-14 text-wrap search-item-header")
                        publication_titles = [pub.text.strip() for pub in publications if pub.text.strip()]
                    except Exception:
                        pass  # Yayınlar sekmesi yoksa devam et

                    # JSON için veriyi kaydet
                    data.append({
                        "name": researcher_name,
                        "department": department,
                        "discipline": discipline,
                        "keywords": keywords,
                        "publications": publication_titles,
                        "profile_url": academician_url
                    })
                    print(f"Başarılı: {academician_name} - {academician_url}")

                except Exception as e:
                    print(f"Akademisyen bilgisi alınamadı: {academician_name} - {academician_url} - {e}")

        except Exception as e:
            print(f"{department_name} için akademisyen linkleri bulunamadı: {e}")

except Exception as e:
    print(f"Genel hata oluştu: {e}")

finally:
    driver.quit()

# Veriyi JSON dosyasına kaydet
with open("academician_publications", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Akademisyen verileri JSON dosyasına kaydedildi.")
