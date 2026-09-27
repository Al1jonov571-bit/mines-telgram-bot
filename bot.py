import os
import hashlib
import hmac
import random

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN", "BU_YERGA_BOT_TOKENINGIZ")


def generate_mines(server_seed, client_seed, nonce, mine_count):
    message = f"{client_seed}:{nonce}".encode()
    digest = hmac.new(
        server_seed.encode(),
        message,
        hashlib.sha256
    ).digest()

    values = list(range(25))

    # deterministic shuffle
    rng = random.Random(int.from_bytes(digest, "big"))

    for i in range(24, 0, -1):
        j = rng.randrange(i + 1)
        values[i], values[j] = values[j], values[i]

    mines = set(values[:mine_count])
    return mines


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💣 Mines verifier\n\n"
        "Bu bot yashirin kelajakdagi bombalarni oldindan "
        "aniqlamaydi.\n\n"
        "Tekshirish uchun:\n"
        "/check SERVER_SEED CLIENT_SEED NONCE MINES"
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 4:
        await update.message.reply_text(
            "Format:\n"
            "/check SERVER_SEED CLIENT_SEED NONCE MINES"
        )
        return

    server_seed = context.args[0]
    client_seed = context.args[1]
    nonce = context.args[2]

    try:
        mine_count = int(context.args[3])
    except ValueError:
        await update.message.reply_text("MINES son bo‘lishi kerak.")
        return

    if not 1 <= mine_count <= 24:
        await update.message.reply_text(
            "Mines soni 1–24 oralig‘ida bo‘lsin."
        )
        return

    mines = generate_mines(
        server_seed,
        client_seed,
        nonce,
        mine_count
    )

    board = []

    for i in range(25):
        if i in mines:
            board.append("💣")
        else:
            board.append("⬜")

    text = "Mines natijasi:\n\n"

    for row in range(5):
        text += " ".join(board[row * 5:(row + 1) * 5]) + "\n"

    text += "\n💣 Bombalar: "
    text += ", ".join(str(x + 1) for x in sorted(mines))

    await update.message.reply_text(text)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))

print("🤖 BOT ISHLAYAPTI...")
app.run_polling()
