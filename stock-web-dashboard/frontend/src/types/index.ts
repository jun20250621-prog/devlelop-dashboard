// 股票類型定義

export interface Stock {
  code: string;
  name: string;
  cost: number;
  shares: number;
  stop_loss?: number;
  stop_profit?: number;
  industry?: string;
  application?: string;
  buy_date?: string;
}

export interface StockWithPrice extends Stock {
  current_price: number;
  change: number;
  change_pct: number;
  profit: number;
  profit_pct: number;
}

export interface Quote {
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
  timestamp: number;
}

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface WatchlistItem {
  code: string;
  name: string;
  industry?: string;
  application?: string;
}

export interface PortfolioSummary {
  total_cost: number;
  count: number;
  stocks: Record<string, Stock>;
}

export interface WebSocketMessage {
  type: 'prices' | 'ping' | 'error';
  data?: Record<string, Quote>;
}