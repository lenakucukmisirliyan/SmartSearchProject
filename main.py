import requests
import re
import json
from bs4 import BeautifulSoup
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)
# URL'den veri çekme
url = "https://webservice.infinityyazilim.com/Api/CatalogTrainingNameList?token=D60338DE-881A-466D-998A-F0B11821A73D"


# Veri çekme ve kaydetme fonksiyonu
def fetch_and_save_trainings():
    response = requests.get(url)
    response.encoding = 'utf-8'
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    metin = soup.get_text()
    pattern = r"Eğitim Adı: (.+?)\sKategori: (.+?)\n"
    results = re.findall(pattern, metin)
    json_data = [{"Eğitim Adı": item[0], "Kategori": item[1]} for item in results]
    with open("egitimler.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

# Flask yapısında veri güncelleyici işlev
def start_background_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_save_trainings, 'interval', hours=24)  # Her 24 saatte bir çalışsın.
    scheduler.start()

# Flask uygulama başlatma
@app.route("/")
def home():
    return "Merhaba! Bot çalışıyor..."

if __name__ == "__main__":
    start_background_scheduler()  # Scheduler'ı başlat
    app.run(debug=True)

# Fonksiyonlar
def get_trainings_by_keyword(keyword):
    with open("egitimler.json", "r", encoding="utf-8") as f:
        all_trainings = json.load(f)
    filtered_trainings = [training for training in all_trainings if
                          keyword.lower() in training["Eğitim Adı"].lower() or keyword.lower() in training[
                              "Kategori"].lower()]
    return filtered_trainings


# Başlangıç mesajı ve kullanıcıdan veri alma
def start_chatbot():

    print("Merhaba! Lütfen eğitim önerisi almak istediğiniz yetkinlik veya konuyu giriniz...")

    while True:
        keyword = input("Anahtar kelime girin: ").strip()

        if not keyword:
            print("Lütfen geçerli bir anahtar kelime giriniz.")
            continue

        if keyword.lower() == 'çıkış':
            print("Botu kapatıyorum. Görüşmek üzere!")
            break

        results = get_trainings_by_keyword(keyword)

        if results:
            print("\nİlgili Eğitimler:")
            for training in results:
                print(f" - {training['Eğitim Adı']} ({training['Kategori']})")
        else:
            print("Bu yetkinlik veya konuya uygun eğitim bulunamadı.")

        print("\nYeni bir anahtar kelime girmek için ENTER'a basın...")


# Eğitimleri sürekli güncelleyen fonksiyonu çalıştır
fetch_and_save_trainings()

# Botu başlat
start_chatbot()
