import asyncio
import requests
from bs4 import BeautifulSoup
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
from FunPayAPI import Account

# ================= ДАННЫЕ =================
VK_TOKEN = "vk1.a.Urn5Te3N7wUPwhSeUkMq2ctSEGhZ_wg0Xsky6NsM8BS8ptHewESLcqqVd0AJ6HdSd6yIIqusjO_eLDCntCdj1_5LgUezE9qwwIhP07xU6QV27nDskPJigmpzoEVdZ0tWYyAHN0xfSdw31tESLTgiITu5aIAdmVP9MH2LD_pB24rRuktWxEIdDIgQ0cfwxJF7M6vM6QHp_jCauae3EY6FvA"
MY_VK_ID = 959374508
GOLDEN_KEY = "j7xn9ygomqkur4n1wec7t45ry56y4qrx"

SERVER_NAME = "Thunderstrike"
FP_URL = "https://funpay.com/chips/114/"

bot = Bot(token=VK_TOKEN)
account = Account(GOLDEN_KEY)

# ================= ПАРСЕР =================
def get_market_data():
    try:
        res = requests.get(FP_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        lots = []
        for item in soup.find_all('a', class_='tc-item'):
            if SERVER_NAME.lower() in item.text.lower():
                p = float(item.find('div', class_='tc-price').text.strip().split()[0].replace(',', '.'))
                u = item.find('div', class_='media-user-name').text.strip()
                lots.append({"user": u, "price": p})
        return sorted(lots, key=lambda x: x['price'])
    except: return []

# ================= ВК МЕНЮ =================
def main_kb():
    return (Keyboard(one_time=False)
            .add(Text("📊 Мониторинг"), color=KeyboardButtonColor.PRIMARY)
            .add(Text("🕵️ Spy"), color=KeyboardButtonColor.PRIMARY)
            .get_json())

@bot.on.message(text=["Начать", "Старт"])
async def start(m: Message):
    if m.from_id == MY_VK_ID:
        await m.answer(f"⚔️ Pixel Online! Сервер: {SERVER_NAME}", keyboard=main_kb())

@bot.on.message(text="📊 Мониторинг")
async def mon(m: Message):
    data = get_market_data()
    if data:
        await m.answer(f"📈 Мин. цена: {data[0]['price']} ₽\n💰 Чистыми: {round(data[0]['price']*0.92, 4)} ₽")

# ================= ФОНОВЫЙ ЦИКЛ =================
async def bg_tasks():
    last_id = None
    while True:
        try:
            account.raise_lots() # Поднимаем лоты
            chats = account.get_chats()
            if chats and chats[0].last_message_id != last_id:
                msg = chats[0]
                if any(x in msg.last_message_text.lower() for x in ["купил", "оплата"]):
                    await bot.api.messages.send(peer_id=MY_VK_ID, message=f"🚨 ЗАКАЗ: {msg.username}!", random_id=0)
                    account.send_message(msg.id, "Привет! Вижу заказ, скоро буду.")
                    # Авто-отзыв
                    async def review():
                        await asyncio.sleep(600)
                        account.send_message(msg.id, "Спасибо за покупку! Жду твой отзыв! ❤️")
                    asyncio.create_task(review())
                last_id = msg.last_message_id
        except: pass
        await asyncio.sleep(60) # Спим минуту

async def run_all():
    asyncio.create_task(bg_tasks())
    await bot.run_polling()

if __name__ == "__main__":
    asyncio.run(run_all())
