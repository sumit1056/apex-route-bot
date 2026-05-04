import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client

# Environment Variables
BOT_TOKEN    = os.environ.get("BOT_TOKEN", "7638823484:AAHHmbuhhYKmc_QFZZvLe7hf4GlYvWDTw3Y")
SUPABASE_URL  = os.environ.get("SUPABASE_URL", "https://dlkgqtuucwflmsakacln.supabase.co")
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsa2dxdHV1Y3dmbG1zYWthY2xuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzg5Mjg0OCwiZXhwIjoyMDkzNDY4ODQ4fQ.Cx2VeTIee_thOOaIvnqpwkQzW-GwgKuugT400l09duA")

INCOME_CATS  = ["Vendor/DCO", "Porter", "Factory"]
EXPENSE_CATS = ["CNG/Petrol", "Maintenance", "Driver Expense", "EMI", "Credit Card Bill", "Other"]

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_entry(entry_type, category, payment, amount, remarks=""):
    now  = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    
    bank_amt   = float(amount) if payment == "UPI"         else 0.0
    cash_amt   = float(amount) if payment == "Cash"        else 0.0
    credit_amt = float(amount) if payment == "Credit Card" else 0.0
    
    data = {
        "date": date,
        "time": time,
        "type": entry_type,
        "category": category,
        "payment_method": payment,
        "bank_amount": bank_amt,
        "cash_amount": cash_amt,
        "credit_amount": credit_amt,
        "remarks": remarks
    }
    
    supabase.table("entries").insert(data).execute()

def wipe_all():
    # Deleting all rows (caution: this is for testing/wipe command)
    supabase.table("entries").delete().neq("id", 0).execute()

def kb(rows):
    return InlineKeyboardMarkup(rows)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "👋 *Welcome to Dreamline Logistics Tracker!*\nWhat would you like to do?",
        parse_mode="Markdown",
        reply_markup=kb([[
            InlineKeyboardButton("💰 Add Income",    callback_data="TYPE_Income"),
            InlineKeyboardButton("💸 Add Expense",   callback_data="TYPE_Expense"),
        ],[
            InlineKeyboardButton("🗑 Wipe All Data", callback_data="WIPE_CONFIRM"),
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
        if cat == "CNG/Petrol" or ctx.user_data.get("type") == "Expense":
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
            "⚠️ *Are you sure?*\nThis will delete ALL entries from the database.",
            parse_mode="Markdown",
            reply_markup=kb([[
                InlineKeyboardButton("✅ Yes, Wipe All", callback_data="WIPE_YES"),
                InlineKeyboardButton("❌ Cancel",        callback_data="WIPE_NO"),
            ]])
        )

    elif d == "WIPE_YES":
        try:
            wipe_all()
            await q.message.reply_text("✅ *All data wiped!* Database is clean.\n\nTap /start to begin fresh.", parse_mode="Markdown")
        except Exception as e:
            await q.message.reply_text(f"❌ Error: {str(e)}")

    elif d == "WIPE_NO":
        await q.message.reply_text("Cancelled. Your data is safe! Tap /start to continue.")
        
    elif d == "START_MENU":
        ctx.user_data.clear()
        await q.message.reply_text(
            "👋 *Welcome to Dreamline Logistics Tracker!*\nWhat would you like to do?",
            parse_mode="Markdown",
            reply_markup=kb([[
                InlineKeyboardButton("💰 Add Income",    callback_data="TYPE_Income"),
                InlineKeyboardButton("💸 Add Expense",   callback_data="TYPE_Expense"),
            ],[
                InlineKeyboardButton("🗑 Wipe All Data", callback_data="WIPE_CONFIRM"),
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

    if "amount" not in ctx.user_data:
        try:
            amount = float(text)
            if amount <= 0: raise ValueError
            ctx.user_data["amount"] = amount
            await update.message.reply_text(
                f"✅ Amount saved: *₹{amount:,.0f}*\n\n"
                f"Now type a short **Remark/Note**.\n"
                f"If you don't want to add a note, just type `-` or `skip`.",
                parse_mode="Markdown"
            )
            return
        except ValueError:
            await update.message.reply_text("⚠️ Please enter a valid positive number.", parse_mode="Markdown")
            return
            
    remarks = text if text.lower() not in ["-", "skip", "no", "none"] else ""
    amount  = ctx.user_data["amount"]

    try:
        await update.message.reply_text("⏳ Saving to Supabase...")
        save_entry(entry_type, category, payment, amount, remarks)
    except Exception as e:
        await update.message.reply_text(f"❌ Error saving to database: {str(e)}\n\nPlease try again.")
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
    # Only start health check server if SKIP_HEALTH_CHECK is not set
    if not os.environ.get("SKIP_HEALTH_CHECK"):
        port = int(os.environ.get("PORT", 10000))
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Dreamline Logistics Bot is running!")
            def log_message(self, format, *args): pass
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"Health check server started on port {port}")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Dreamline Logistics Bot is running with Supabase...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
