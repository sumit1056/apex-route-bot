import os
import json
import gspread
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from google.oauth2.service_account import Credentials

# ── Config ──────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SHEET_ID  = os.environ.get("SHEET_ID")
CREDS_JSON = os.environ.get("GOOGLE_CREDS")

# ── Google Sheets connection ─────────────────────────────────
def get_sheet(tab_name):
    creds_dict = json.loads(CREDS_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.worksheet(tab_name)

def save_to_sheet(entry_type, category, amount):
    tab = "Income" if entry_type == "Income" else "Expenses"
    ws = get_sheet(tab)
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    all_rows = ws.get_all_values()
    # Insert before last row (TOTAL row)
    row_num = len(all_rows) - 1
    ws.insert_row([row_num, date, time, category, amount, ""], len(all_rows))

# ── Bot Handlers ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [[
        InlineKeyboardButton("💰 Add Income",  callback_data="TYPE_Income"),
        InlineKeyboardButton("💸 Add Expense", callback_data="TYPE_Expense")
    ]]
    await update.message.reply_text(
        "👋 Welcome to *Apex Route Tracker!*\nWhat would you like to record?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("TYPE_"):
        entry_type = data.replace("TYPE_", "")
        context.user_data["type"] = entry_type

        if entry_type == "Income":
            cats = ["Vendor/DCO", "Porter", "Factory"]
        else:
            cats = ["CNG/Petrol", "Maintenance", "Driver Expense", "Other"]

        keyboard = []
        for i in range(0, len(cats), 2):
            row = [InlineKeyboardButton(cats[i], callback_data="CAT_" + cats[i])]
            if i + 1 < len(cats):
                row.append(InlineKeyboardButton(cats[i+1], callback_data="CAT_" + cats[i+1]))
            keyboard.append(row)

        await query.message.reply_text(
            f"You chose *{entry_type}*.\nNow select a category:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("CAT_"):
        category = data.replace("CAT_", "")
        context.user_data["category"] = category
        await query.message.reply_text(
            f"📂 Category: *{category}*\n\nNow type the *amount* (numbers only):",
            parse_mode="Markdown"
        )

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    entry_type = context.user_data.get("type")
    category   = context.user_data.get("category")

    if not entry_type or not category:
        await update.message.reply_text("Please tap /start to begin a new entry.")
        return

    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number only. Example: *1500*", parse_mode="Markdown")
        return

    save_to_sheet(entry_type, category, amount)
    context.user_data.clear()

    emoji = "💰" if entry_type == "Income" else "💸"
    await update.message.reply_text(
        f"{emoji} *Entry Saved Successfully!*\n\n"
        f"• Type: *{entry_type}*\n"
        f"• Category: *{category}*\n"
        f"• Amount: *₹{amount:,.0f}*\n\n"
        f"Tap /start to add another entry.",
        parse_mode="Markdown"
    )

# ── Main ─────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
