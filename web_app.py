# -*- coding: utf-8 -*-
"""
股票分析系統 - Web 介面
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os

# 確保可以匯入專案模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder='templates')
CORS(app)

# 匯入數據模組
from data.fetcher import StockDataFetcher
from data.database import DatabaseManager

fetcher = StockDataFetcher()
db = DatabaseManager()

# ==================== 路由 ====================

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """健康檢查"""
    return jsonify({'status': 'ok', 'message': '股票分析系統運行中'})

@app.route('/api/market')
def api_market():
    """市場概況"""
    try:
        market = fetcher.get_market_index()
        return jsonify(market)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strong-stocks')
def api_strong_stocks():
    """強勢股"""
    try:
        limit = request.args.get('limit', 10, type=int)
        stocks = fetcher.get_strong_stocks(limit=limit)
        return jsonify(stocks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-gainers')
def api_top_gainers():
    """漲幅排行"""
    try:
        limit = request.args.get('limit', 20, type=int)
        gainers = fetcher.get_top_gainers(limit=limit)
        return jsonify(gainers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<code>')
def api_analyze(code):
    """股票分析"""
    try:
        # 獲取公司資訊
        company = fetcher.get_company_info(code)
        
        # 獲取歷史數據
        hist = fetcher.fetch_historical_data(code, days=30)
        
        return jsonify({
            'code': code,
            'company': company,
            'history': hist
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio')
def api_portfolio():
    """持股列表"""
    try:
        portfolio = db.get_portfolio()
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio', methods=['POST'])
def api_portfolio_add():
    """新增持股"""
    try:
        data = request.get_json()
        db.add_portfolio(
            code=data.get('code'),
            name=data.get('name'),
            shares=int(data.get('shares', 0)),
            cost=float(data.get('cost', 0)),
            industry=data.get('industry', ''),
            application=data.get('application', ''),
            buy_date=data.get('buy_date', ''),
            stop_loss=float(data.get('stop_loss', 0)),
            stop_profit=float(data.get('stop_profit', 0))
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/<code>', methods=['DELETE'])
def api_portfolio_delete(code):
    """刪除持股"""
    try:
        db.remove_portfolio(code)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist')
def api_watchlist():
    """觀察名單"""
    try:
        watchlist = db.get_watchlist()
        return jsonify(watchlist)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['POST'])
def api_watchlist_add():
    """新增觀察股票"""
    try:
        data = request.get_json()
        db.add_watchlist(
            code=data.get('code'),
            name=data.get('name'),
            target_price=data.get('target_price'),
            reason=data.get('reason', ''),
            industry=data.get('industry', '')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist/<code>', methods=['DELETE'])
def api_watchlist_delete(code):
    """刪除觀察股票"""
    try:
        db.remove_watchlist(code)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def api_trades():
    """交易紀錄"""
    try:
        trades = db.get_trades()
        return jsonify(trades)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades', methods=['POST'])
def api_trade_add():
    """新增交易"""
    try:
        data = request.get_json()
        db.add_trade(
            code=data.get('code'),
            action=data.get('action'),
            shares=int(data.get('shares', 0)),
            price=float(data.get('price', 0)),
            name=data.get('name', ''),
            trade_date=data.get('trade_date', ''),
            strategy=data.get('strategy', '')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 啟動 ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🚀 股票分析系統 Web 介面")
    print(f"📍 http://localhost:{port}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=True)
