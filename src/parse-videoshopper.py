import datetime
import time
import requests as r
import random
from bs4 import BeautifulSoup as bs
import schedule
import sqlite3
import telebot
from dotenv import load_dotenv
import os

load_dotenv()
tgbotapikey = os.getenv('TGBOT_TOKEN')
tgbotchatid = os.getenv('CHAT_ID')
dbconnection = sqlite3.connect("iphoneprice.db")
cursor = dbconnection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS price(timestamp TIMESTAMP, price INTEGER)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON price(timestamp)')
dbconnection.commit()
url = 'https://video-shoper.ru/shipment/apple-iphone-17-pro-256gb-esim-cosmic-orange-oranzhevyy.html'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "Cookie": "beget=begetok"
}
def iphone():
    # startexecution = time.time()
    res=r.get(url, headers=headers)

    try:
        soup = bs(res.content, 'html.parser')
        content = soup.find('div', class_='current')
        replaced = content.text.replace('₽', '')
        rpl = str(replaced).replace(' ', '').strip()
    except Exception as e:
        error = f'Ошибка, проверь логи {e}'
        bot = telebot.TeleBot(tgbotapikey)
        bot.send_message(tgbotchatid, error)
        return
    # rpl = 99995
    print('Текущая цена: ', rpl, '\n')
    # endexecution = time.time()
    # timeofrequest = endexecution - startexecution
    # print('Время выполнения запроса: ',round(timeofrequest,1), 'секунд\n')
    timestampofexec = time.strftime('%H:%M:%S', time.localtime(time.time()))
    dateofexec = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    full_timestamp = f"{dateofexec} {timestampofexec}"

    cursor.execute('INSERT INTO price (timestamp, price) VALUES (?, ?)', (full_timestamp, rpl))
    dbconnection.commit()

    cursor.execute('SELECT * FROM price ORDER BY timestamp DESC LIMIT 5')
    recent_records = cursor.fetchall()
    print(f"Последние {len(recent_records)} записей в БД:")
    for record in recent_records:
        print(f"  {record[0]} - {record[1]} руб.")
    cursor.execute('''DELETE FROM price WHERE date(timestamp) < date('now', '-3 days')''')
    dbconnection.commit()
    sendtelegrammessage(rpl)
    return rpl

def sendtelegrammessage(rpl):
    cursor.execute('SELECT price FROM price ORDER BY timestamp DESC LIMIT 1 OFFSET 1')
    result = cursor.fetchone()
    if result:
        current_price = int(rpl)
        previous_price = int(result[0])
        if current_price < previous_price:
            cost = f'Цена на телефон упала! Было: {previous_price} руб., Стало: {current_price} руб.'
            bot = telebot.TeleBot(tgbotapikey)
            bot.send_message(tgbotchatid, cost)
            print(cost)
        elif current_price > previous_price:
            cost = f'Цена на телефон выросла! Было: {previous_price} руб., Стало: {current_price} руб.'
            bot = telebot.TeleBot(tgbotapikey)
            bot.send_message(tgbotchatid, cost)

if __name__ == '__main__':
    iphone()

    next_interval = random.randint(5, 20)
    schedule.every(next_interval).minutes.do(iphone)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        cursor.close()
        dbconnection.close()