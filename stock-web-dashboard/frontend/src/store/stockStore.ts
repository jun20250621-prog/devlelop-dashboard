// 股票狀態管理

import { create } from 'zustand';
import type { Stock, Quote, WatchlistItem } from '../types';

interface StockStore {
  // 持股
  stocks: Stock[];
  quotes: Record<string, Quote>;
  loading: boolean;
  
  // 觀察名單
  watchlist: WatchlistItem[];
  
  // WebSocket
  wsConnected: boolean;
  
  // Actions
  setStocks: (stocks: Stock[]) => void;
  setQuotes: (quotes: Record<string, Quote>) => void;
  updateQuote: (code: string, quote: Quote) => void;
  setLoading: (loading: boolean) => void;
  setWatchlist: (watchlist: WatchlistItem[]) => void;
  setWsConnected: (connected: boolean) => void;
  
  // 計算屬性
  getPortfolioValue: () => number;
  getTotalProfit: () => number;
}

export const useStockStore = create<StockStore>((set, get) => ({
  stocks: [],
  quotes: {},
  loading: true,
  watchlist: [],
  wsConnected: false,
  
  setStocks: (stocks) => set({ stocks }),
  setQuotes: (quotes) => set({ quotes }),
  updateQuote: (code, quote) => set((state) => ({
    quotes: { ...state.quotes, [code]: quote }
  })),
  setLoading: (loading) => set({ loading }),
  setWatchlist: (watchlist) => set({ watchlist }),
  setWsConnected: (wsConnected) => set({ wsConnected }),
  
  getPortfolioValue: () => {
    const { stocks, quotes } = get();
    return stocks.reduce((total, stock) => {
      const quote = quotes[stock.code];
      return total + (quote?.price || 0) * stock.shares;
    }, 0);
  },
  
  getTotalProfit: () => {
    const { stocks, quotes } = get();
    return stocks.reduce((total, stock) => {
      const quote = quotes[stock.code];
      if (!quote) return total;
      const currentValue = quote.price * stock.shares;
      const costValue = stock.cost * stock.shares;
      return total + (currentValue - costValue);
    }, 0);
  }
}));