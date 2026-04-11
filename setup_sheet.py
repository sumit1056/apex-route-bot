#!/usr/bin/env python3
"""
Dreamline Logistics -- Google Sheet Professional Setup Script
Theme C: Black, Gold, Crimson

Run once to build all 5 tabs:
  Dashboard | Income | Expenses | Cash & Bank | Monthly Summary

Usage:
  python setup_sheet.py
"""
import os, json, time
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# CONFIG
SHEET_ID   = os.environ.get("SHEET_ID",   "1bu5fls4crB6nQpLfLQgE3wGCdOdq3mr-9jws5foXctE")
CREDS_JSON = os.environ.get("GOOGLE_CREDS")
CREDS_FILE = "apexroutebot-c4cb3ee13d7d.json"

# THEME C COLORS
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

def up(ws, rng, val):
    """Single cell/range update with automatic retry on 429."""
    for attempt in range(5):
        try:
            ws.update(val if isinstance(val, list) else [[val]], range_name=rng)
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                print(f"  Rate limit hit, waiting 30s...")
                time.sleep(30)
            else:
                raise

def upf(ws, rng, formula):
    """Formula update with retry."""
    for attempt in range(5):
        try:
            ws.update([[formula]], range_name=rng, value_input_option='USER_ENTERED')
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                print(f"  Rate limit hit, waiting 30s...")
                time.sleep(30)
            else:
                raise

def fmt(ws, rng, style):
    """Format with retry."""
    for attempt in range(5):
        try:
            ws.format(rng, style)
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                print(f"  Rate limit hit, waiting 30s...")
                time.sleep(30)
            else:
                raise

def b_up(ws, data, opts=None):
    """Batch update with retry."""
    for attempt in range(5):
        try:
            if opts: ws.batch_update(data, value_input_option=opts)
            else:    ws.batch_update(data)
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                print(f"  Rate limit hit, waiting 30s...")
                time.sleep(30)
            else:
                raise

def mrg(ws, rng):
    """Merge with retry."""
    for attempt in range(5):
        try:
            ws.merge_cells(rng)
            return
        except gspread.exceptions.APIError as e:
            if '429' in str(e):
                print(f"  Rate limit hit, waiting 30s...")
                time.sleep(30)
            else:
                raise


