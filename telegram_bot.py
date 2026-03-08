# -*- coding: utf-8 -*-
"""
Telegram Bot 互動模組
"""

import requests
import json
from data.fetcher import StockDataFetcher
from data.database import DatabaseManager

# Telegram 設定
TELEGRAM_BOT_TOKEN = "8294937993:AAFOY_rwU33p6ndhFrnDyjKFrSQ-_1KavOE"
TELEGRAM_CHAT_ID = "8137433836"

fetcher = StockDataFetcher()
db = DatabaseManager()

def send_message(text, parse_mode="Markdown"):
    """發送訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.json()
    except Exception as e:
        print(f"發送失敗: {e}")
        return None

def generate_portfolio_keyboard():
    """生成持股鍵盤"""
    portfolio = db.get_portfolio()
    buttons = []
    for p in portfolio:
        text = f"{p['code']} {p['name']}"
        buttons.append([{"text": text, "callback_data": f"portfolio_{p['code']}"}])
    
    keyboard = {"inline_keyboard": buttons}
    return json.dumps(keyboard)

def generate_watchlist_keyboard():
    """生成觀察名單鍵盤"""
    watchlist = db.get_watchlist()
    buttons = []
    for w in watchlist:
        text = f"{w['code']} {w['name']}"
        buttons.append([{"text": text, "callback_data": f"watch_{w['code']}"}])
    
    keyboard = {"inline_keyboard": buttons}
    return json.dumps(keyboard)

def handle_callback(callback_data):
    """處理回調"""
    parts = callback_data.split("_")
    action = parts[0]
    code = parts[1] if len(parts) > 1 else None
    
    if action == "portfolio" and code:
        # 查看持股詳細
        portfolio = db.get_portfolio()
        stock = next((p for p in portfolio if p['code'] == code), None)
        if stock:
            return f"📊 {stock['code']} {stock['name']}\n\n💰 成本: ${stock['cost']}\n📈 股數: {stock['shares']}\n🎯 停損: ${stock.get('stop_loss', 'N/A')}\n🎯 停利: ${stock.get('stop_profit', 'N/A')}"
    
    elif action == "watch" and code:
        # 查看觀察股票
        watchlist = db.get_watchlist()
        stock = next((w for w in watchlist if w['code'] == code), None)
        if stock:
            return f"👀 {stock['code']} {stock['name']}\n\n🎯 目標價: ${stock.get('target_price', 'N/A')}\n📝 原因: {stock.get('reason', 'N/A')}"
    
    elif action == "analyze":
        # 分析股票
        try:
            analysis = fetcher.fetch_historical_data(code, days=30)
            if analysis:
                latest = analysis[-1]
                return f"📊 {code} 分析\n\n💰 價格: ${latest.get('close', 'N/A')}\n📈 漲跌幅: {latest.get('change_pct', 'N/A')}%"
        except:
            pass
        return f"無法分析 {code}"
    
    return "未知指令"

def send_market_report():
    """發送市場報告"""
    # 強勢股
    strong = fetcher.get_strong_stocks(limit=5)
    strong_text = "\n".join([f"• {s['code']} {s['name']}: ${s['price']} ({s['change_pct']:+.2f}%)" for s in strong])
    
    # 漲幅排行
    gainers = fetcher.get_top_gainers(limit=5)
    gainers_text = "\n".join([f"• {g['code']} {g['name']}: {g['change_pct']:+.2f}%" for g in gainers])
    
    # 持股
    portfolio = db.get_portfolio()
    portfolio_text = "\n".join([f"• {p['code']} {p['name']}: ${p['cost']}" for p in portfolio]) or "無持股"
    
    message = f"""📊 台股市場報告

🚀 強勢股
{strong_text}

📈 漲幅排行
{gainers_text}

💼 持股
{portfolio_text}

🔗 使用指令:
/strong - 強勢股
/gainers - 漲幅排行
/portfolio - 持股
/watchlist - 觀察名單
/analyze [代碼] - 分析股票
"""
    
    return send_message(message)

def send_portfolio_with_buttons():
    """發送持股列表（附按鈕）"""
    portfolio = db.get_portfolio()
    
    if not portfolio:
        return send_message("📋 目前沒有持股")
    
    text = "💼 持股列表\n\n點擊股票查看詳細資訊："
    keyboard = generate_portfolio_keyboard()
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "reply_markup": keyboard
    }
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"發送失敗: {e}")

def send_watchlist_with_buttons():
    """發送觀察名單（附按鈕）"""
    watchlist = db.get_watchlist()
    
    if not watchlist:
        return send_message("📋 目前沒有觀察名單")
    
    text = "👀 觀察名單\n\n點擊股票查看詳細資訊："
    keyboard = generate_watchlist_keyboard()
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "reply_markup": keyboard
    }
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"發送失敗: {e}")

# 指令處理
def process_command(command, args=None):
    """處理指令"""
    command = command.lower()
    
    if command == "/start" or command == "/help":
        return send_message("""📊 股票分析機器人

可用指令：
/start - 開始
/strong - 強勢股
/gainers - 漲幅排行
/market - 市場報告
/portfolio - 持股列表
/watchlist - 觀察名單
/analyze [代碼] - 分析股票
""")
    
    elif command == "/strong":
        strong = fetcher.get_strong_stocks(limit=10)
        text = "🚀 強勢股 TOP 10\n\n" + "\n".join([
            f"{i+1}. {s['code']} {s['name']}: ${s['price']} ({s['change_pct']:+.2f}%) ⭐{s['technical_score']}/10"
            for i, s in enumerate(strong)
        ])
        return send_message(text)
    
    elif command == "/gainers":
        gainers = fetcher.get_top_gainers(limit=10)
        text = "📈 漲幅排行 TOP 10\n\n" + "\n".join([
            f"{i+1}. {g['code']} {g['name']}: {g['change_pct']:+.2f}%"
            for i, g in enumerate(gainers)
        ])
        return send_message(text)
    
    elif command == "/market":
        return send_market_report()
    
    elif command == "/portfolio":
        return send_portfolio_with_buttons()
    
    elif command == "/watchlist":
        return send_watchlist_with_buttons()
    
    elif command == "/analyze" and args:
        code = args[0] if args else None
        if code:
            try:
                hist = fetcher.fetch_historical_data(code, days=30)
                if hist:
                    latest = hist[-1]
                    prev = hist[-2] if len(hist) > 1 else latest
                    change = latest.get('close', 0) - prev.get('close', 0)
                    change_pct = (change / prev.get('close', 1)) * 100
                    text = f"""📊 {code} 分析

💰 現價: ${latest.get('close', 'N/A')}
📈 漲跌: {change:+.2f} ({change_pct:+.2f}%)
📅 交易日: {latest.get('date', 'N/A')}

🔗 完整分析請使用 CLI:
python main.py analyze {code}
"""
                    return send_message(text)
            except Exception as e:
                return send_message(f"❌ 無法分析 {code}: {e}")
        return send_message("請輸入股票代碼，例如：/analyze 2330")
    
    else:
        return send_message("未知指令，請使用 /help 查看指令列表")


if __name__ == '__main__':
    # 測試發送
    print("📤 發送市場報告...")
    send_market_report()
    print("✅ 完成")
