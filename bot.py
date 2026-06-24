import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ==================== ПРИВЕТСТВИЕ ====================
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📨 Отправить предложение",
                    callback_data="send_suggestion"
                )
            ]
        ]
    )

    await message.answer(
        "Все что угодно кидайте пишите Кароль всё посмотрит и ответит!.\n"
        "Нажми кнопку ниже, чтобы отправить сообщение:",
        reply_markup=keyboard
    )


# Обработка кнопки
@dp.callback_query(F.data == "send_suggestion")
async def suggest_button(callback):
    await callback.message.answer(
        "Теперь просто напиши сообщение, отправь фото, видео или голосовое.\n"
        "Я сразу передам это Каролю."
    )
    await callback.answer()


# ==================== ПЕРЕСЫЛКА СООБЩЕНИЙ ====================
@dp.message()
async def forward_to_admin(message: Message):
    # Игнорируем команды (чтобы /start не попадал сюда)
    if message.text and message.text.startswith('/'):
        return

    user = message.from_user

    info = f"📨 Новое предложение от пользователя:\n\n" \
           f"👤 Имя: {user.full_name}\n" \
           f"🔗 Username: @{user.username if user.username else 'нет'}\n" \
           f"🆔 ID: <code>{user.id}</code>\n" \
           f"──────────────────\n"

    try:
        if message.text:
            await bot.send_message(ADMIN_ID, info + message.text)

        elif message.photo:
            await bot.send_photo(
                ADMIN_ID,
                message.photo[-1].file_id,
                caption=info + (message.caption or "")
            )

        elif message.video:
            await bot.send_video(
                ADMIN_ID,
                message.video.file_id,
                caption=info + (message.caption or "")
            )

        elif message.voice:
            await bot.send_voice(ADMIN_ID, message.voice.file_id, caption=info)

        elif message.document:
            await bot.send_document(
                ADMIN_ID,
                message.document.file_id,
                caption=info + (message.caption or "")
            )

        else:
            await bot.send_message(ADMIN_ID, info + "📎 Отправил файл другого типа")

        await message.answer("Передано. Можешь отправить что-нибудь ещё.")

    except Exception as e:
        print("Ошибка:", e)
        await message.answer("❌ Что-то пошло не так. Попробуй ещё раз.")


async def main():
    print("✅ Предложка бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())