# =========================================================
# INCOME TAB
# =========================================================
def setup_income(ws):
    print("[Income] Setting up Income tab...")
    ws.clear(); time.sleep(2)

    ws.batch_update([
        {'range': 'A1',    'values': [['DREAMLINE LOGISTICS -- INCOME TRACKER']]},
        {'range': 'A2',    'values': [['Bot entries auto-append before TOTAL row  |  UPI = Bank  |  Cash = Cash']]},
        {'range': 'A3:H3', 'values': [['#', 'Date', 'Time', 'Category', 'Payment', 'Bank (Rs)', 'Cash (Rs)', 'Remarks']]},
        {'range': 'A4:H4', 'values': [['', 'TOTAL  INCOME', '', '', '',
            '=SUMIF(B4:B10000,"<>TOTAL  INCOME",F4:F10000)',
            '=SUMIF(B4:B10000,"<>TOTAL  INCOME",G4:G10000)', '']]},
    ], value_input_option='USER_ENTERED')
    time.sleep(3)

    mrg(ws, 'A1:H1'); mrg(ws, 'A2:H2'); mrg(ws, 'B4:E4')
    time.sleep(3)

    fmt(ws, 'A1:H1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A2:H2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(9, italic=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A3:H3', {'backgroundColor': C_DARK1, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F3', {'backgroundColor': C_BLUE_BG,  'textFormat': T(10, bold=True, color=C_WHITE)})
    fmt(ws, 'G3', {'backgroundColor': C_GREEN_BG, 'textFormat': T(10, bold=True, color=C_WHITE)})
    fmt(ws, 'A4:H4', {'backgroundColor': C_GREEN_BG, 'textFormat': T(11, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F4:G4', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0.00'}})

    ws.freeze(rows=3)
    print("  Done!")


# =========================================================
# EXPENSES TAB
# =========================================================
def setup_expenses(ws):
    print("[Expenses] Setting up Expenses tab...")
    ws.clear(); time.sleep(2)

    ws.batch_update([
        {'range': 'A1',    'values': [['DREAMLINE LOGISTICS -- EXPENSE TRACKER']]},
        {'range': 'A2',    'values': [['Bot entries auto-append before TOTAL row  |  UPI = Bank  |  Cash = Cash  |  CNG = Credit Card']]},
        {'range': 'A3:I3', 'values': [['#', 'Date', 'Time', 'Category', 'Payment', 'Bank (Rs)', 'Cash (Rs)', 'Credit Card (Rs)', 'Remarks']]},
        {'range': 'A4:I4', 'values': [['', 'TOTAL  EXPENSES', '', '', '',
            '=SUMIF(B4:B10000,"<>TOTAL  EXPENSES",F4:F10000)',
            '=SUMIF(B4:B10000,"<>TOTAL  EXPENSES",G4:G10000)',
            '=SUMIF(B4:B10000,"<>TOTAL  EXPENSES",H4:H10000)', '']]},
    ], value_input_option='USER_ENTERED')
    time.sleep(3)

    mrg(ws, 'A1:I1'); mrg(ws, 'A2:I2'); mrg(ws, 'B4:E4')
    time.sleep(3)

    fmt(ws, 'A1:I1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A2:I2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(9, italic=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A3:I3', {'backgroundColor': C_DARK1, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F3', {'backgroundColor': C_BLUE_BG,  'textFormat': T(10, bold=True, color=C_WHITE)})
    fmt(ws, 'G3', {'backgroundColor': C_GREEN_BG, 'textFormat': T(10, bold=True, color=C_WHITE)})
    fmt(ws, 'H3', {'backgroundColor': C_PURP_BG,  'textFormat': T(10, bold=True, color=C_WHITE)})
    fmt(ws, 'A4:I4', {'backgroundColor': C_CRIM_BG, 'textFormat': T(11, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F4:H4', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0.00'}})

    ws.freeze(rows=3)
    print("  Done!")


# =========================================================
# DASHBOARD TAB
# =========================================================
def setup_dashboard(ws):
    print("[Dashboard] Setting up Dashboard tab...")
    ws.clear(); time.sleep(2)
    now = datetime.now()

    income_cats  = ['Vendor/DCO', 'Porter', 'Factory']
    expense_cats = ['CNG/Petrol', 'Maintenance', 'Driver Expense', 'EMI', 'Credit Card Bill', 'Other']

    def ic(cat):
        return f'=SUMPRODUCT((IFERROR(VALUE(MID(Income!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Income!B$4:B$2000,4)),0)=E2)*(Income!D$4:D$2000="{cat}")*(IFERROR(Income!F$4:F$2000,0)+IFERROR(Income!G$4:G$2000,0)))'
    def ec(cat):
        return f'=SUMPRODUCT((IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=E2)*(Expenses!D$4:D$2000="{cat}")*(IFERROR(Expenses!F$4:F$2000,0)+IFERROR(Expenses!G$4:G$2000,0)+IFERROR(Expenses!H$4:H$2000,0)))'

    total_inc  = '=SUMPRODUCT((IFERROR(VALUE(MID(Income!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Income!B$4:B$2000,4)),0)=E2)*(IFERROR(Income!F$4:F$2000,0)+IFERROR(Income!G$4:G$2000,0)))'
    total_exp  = '=SUMPRODUCT((IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=E2)*(IFERROR(Expenses!F$4:F$2000,0)+IFERROR(Expenses!G$4:G$2000,0)+IFERROR(Expenses!H$4:H$2000,0)))'
    cash_hand  = '=SUMPRODUCT((IFERROR(VALUE(MID(Income!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Income!B$4:B$2000,4)),0)=E2)*IFERROR(Income!G$4:G$2000,0))-SUMPRODUCT((IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=E2)*IFERROR(Expenses!G$4:G$2000,0))'
    bank_bal   = '=SUMPRODUCT((IFERROR(VALUE(MID(Income!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Income!B$4:B$2000,4)),0)=E2)*IFERROR(Income!F$4:F$2000,0))-SUMPRODUCT((IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=E2)*IFERROR(Expenses!F$4:F$2000,0))'
    credit_due = '=SUMPRODUCT((IFERROR(VALUE(MID(Expenses!B$4:B$2000,4,2)),0)=C2)*(IFERROR(VALUE(RIGHT(Expenses!B$4:B$2000,4)),0)=E2)*IFERROR(Expenses!H$4:H$2000,0))'

    # All text: ONE call
    ws.batch_update([
        {'range': 'A1',    'values': [['DREAMLINE LOGISTICS -- FINANCIAL DASHBOARD']]},
        {'range': 'A2:H2', 'values': [['', 'FILTER BY MONTH:', now.month, '| YEAR:', now.year, '', 'Change C2 (1-12) & E2 (year)', '']]},
        {'range': 'B4', 'values': [['TOTAL INCOME']]},   {'range': 'D4', 'values': [['TOTAL EXPENSES']]},
        {'range': 'F4', 'values': [['NET PROFIT']]},     {'range': 'H4', 'values': [['CASH IN HAND']]},
        {'range': 'B7', 'values': [['INCOME BY CATEGORY']]}, {'range': 'E7', 'values': [['EXPENSES BY CATEGORY']]},
        {'range': 'B8',  'values': [[income_cats[0]]]},  {'range': 'B9',  'values': [[income_cats[1]]]},
        {'range': 'B10', 'values': [[income_cats[2]]]},
        {'range': 'E8',  'values': [[expense_cats[0]]]}, {'range': 'E9',  'values': [[expense_cats[1]]]},
        {'range': 'E10', 'values': [[expense_cats[2]]]}, {'range': 'E11', 'values': [[expense_cats[3]]]},
        {'range': 'E12', 'values': [[expense_cats[4]]]}, {'range': 'E13', 'values': [[expense_cats[5]]]},
        {'range': 'B15', 'values': [['BANK BALANCE']]},  {'range': 'D15', 'values': [['CASH IN HAND']]},
        {'range': 'F15', 'values': [['CREDIT CARD DUE']]},
    ])
    time.sleep(3)

    # All formulas: ONE call
    ws.batch_update([
        {'range': 'B5', 'values': [[total_inc]]},  {'range': 'D5', 'values': [[total_exp]]},
        {'range': 'F5', 'values': [['=B5-D5']]},   {'range': 'H5', 'values': [[cash_hand]]},
        {'range': 'D8',  'values': [[ic(income_cats[0])]]},  {'range': 'D9',  'values': [[ic(income_cats[1])]]},
        {'range': 'D10', 'values': [[ic(income_cats[2])]]},
        {'range': 'G8',  'values': [[ec(expense_cats[0])]]}, {'range': 'G9',  'values': [[ec(expense_cats[1])]]},
        {'range': 'G10', 'values': [[ec(expense_cats[2])]]}, {'range': 'G11', 'values': [[ec(expense_cats[3])]]},
        {'range': 'G12', 'values': [[ec(expense_cats[4])]]}, {'range': 'G13', 'values': [[ec(expense_cats[5])]]},
        {'range': 'B16', 'values': [[bank_bal]]},  {'range': 'D16', 'values': [[cash_hand]]},
        {'range': 'F16', 'values': [[credit_due]]},
    ], value_input_option='USER_ENTERED')
    time.sleep(3)

    # Merges
    for rng in ['A1:H1','B4:C4','D4:E4','F4:G4','B5:C5','D5:E5','F5:G5',
                'B7:C7','E7:H7','B15:C15','D15:E15','F15:G15','B16:C16','D16:E16','F16:G16']:
        mrg(ws, rng); time.sleep(0.5)
    time.sleep(3)

    # Formatting
    nf = {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}
    fmt(ws, 'A1:H1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A2:H2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(10, color=C_GREY), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'C2', {'textFormat': T(12, bold=True, color=C_GOLD)}); time.sleep(1)
    fmt(ws, 'E2', {'textFormat': T(12, bold=True, color=C_GOLD)})
    fmt(ws, 'A3:H3', {'backgroundColor': C_BLACK})
    fmt(ws, 'B4', {'backgroundColor': C_GOLD_BG, 'textFormat': T(9, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'})
    fmt(ws, 'D4', {'backgroundColor': C_CRIM_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F4', {'backgroundColor': C_BLUE_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'H4', {'backgroundColor': C_GOLD_BG, 'textFormat': T(9, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'}); time.sleep(3)
    fmt(ws, 'B5', {**nf, 'backgroundColor': C_GREEN_BG, 'textFormat': T(18, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'D5', {**nf, 'backgroundColor': C_CRIM_BG,  'textFormat': T(18, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F5', {**nf, 'backgroundColor': C_BLUE_BG,  'textFormat': T(18, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'H5', {**nf, 'backgroundColor': C_GOLD_BG,  'textFormat': T(18, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A6:H6', {'backgroundColor': C_BLACK}); time.sleep(3)
    fmt(ws, 'B7', {'backgroundColor': C_GOLD_BG, 'textFormat': T(10, bold=True, color=C_GOLD),  'horizontalAlignment': 'CENTER'})
    fmt(ws, 'E7', {'backgroundColor': C_CRIM_BG, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    for i in range(3):
        r = 8 + i; bg = C_DARK1 if i % 2 == 0 else C_DARK2
        fmt(ws, f'A{r}:D{r}', {'backgroundColor': bg}); time.sleep(1)
        fmt(ws, f'B{r}', {'textFormat': T(10, bold=True, color=C_GOLD)}); time.sleep(1)
        fmt(ws, f'D{r}', {**nf, 'textFormat': T(10, color=C_WHITE)}); time.sleep(1)
    for i in range(6):
        r = 8 + i; bg = C_DARK1 if i % 2 == 0 else C_DARK2
        fmt(ws, f'E{r}:H{r}', {'backgroundColor': bg}); time.sleep(1)
        fmt(ws, f'E{r}', {'textFormat': T(10, bold=True, color=C_GOLD)}); time.sleep(1)
        fmt(ws, f'G{r}', {**nf, 'textFormat': T(10, color=C_WHITE)}); time.sleep(1)
    time.sleep(3)
    fmt(ws, 'A14:H14', {'backgroundColor': C_BLACK})
    fmt(ws, 'B15', {'backgroundColor': C_BLUE_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'D15', {'backgroundColor': C_GREEN_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F15', {'backgroundColor': C_PURP_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'B16', {**nf, 'backgroundColor': C_BLUE_BG,  'textFormat': T(14, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'D16', {**nf, 'backgroundColor': C_GREEN_BG, 'textFormat': T(14, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'F16', {**nf, 'backgroundColor': C_PURP_BG,  'textFormat': T(14, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.freeze(rows=1)
    print("  Done!")


# =========================================================
# CASH & BANK TAB
# =========================================================
def setup_cash_bank(ws):
    print("[CashBank] Setting up Cash & Bank tab...")
    ws.clear(); time.sleep(2)

    all_inc = "=SUM(Income!F4:F10000)+SUM(Income!G4:G10000)"
    all_exp = "=SUM(Expenses!F4:F10000)+SUM(Expenses!G4:G10000)+SUM(Expenses!H4:H10000)"

    b_up(ws, [
        {'range': 'A1',    'values': [['DREAMLINE LOGISTICS -- CASH & BANK TRACKER']]},
        {'range': 'A2',    'values': [['All-time running totals (not month-filtered)']]},
        {'range': 'A4:F4', 'values': [['TOTAL INCOME', '', 'TOTAL EXPENSES', '', 'NET PROFIT', '']]},
        {'range': 'A8:F8', 'values': [['BANK ACCOUNT', '', 'CASH IN HAND', '', 'CREDIT CARD DUE', '']]},
    ])
    ws.batch_update([
        {'range': 'A5', 'values': [[all_inc]]},
        {'range': 'C5', 'values': [[all_exp]]},
        {'range': 'E5', 'values': [['=A5-C5']]},
        {'range': 'A9', 'values': [['=SUM(Income!F4:F10000)-SUM(Expenses!F4:F10000)']]},
        {'range': 'C9', 'values': [['=SUM(Income!G4:G10000)-SUM(Expenses!G4:G10000)']]},
        {'range': 'E9', 'values': [['=SUM(Expenses!H4:H10000)']]},
    ], value_input_option='USER_ENTERED')
    time.sleep(3)

    for rng in ['A1:F1','A2:F2','A4:B4','C4:D4','E4:F4','A5:B5','C5:D5','E5:F5',
                'A8:B8','C8:D8','E8:F8','A9:B9','C9:D9','E9:F9']:
        mrg(ws, rng); time.sleep(0.4)
    time.sleep(3)

    nf = {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}
    fmt(ws, 'A1:F1', {'backgroundColor': C_BLACK,    'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A2:F2', {'backgroundColor': C_CHARCOAL, 'textFormat': T(9, italic=True, color=C_GREY), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A4', {'backgroundColor': C_GREEN_BG, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'C4', {'backgroundColor': C_CRIM_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'E4', {'backgroundColor': C_BLUE_BG,  'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'}); time.sleep(3)
    fmt(ws, 'A5', {**nf, 'backgroundColor': C_GREEN_BG, 'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'C5', {**nf, 'backgroundColor': C_CRIM_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'E5', {**nf, 'backgroundColor': C_BLUE_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A6:F6', {'backgroundColor': C_BLACK}); time.sleep(3)
    fmt(ws, 'A8', {'backgroundColor': C_BLUE_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'C8', {'backgroundColor': C_GREEN_BG, 'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'E8', {'backgroundColor': C_PURP_BG,  'textFormat': T(9, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A9', {**nf, 'backgroundColor': C_BLUE_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'C9', {**nf, 'backgroundColor': C_GREEN_BG, 'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'E9', {**nf, 'backgroundColor': C_PURP_BG,  'textFormat': T(16, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})

    ws.freeze(rows=1)
    print("  Done!")


# =========================================================
# MONTHLY SUMMARY TAB
# =========================================================
def setup_monthly_summary(ws):
    print("[Monthly] Setting up Monthly Summary tab (takes ~3 min)...")
    ws.clear(); time.sleep(2)

    b_up(ws, [
        {'range': 'A1',    'values': [['DREAMLINE LOGISTICS -- MONTHLY SUMMARY']]},
        {'range': 'A3:H3', 'values': [['Month', 'Year', 'Total Income', 'Total Expenses', 'Net Profit', 'Bank Bal', 'Cash Bal', 'Credit Due']]},
    ])
    mrg(ws, 'A1:H1'); time.sleep(2)

    fmt(ws, 'A1:H1', {'backgroundColor': C_BLACK, 'textFormat': T(14, bold=True, color=C_GOLD), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'A3:H3', {'backgroundColor': C_DARK1, 'textFormat': T(10, bold=True, color=C_WHITE), 'horizontalAlignment': 'CENTER'})
    fmt(ws, 'C3', {'backgroundColor': C_GREEN_BG}); fmt(ws, 'D3', {'backgroundColor': C_CRIM_BG})
    fmt(ws, 'E3', {'backgroundColor': C_BLUE_BG});  fmt(ws, 'F3', {'backgroundColor': C_BLUE_BG})
    fmt(ws, 'G3', {'backgroundColor': C_GREEN_BG}); fmt(ws, 'H3', {'backgroundColor': C_PURP_BG})
    time.sleep(3)

    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    nf = {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}
    now = datetime.now()
    row = 4

    b_text = []
    b_form = []

    for year in [now.year - 1, now.year, now.year + 1]:
        for m_num, m_name in enumerate(months, 1):
            def mf(sheet, col, mn=m_num, yr=year):
                return f'=SUMPRODUCT((IFERROR(VALUE(MID({sheet}!B$4:B$2000,4,2)),0)={mn})*(IFERROR(VALUE(RIGHT({sheet}!B$4:B$2000,4)),0)={yr})*IFERROR({sheet}!{col}$4:{col}$2000,0))'

            row_text = [[m_name, year]]
            row_formulas = [
                [f'={mf("Income","F")[1:]}+{mf("Income","G")[1:]}'],
                [f'={mf("Expenses","F")[1:]}+{mf("Expenses","G")[1:]}+{mf("Expenses","H")[1:]}'],
                [f'=C{row}-D{row}'],
                [f'={mf("Income","F")[1:]}-{mf("Expenses","F")[1:]}'],
                [f'={mf("Income","G")[1:]}-{mf("Expenses","G")[1:]}'],
                [mf("Expenses","H")],
            ]

            b_text.append({'range': f'A{row}:B{row}', 'values': [row_text[0]]})
            b_form.extend([
                {'range': f'C{row}', 'values': [row_formulas[0]]},
                {'range': f'D{row}', 'values': [row_formulas[1]]},
                {'range': f'E{row}', 'values': [row_formulas[2]]},
                {'range': f'F{row}', 'values': [row_formulas[3]]},
                {'range': f'G{row}', 'values': [row_formulas[4]]},
                {'range': f'H{row}', 'values': [row_formulas[5]]},
            ])

            row += 1

    b_up(ws, b_text)
    time.sleep(3)
    b_up(ws, b_form, opts='USER_ENTERED')
    time.sleep(3)

    # Do formats in a loop after values since we can't batch_format easily
    row = 4
    for year in [now.year - 1, now.year, now.year + 1]:
        for m_num, m_name in enumerate(months, 1):
            bg = C_GOLD_BG if (m_num == now.month and year == now.year) else (C_DARK1 if m_num % 2 == 0 else C_DARK2)
            fmt(ws, f'A{row}:H{row}', {'backgroundColor': bg, 'textFormat': T(10, color=C_WHITE)})
            fmt(ws, f'A{row}:B{row}', {'textFormat': T(10, bold=True, color=C_GOLD)})
            fmt(ws, f'C{row}:H{row}', nf)
            row += 1


    ws.freeze(rows=3)
    print("  Done!")


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    print("[START] Connecting to Google Sheets...")
    book = connect()
    print(f"  Connected: {book.title}\n")

    print("Setting up Dashboard (1/5)...")
    setup_dashboard(ws_get(book, "Dashboard"))
    time.sleep(10)

    print("Setting up Income (2/5)...")
    setup_income(ws_get(book, "Income"))
    time.sleep(10)

    print("Setting up Expenses (3/5)...")
    setup_expenses(ws_get(book, "Expenses"))
    time.sleep(10)

    print("Setting up Cash & Bank (4/5)...")
    setup_cash_bank(ws_get(book, "Cash & Bank"))
    time.sleep(10)

    print("Setting up Monthly Summary (5/5) - This takes ~3 minutes...")
    setup_monthly_summary(ws_get(book, "Monthly Summary"))

    print("\n[DONE] All tabs set up successfully!")
    print("[NOTE] On the Dashboard, change C2 (month 1-12) and E2 (year) to filter.")
