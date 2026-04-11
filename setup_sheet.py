#!/usr/bin/env python3
"""
Dreamline Logistics — Google Sheet Professional Setup Script
Theme C: Black · Gold · Crimson

Run once to format all 5 tabs:
  Dashboard | Income | Expenses | Cash & Bank | Monthly Summary

Usage:
  python setup_sheet.py
"""
import os, json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────
SHEET_ID   = os.environ.get("SHEET_ID",   "1bu5fls4crB6nQpLfLQgE3wGCdOdq3mr-9jws5foXctE")
CREDS_JSON = os.environ.get("GOOGLE_CREDS")
CREDS_FILE = "apexroutebot-c4cb3ee13d7d.json"

# ─── THEME C COLORS ────────────────────────────────────────
def rgb(r, g, b): return {"red": r/255, "green": g/255, "blue": b/255}

C_BLACK    = rgb(8,   8,   8)
C_CHARCOAL = rgb(22,  22,  22)
C_DARK1    = rgb(28,  28,  28)
C_DARK2    = rgb(40,  40,  40)
C_GOLD     = rgb(212, 175, 55)
C_GOLD_BG  = rgb(55,  42,  0)
C_CRIMSON  = rgb(139, 0,   0)
C_CRIM_BG  = rgb(90,  0,   0)
C_BLUE_BG  = rgb(0,   50,  120)
C_GREEN_BG = rgb(0,   80,  40)
C_PURP_BG  = rgb(60,  0,   100)
C_WHITE    = rgb(255, 255, 255)
C_GREY     = rgb(150, 150, 150)

def T(size=10, bold=False, color=None, italic=False):
    f = {"fontSize": size, "bold": bold, "italic": italic}
    if color: f["foregroundColor"] = color
    return f

# ─── CONNECT ───────────────────────────────────────────────
def connect():
    if CREDS_JSON:
        info = json.loads(CREDS_JSON)
    else:
        with open(CREDS_FILE) as f:
            info = json.load(f)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds  = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

def ws_get(book, title):
    try:    return book.worksheet(title)
    except: return book.add_worksheet(title=title, rows=1000, cols=26)

# ─── HELPER: SUMPRODUCT for monthly filter ─────────────────
# Dates stored as DD/MM/YYYY text. C2=month, E2=year on Dashboard.
def inc_sum(col):
    """Sum an Income column filtered by Dashboard month+year"""
    return (
        f'=SUMPRODUCT('
        f'(IFERROR(VALUE(MID(Income!B$4:B$2000,4,2)),0)=Dashboard!C$2)*'
        f'(IFERROR(VALUE(RIGHT(Income!B$4:B$2000,4)),0)=Dashboard!E$2)*'
        f'IFERROR(Income!{col}$4:{col}$2000,0))'
    )

def exp_sum(col):
    """Sum an Expenses column filtered by Dashboard month+year"""
    return (
        f'=SUMPRODUCT('
        f'(IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=Dashboard!C$2)*'
        f'(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=Dashboard!E$2)*'
        f'IFERROR(Expenses!{col}$4:{col}$2000,0))'
    )

def inc_cat(cat):
    return (
        f'=SUMPRODUCT('
        f'(IFERROR(VALUE(MID(Income!B$4:B$2000,4,2)),0)=Dashboard!C$2)*'
        f'(IFERROR(VALUE(RIGHT(Income!B$4:B$2000,4)),0)=Dashboard!E$2)*'
        f'(Income!D$4:D$2000="{cat}")*'
        f'(IFERROR(Income!F$4:F$2000,0)+IFERROR(Income!G$4:G$2000,0)))'
    )

def exp_cat(cat):
    return (
        f'=SUMPRODUCT('
        f'(IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=Dashboard!C$2)*'
        f'(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=Dashboard!E$2)*'
        f'(Expenses!D$4:D$2000="{cat}")*'
        f'(IFERROR(Expenses!F$4:F$2000,0)+IFERROR(Expenses!G$4:G$2000,0)+IFERROR(Expenses!H$4:H$2000,0)))'
    )


