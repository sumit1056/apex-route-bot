import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import gspread
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from google.oauth2.service_account import Credentials

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "8531728576:AAGvpCGkhk_zJwrY5eJD9jealbveAxns3yY")
SHEET_ID   = os.environ.get("SHEET_ID", "1bu5fls4crB6nQpLfLQgE3wGCdOdq3mr-9jws5foXctE")
CREDS_JSON = os.environ.get("GOOGLE_CREDS")

INCOME_CATS  = ["Vendor/DCO", "Porter", "Factory"]
EXPENSE_CATS = ["CNG/Petrol", "Maintenance", "Driver Expense", "EMI", "Credit Card Bill", "Other"]

def get_sheet(tab_name):
    creds_dict = json.loads(CREDS_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(tab_name)

def save_income(category, payment, amount, remarks=""):
    ws   = get_sheet("Income")
    now  = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    rows = ws.get_all_values()
    bank_amt = amount if payment == "UPI"  else ""
    cash_amt = amount if payment == "Cash" else ""
    ws.insert_row([len(rows)-2, date, time, category, payment, bank_amt, cash_amt, remarks], len(rows))

def save_expense(category, payment, amount, remarks=""):
    ws   = get_sheet("Expenses")
    now  = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    rows = ws.get_all_values()
    bank_amt   = amount if payment == "UPI"         else ""
    cash_amt   = amount if payment == "Cash"        else ""
    credit_amt = amount if payment == "Credit Card" else ""
    ws.insert_row([len(rows)-2, date, time, category, payment, bank_amt, cash_amt, credit_amt, remarks], len(rows))

def wipe_all():
    for tab in ["Income", "Expenses"]:
        ws   = get_sheet(tab)
        rows = ws.get_all_values()
        if len(rows) > 4:
            ws.delete_rows(5, len(rows))

def kb(rows):
    return InlineKeyboardMarkup(rows)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "👋 *Welcome to Apex Route Logistics Tracker!*\nWhat would you like to do?",
        parse_mode="Markdown",
        reply_markup=kb([[
            InlineKeyboardButton("💰 Add Income",    callback_data="TYPE_Income"),
            InlineKeyboardButton("💸 Add Expense",   callback_data="TYPE_Expense"),
        ],[
            InlineKeyboardButton("🗑 Wipe Test Data", callback_data="WIPE_CONFIRM"),
        ]])
    )

