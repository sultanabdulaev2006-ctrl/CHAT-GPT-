import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
import aiohttp

# ====== Настройки ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API = os.getenv("HF_API")

if not BOT_TOKEN or not HF_API:
    raise ValueError("❌ BOT_TOKEN или HF_API не заданы!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== Веб сервер для Render ======
async def handle(request):
    return web.Response(text="AI Bot is running 🚀")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    port = int(os.getenv("PORT", 8000))  # Render автоматически задаёт PORT
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server running on port {port}")

# ====== Функция для общения с Hugging Face ======
async def ask_ai(prompt: str) -> str:
    url = "https://api-inference.huggingface.co/models/gpt2"  # бесплатная модель
    headers = {"Authorization": f"Bearer {HF_API}"}
    json_data = {"inputs": prompt}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data[0]["generated_text"]
            else:
                return "❌ Ошибка: не удалось получить ответ от ИИ."

# ====== Новый хэндлер: любые сообщения через ИИ ======
@dp.message()
async def ai_reply(message: types.Message):
    await message.chat.do("typing")  # Показывает "печатает"
    response = await ask_ai(message.text)
    await message.answer(response)

# ====== Запуск ======
async def main():
    asyncio.create_task(start_web())  # веб-сервер для Render
    print("🤖 AI Bot запущен и работает 24/7")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