# ═══════════════════════════════════════════════════════════
# INCOME TAB
# ═══════════════════════════════════════════════════════════
def setup_income(ws):
    print("📥 Setting up Income tab...")
    ws.clear()

    ws.update('A1', [['🚚  DREAMLINE LOGISTICS  —  INCOME TRACKER']])
    ws.merge_cells('A1:H1')
    ws.format('A1:H1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'})

    ws.update('A2', [['Bot entries auto-append before TOTAL row  •  UPI = Bank (₹)  |  Cash = Cash (₹)']])
    ws.merge_cells('A2:H2')
    ws.format('A2:H2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(9, italic=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})

    ws.update('A3:H3', [['#', 'Date', 'Time', 'Category', 'Payment', 'Bank (₹)', 'Cash (₹)', 'Remarks']])
    ws.format('A3:H3', {'backgroundColor': C_DARK1, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F3', {'backgroundColor': C_BLUE_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('G3', {'backgroundColor': C_GREEN_BG, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    # TOTAL row — bot always inserts NEW rows BEFORE this row
    ws.update('A4:H4', [['', 'TOTAL  INCOME', '', '', '',
        '=SUMIF(B4:B10000,"<>TOTAL  INCOME",F4:F10000)',
        '=SUMIF(B4:B10000,"<>TOTAL  INCOME",G4:G10000)', '']])
    ws.merge_cells('B4:E4')
    ws.format('A4:H4', {'backgroundColor': C_GREEN_BG, 'textFormat': T(11, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F4:G4', {'numberFormat': {'type': 'NUMBER', 'pattern': '₹#,##0.00'}})

    ws.freeze(rows=3)
    print("  ✓ Done")


# ═══════════════════════════════════════════════════════════
# EXPENSES TAB
# ═══════════════════════════════════════════════════════════
def setup_expenses(ws):
    print("💸 Setting up Expenses tab...")
    ws.clear()

    ws.update('A1', [['🚚  DREAMLINE LOGISTICS  —  EXPENSE TRACKER']])
    ws.merge_cells('A1:I1')
    ws.format('A1:I1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'})

    ws.update('A2', [['Bot entries auto-append before TOTAL row  •  CNG uses Credit Card  •  UPI = Bank  |  Cash = Cash']])
    ws.merge_cells('A2:I2')
    ws.format('A2:I2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(9, italic=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})

    ws.update('A3:I3', [['#', 'Date', 'Time', 'Category', 'Payment', 'Bank (₹)', 'Cash (₹)', 'Credit Card (₹)', 'Remarks']])
    ws.format('A3:I3', {'backgroundColor': C_DARK1, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F3', {'backgroundColor': C_BLUE_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('G3', {'backgroundColor': C_GREEN_BG, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('H3', {'backgroundColor': C_PURP_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.update('A4:I4', [['', 'TOTAL  EXPENSES', '', '', '',
        '=SUMIF(B4:B10000,"<>TOTAL  EXPENSES",F4:F10000)',
        '=SUMIF(B4:B10000,"<>TOTAL  EXPENSES",G4:G10000)',
        '=SUMIF(B4:B10000,"<>TOTAL  EXPENSES",H4:H10000)', '']])
    ws.merge_cells('B4:E4')
    ws.format('A4:I4', {'backgroundColor': C_CRIM_BG, 'textFormat': T(11, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F4:H4', {'numberFormat': {'type': 'NUMBER', 'pattern': '₹#,##0.00'}})

    ws.freeze(rows=3)
    print("  ✓ Done")


# ═══════════════════════════════════════════════════════════
# DASHBOARD TAB
# ═══════════════════════════════════════════════════════════
def setup_dashboard(ws):
    print("📊 Setting up Dashboard tab...")
    ws.clear()
    now = datetime.now()

    # Row 1: Title
    ws.update('A1', [['🚚  DREAMLINE LOGISTICS  —  FINANCIAL DASHBOARD']])
    ws.merge_cells('A1:H1')
    ws.format('A1:H1', {'backgroundColor': C_BLACK, 'textFormat': T(15, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE'})

    # Row 2: Monthly filter
    ws.update('A2:H2', [['', '📅  FILTER  BY  MONTH:', now.month, '|  YEAR:', now.year, '', 'Change C2 (month 1-12) & E2 (year)', '']])
    ws.format('A2:H2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(10, bold=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})
    ws.format('C2', {'textFormat': T(13, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    ws.format('E2', {'textFormat': T(13, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})

    # Row 3: separator
    ws.format('A3:H3', {'backgroundColor': C_BLACK})

    # Row 4: Metric card headers
    ws.update('B4', [['TOTAL INCOME']])
    ws.update('D4', [['TOTAL EXPENSES']])
    ws.update('F4', [['NET PROFIT']])
    ws.update('H4', [['CASH IN HAND']])
    ws.merge_cells('B4:C4'); ws.merge_cells('D4:E4'); ws.merge_cells('F4:G4')
    ws.format('B4', {'backgroundColor': C_GOLD_BG, 'textFormat': T(9, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    ws.format('D4', {'backgroundColor': C_CRIM_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F4', {'backgroundColor': C_BLUE_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('H4', {'backgroundColor': C_GOLD_BG,  'textFormat': T(9, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'})

    # Row 5: Metric values
    total_inc = f'={inc_sum("F")[1:]}+{inc_sum("G")[1:]}'
    total_exp = f'={exp_sum("F")[1:]}+{exp_sum("G")[1:]}+{exp_sum("H")[1:]}'
    cash_hand  = f'={inc_sum("G")[1:]}-{exp_sum("G")[1:]}'

    ws.update('B5', [[total_inc]], value_input_option='USER_ENTERED')
    ws.update('D5', [[total_exp]], value_input_option='USER_ENTERED')
    ws.update('F5', [['=B5-D5']], value_input_option='USER_ENTERED')
    ws.update('H5', [[cash_hand]], value_input_option='USER_ENTERED')

    ws.merge_cells('B5:C5'); ws.merge_cells('D5:E5'); ws.merge_cells('F5:G5')
    num_fmt = {'numberFormat': {'type': 'NUMBER', 'pattern': '₹#,##0'}}
    ws.format('B5', {**num_fmt, 'backgroundColor': C_GREEN_BG, 'textFormat': T(18, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('D5', {**num_fmt, 'backgroundColor': C_CRIMSON,  'textFormat': T(18, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F5', {**num_fmt, 'backgroundColor': C_BLUE_BG,  'textFormat': T(18, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('H5', {**num_fmt, 'backgroundColor': C_GOLD_BG,  'textFormat': T(18, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'})

    # Row 6: separator
    ws.format('A6:H6', {'backgroundColor': C_BLACK})

    # Row 7: Category section headers
    ws.update('B7', [['INCOME  BY  CATEGORY']]); ws.merge_cells('B7:C7')
    ws.update('E7', [['EXPENSES  BY  CATEGORY']]); ws.merge_cells('E7:H7')
    ws.format('B7', {'backgroundColor': C_GOLD_BG, 'textFormat': T(10, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'})
    ws.format('E7', {'backgroundColor': C_CRIM_BG, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    # Income categories rows 8-10
    income_cats  = ['Vendor/DCO', 'Porter', 'Factory']
    expense_cats = ['CNG/Petrol', 'Maintenance', 'Driver Expense', 'EMI', 'Credit Card Bill', 'Other']

    for i, cat in enumerate(income_cats):
        r = 8 + i
        bg = C_DARK1 if i % 2 == 0 else C_DARK2
        ws.update(f'B{r}', cat)
        ws.update(f'D{r}', [[inc_cat(cat)]], value_input_option='USER_ENTERED')
        ws.format(f'A{r}:D{r}', {'backgroundColor': bg})
        ws.format(f'B{r}', {'textFormat': T(10, bold=True, color=C_GOLD)})
        ws.format(f'D{r}', {**num_fmt, 'textFormat': T(10, bold=False, color=C_WHITE)})

    for i, cat in enumerate(expense_cats):
        r = 8 + i
        bg = C_DARK1 if i % 2 == 0 else C_DARK2
        ws.update(f'E{r}', cat)
        ws.update(f'G{r}', [[exp_cat(cat)]], value_input_option='USER_ENTERED')
        ws.format(f'E{r}:H{r}', {'backgroundColor': bg})
        ws.format(f'E{r}', {'textFormat': T(10, bold=True, color=C_GOLD)})
        ws.format(f'G{r}', {**num_fmt, 'textFormat': T(10, bold=False, color=C_WHITE)})

    # Row 14: separator
    ws.format('A14:H14', {'backgroundColor': C_BLACK})

    # Row 15-16: Bank / Cash / Credit summary
    ws.update('B15', [['BANK BALANCE']]); ws.merge_cells('B15:C15')
    ws.update('D15', [['CASH IN HAND']]); ws.merge_cells('D15:E15')
    ws.update('F15', [['CREDIT CARD DUE']]); ws.merge_cells('F15:G15')
    ws.format('B15', {'backgroundColor': C_BLUE_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('D15', {'backgroundColor': C_GREEN_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F15', {'backgroundColor': C_PURP_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    bank_bal  = f'={inc_sum("F")[1:]}-{exp_sum("F")[1:]}'
    cash_bal  = f'={inc_sum("G")[1:]}-{exp_sum("G")[1:]}'
    credit_due = exp_sum("H")

    ws.update('B16', [[bank_bal]], value_input_option='USER_ENTERED');  ws.merge_cells('B16:C16')
    ws.update('D16', [[cash_bal]], value_input_option='USER_ENTERED');  ws.merge_cells('D16:E16')
    ws.update('F16', [[credit_due]], value_input_option='USER_ENTERED'); ws.merge_cells('F16:G16')
    ws.format('B16', {**num_fmt, 'backgroundColor': C_BLUE_BG,  'textFormat': T(14, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('D16', {**num_fmt, 'backgroundColor': C_GREEN_BG, 'textFormat': T(14, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('F16', {**num_fmt, 'backgroundColor': C_PURP_BG,  'textFormat': T(14, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.freeze(rows=1)
    print("  ✓ Done")


# ═══════════════════════════════════════════════════════════
# CASH & BANK TAB
# ═══════════════════════════════════════════════════════════
def setup_cash_bank(ws):
    print("🏦 Setting up Cash & Bank tab...")
    ws.clear()

    ws.update('A1', [['🚚  DREAMLINE LOGISTICS  —  CASH & BANK TRACKER']])
    ws.merge_cells('A1:F1')
    ws.format('A1:F1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})

    ws.update('A2', [['All-time running totals  (not month-filtered)']])
    ws.merge_cells('A2:F2')
    ws.format('A2:F2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(9, italic=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})

    # Headers row 4
    labels = [['TOTAL INCOME', '', 'TOTAL EXPENSES', '', 'NET PROFIT', '']]
    ws.update('A4:F4', labels)
    ws.merge_cells('A4:B4'); ws.merge_cells('C4:D4'); ws.merge_cells('E4:F4')
    ws.format('A4', {'backgroundColor': C_GREEN_BG, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('C4', {'backgroundColor': C_CRIM_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('E4', {'backgroundColor': C_BLUE_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    # Values row 5 (ALL-TIME, no filter)
    all_inc = "=SUM(Income!F4:F10000)+SUM(Income!G4:G10000)"
    all_exp = "=SUM(Expenses!F4:F10000)+SUM(Expenses!G4:G10000)+SUM(Expenses!H4:H10000)"
    num_fmt = {'numberFormat': {'type': 'NUMBER', 'pattern': '₹#,##0'}}
    ws.update('A5', [[all_inc]], value_input_option='USER_ENTERED'); ws.merge_cells('A5:B5')
    ws.update('C5', [[all_exp]], value_input_option='USER_ENTERED'); ws.merge_cells('C5:D5')
    ws.update('E5', [['=A5-C5']], value_input_option='USER_ENTERED'); ws.merge_cells('E5:F5')
    ws.format('A5', {**num_fmt, 'backgroundColor': C_GREEN_BG, 'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('C5', {**num_fmt, 'backgroundColor': C_CRIM_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('E5', {**num_fmt, 'backgroundColor': C_BLUE_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.format('A6:F6', {'backgroundColor': C_BLACK})

    # Bank / Cash / Credit breakdown row 8-9
    ws.update('A8', [['BANK ACCOUNT']]);  ws.merge_cells('A8:B8')
    ws.update('C8', [['CASH IN HAND']]);  ws.merge_cells('C8:D8')
    ws.update('E8', [['CREDIT CARD DUE']]);ws.merge_cells('E8:F8')
    ws.format('A8', {'backgroundColor': C_BLUE_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('C8', {'backgroundColor': C_GREEN_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('E8', {'backgroundColor': C_PURP_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.update('A9', [['=SUM(Income!F4:F10000)-SUM(Expenses!F4:F10000)']], value_input_option='USER_ENTERED'); ws.merge_cells('A9:B9')
    ws.update('C9', [['=SUM(Income!G4:G10000)-SUM(Expenses!G4:G10000)']], value_input_option='USER_ENTERED'); ws.merge_cells('C9:D9')
    ws.update('E9', [['=SUM(Expenses!H4:H10000)']], value_input_option='USER_ENTERED'); ws.merge_cells('E9:F9')
    ws.format('A9', {**num_fmt, 'backgroundColor': C_BLUE_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('C9', {**num_fmt, 'backgroundColor': C_GREEN_BG, 'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('E9', {**num_fmt, 'backgroundColor': C_PURP_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.freeze(rows=1)
    print("  ✓ Done")


# ═══════════════════════════════════════════════════════════
# MONTHLY SUMMARY TAB
# ═══════════════════════════════════════════════════════════
def setup_monthly_summary(ws):
    print("📅 Setting up Monthly Summary tab...")
    ws.clear()

    ws.update('A1', [['🚚  DREAMLINE LOGISTICS  —  MONTHLY SUMMARY']])
    ws.merge_cells('A1:H1')
    ws.format('A1:H1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})

    ws.update('A3:H3', [['Month', 'Year', 'Total Income', 'Total Expenses', 'Net Profit', 'Bank Bal', 'Cash Bal', 'Credit Due']])
    ws.format('A3:H3', {'backgroundColor': C_DARK1, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    ws.format('C3', {'backgroundColor': C_GREEN_BG})
    ws.format('D3', {'backgroundColor': C_CRIM_BG})
    ws.format('E3', {'backgroundColor': C_BLUE_BG})
    ws.format('F3', {'backgroundColor': C_BLUE_BG})
    ws.format('G3', {'backgroundColor': C_GREEN_BG})
    ws.format('H3', {'backgroundColor': C_PURP_BG})

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    num_fmt = {'numberFormat': {'type': 'NUMBER', 'pattern': '₹#,##0'}}
    now = datetime.now()
    row = 4

    for year in [now.year - 1, now.year, now.year + 1]:
        for m_num, m_name in enumerate(months, 1):
            def mf(sheet, col):
                return (
                    f'=SUMPRODUCT('
                    f'(IFERROR(VALUE(MID({sheet}!B$4:B$2000,4,2)),0)={m_num})*'
                    f'(IFERROR(VALUE(RIGHT({sheet}!B$4:B$2000,4)),0)={year})*'
                    f'IFERROR({sheet}!{col}$4:{col}$2000,0))'
                )
            inc = f'={mf("Income","F")[1:]}+{mf("Income","G")[1:]}'
            exp = f'={mf("Expenses","F")[1:]}+{mf("Expenses","G")[1:]}+{mf("Expenses","H")[1:]}'
            bank = f'={mf("Income","F")[1:]}-{mf("Expenses","F")[1:]}'
            cash = f'={mf("Income","G")[1:]}-{mf("Expenses","G")[1:]}'
            cred = mf("Expenses", "H")

            ws.update(f'A{row}', m_name)
            ws.update(f'B{row}', year)
            ws.update(f'C{row}', [[inc]],  value_input_option='USER_ENTERED')
            ws.update(f'D{row}', [[exp]],  value_input_option='USER_ENTERED')
            ws.update(f'E{row}', [[f'=C{row}-D{row}']], value_input_option='USER_ENTERED')
            ws.update(f'F{row}', [[bank]], value_input_option='USER_ENTERED')
            ws.update(f'G{row}', [[cash]], value_input_option='USER_ENTERED')
            ws.update(f'H{row}', [[cred]], value_input_option='USER_ENTERED')

            bg = C_DARK1 if m_num % 2 == 0 else C_DARK2
            if m_num == now.month and year == now.year:
                bg = C_GOLD_BG  # highlight current month

            ws.format(f'A{row}:H{row}', {'backgroundColor': bg, 'textFormat': T(10, color=C_WHITE)})
            ws.format(f'A{row}:B{row}', {'textFormat': T(10, bold=True, color=C_GOLD)})
            ws.format(f'C{row}:H{row}', num_fmt)
            row += 1

    ws.freeze(rows=3)
    print("  ✓ Done")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 Connecting to Google Sheets...")
    book = connect()
    print(f"   ✓ Connected: {book.title}\n")

    setup_dashboard(  ws_get(book, "Dashboard"))
    setup_income(     ws_get(book, "Income"))
    setup_expenses(   ws_get(book, "Expenses"))
    setup_cash_bank(  ws_get(book, "Cash & Bank"))
    setup_monthly_summary(ws_get(book, "Monthly Summary"))

    print("\n✅ All tabs set up successfully!")
    print("📌 Reminder: On the Dashboard, change C2 (month) and E2 (year) to filter by month.")
