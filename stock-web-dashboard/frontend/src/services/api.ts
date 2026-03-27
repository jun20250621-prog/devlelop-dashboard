// API 服務

const API_BASE = import.meta.env.PROD ? '' : '/api';

export async function fetchPortfolio(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/portfolio/`);
  if (!res.ok) throw new Error('Failed to fetch portfolio');
  return res.json();
}

export async function fetchPortfolioSummary(): Promise<any> {
  const res = await fetch(`${API_BASE}/portfolio/summary`);
  if (!res.ok) throw new Error('Failed to fetch summary');
  return res.json();
}

export async function fetchQuotes(codes: string[]): Promise<Record<string, any>> {
  const res = await fetch(`${API_BASE}/quotes/prices?codes=${codes.join(',')}`);
  if (!res.ok) throw new Error('Failed to fetch quotes');
  return res.json();
}

export async function fetchQuote(code: string): Promise<any> {
  const res = await fetch(`${API_BASE}/quotes/price/${code}`);
  if (!res.ok) throw new Error('Failed to fetch quote');
  return res.json();
}

export async function fetchHistory(code: string, days: number = 60): Promise<any[]> {
  const res = await fetch(`${API_BASE}/quotes/history/${code}?days=${days}`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function fetchWatchlist(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/portfolio/watchlist`);
  if (!res.ok) throw new Error('Failed to fetch watchlist');
  return res.json();
}

export async function addStock(stock: any): Promise<any> {
  const res = await fetch(`${API_BASE}/portfolio/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(stock)
  });
  if (!res.ok) throw new Error('Failed to add stock');
  return res.json();
}

export async function updateStock(code: string, stock: any): Promise<any> {
  const res = await fetch(`${API_BASE}/portfolio/${code}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(stock)
  });
  if (!res.ok) throw new Error('Failed to update stock');
  return res.json();
}

export async function deleteStock(code: string): Promise<any> {
  const res = await fetch(`${API_BASE}/portfolio/${code}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete stock');
  return res.json();
}

export async function addWatchlist(item: any): Promise<any> {
  const res = await fetch(`${API_BASE}/portfolio/watchlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  });
  if (!res.ok) throw new Error('Failed to add watchlist');
  return res.json();
}

export async function deleteWatchlist(code: string): Promise<any> {
  const res = await fetch(`${API_BASE}/portfolio/watchlist/${code}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete watchlist');
  return res.json();
}