async def btn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "TYPE_Income":
        ctx.user_data.clear()
        ctx.user_data["type"] = "Income"
        rows = []
        for i in range(0, len(INCOME_CATS), 2):
            row = [InlineKeyboardButton(INCOME_CATS[i], callback_data="CAT_"+INCOME_CATS[i])]
            if i+1 < len(INCOME_CATS):
                row.append(InlineKeyboardButton(INCOME_CATS[i+1], callback_data="CAT_"+INCOME_CATS[i+1]))
            rows.append(row)
        await q.message.reply_text("💰 Select *Income Category:*", parse_mode="Markdown", reply_markup=kb(rows))

    elif d == "TYPE_Expense":
        ctx.user_data.clear()
        ctx.user_data["type"] = "Expense"
        rows = []
        for i in range(0, len(EXPENSE_CATS), 2):
            row = [InlineKeyboardButton(EXPENSE_CATS[i], callback_data="CAT_"+EXPENSE_CATS[i])]
            if i+1 < len(EXPENSE_CATS):
                row.append(InlineKeyboardButton(EXPENSE_CATS[i+1], callback_data="CAT_"+EXPENSE_CATS[i+1]))
            rows.append(row)
        await q.message.reply_text("💸 Select *Expense Category:*", parse_mode="Markdown", reply_markup=kb(rows))

    elif d.startswith("CAT_"):
        cat = d.replace("CAT_", "")
        ctx.user_data["category"] = cat
        if cat == "CNG/Petrol":
            pay_btns = kb([[
                InlineKeyboardButton("💳 Credit Card", callback_data="PAY_Credit Card"),
                InlineKeyboardButton("🏦 UPI",         callback_data="PAY_UPI"),
            ],[
                InlineKeyboardButton("💵 Cash",        callback_data="PAY_Cash"),
            ]])
        else:
            pay_btns = kb([[
                InlineKeyboardButton("🏦 UPI",  callback_data="PAY_UPI"),
                InlineKeyboardButton("💵 Cash", callback_data="PAY_Cash"),
            ]])
        await q.message.reply_text(
            f"📂 Category: *{cat}*\nSelect payment method:",
            parse_mode="Markdown", reply_markup=pay_btns
        )

    elif d.startswith("PAY_"):
        payment = d.replace("PAY_", "")
        ctx.user_data["payment"] = payment
        cat      = ctx.user_data.get("category")
        pay_icon = "💳" if payment == "Credit Card" else ("🏦" if payment == "UPI" else "💵")
        await q.message.reply_text(
            f"📂 *{cat}* | {pay_icon} *{payment}*\n\nNow type the *amount* (numbers only):",
            parse_mode="Markdown"
        )

    elif d == "WIPE_CONFIRM":
        await q.message.reply_text(
            "⚠️ *Are you sure?*\nThis will delete ALL entries from Income and Expenses.",
            parse_mode="Markdown",
            reply_markup=kb([[
                InlineKeyboardButton("✅ Yes, Wipe All", callback_data="WIPE_YES"),
                InlineKeyboardButton("❌ Cancel",        callback_data="WIPE_NO"),
            ]])
        )

    elif d == "WIPE_YES":
        try:
            wipe_all()
            await q.message.reply_text("✅ *All test data wiped!* Sheets are clean.\n\nTap /start to begin fresh.", parse_mode="Markdown")
        except Exception as e:
            await q.message.reply_text(f"❌ Error: {str(e)}")

    elif d == "WIPE_NO":
        await q.message.reply_text("Cancelled. Your data is safe! Tap /start to continue.")
        
    elif d == "START_MENU":
        ctx.user_data.clear()
        await q.message.reply_text(
            "👋 *Welcome to Apex Route Logistics Tracker!*\nWhat would you like to do?",
            parse_mode="Markdown",
            reply_markup=kb([[
                InlineKeyboardButton("💰 Add Income",    callback_data="TYPE_Income"),
                InlineKeyboardButton("💸 Add Expense",   callback_data="TYPE_Expense"),
            ],[
                InlineKeyboardButton("🗑 Wipe Test Data", callback_data="WIPE_CONFIRM"),
            ]])
        )

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text       = update.message.text.strip()
    entry_type = ctx.user_data.get("type")
    category   = ctx.user_data.get("category")
    payment    = ctx.user_data.get("payment")

    if not entry_type or not category or not payment:
        await update.message.reply_text("Please tap /start to begin a new entry.")
        return

    # Check if we are waiting for amount or remarks
    if "amount" not in ctx.user_data:
        try:
            amount = float(text)
            if amount <= 0: raise ValueError
            ctx.user_data["amount"] = amount
            
            # Prompt for remarks
            await update.message.reply_text(
                f"✅ Amount saved: *₹{amount:,.0f}*\n\n"
                f"Now type a short **Remark/Note** (e.g. 'Invoice #123' or 'Fuel at HP').\n"
                f"If you don't want to add a note, just type `-` or `skip`.",
                parse_mode="Markdown"
            )
            return

        except ValueError:
            await update.message.reply_text("⚠️ Please enter a valid positive number.\nExample: *1500*", parse_mode="Markdown")
            return
            
    # If we already have amount, this must be remarks
    remarks = text if text.lower() not in ["-", "skip", "no", "none"] else ""
    amount  = ctx.user_data["amount"]

    # Save to sheets
    try:
        await update.message.reply_text("⏳ Saving to Google Sheets...")
        if entry_type == "Income":
            save_income(category, payment, amount, remarks)
        else:
            save_expense(category, payment, amount, remarks)
    except Exception as e:
        await update.message.reply_text(f"❌ Error saving to sheet: {str(e)}\n\nPlease try again.")
        return

    ctx.user_data.clear()
    icon     = "💰" if entry_type == "Income" else "💸"
    pay_icon = "💳" if payment == "Credit Card" else ("🏦" if payment == "UPI" else "💵")
    remark_text = f"\n• Remarks: *{remarks}*" if remarks else ""
    
    await update.message.reply_text(
        f"{icon} *Entry Saved Successfully!*\n\n"
        f"• Type: *{entry_type}*\n"
        f"• Category: *{category}*\n"
        f"• Payment: {pay_icon} *{payment}*\n"
        f"• Amount: *₹{amount:,.0f}*{remark_text}\n\n"
        f"Tap /start to add another entry.",
        parse_mode="Markdown",
        reply_markup=kb([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="START_MENU")]])
    )

def main():
    # Start a small health-check HTTP server on the PORT Render expects
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Apex Route Bot is running!")
        def log_message(self, format, *args):
            pass  # suppress noisy HTTP logs
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Health check server listening on port {port}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Apex Route Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
