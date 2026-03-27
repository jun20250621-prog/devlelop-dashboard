import { useState, useEffect } from 'react';
import { useStockStore } from './store/stockStore';
import { useWebSocket } from './hooks/useWebSocket';
import { fetchPortfolio, fetchQuotes, fetchWatchlist, addStock, updateStock, deleteStock } from './services/api';
import { StockCard } from './components/StockCard';
import { StockForm } from './components/StockForm';
import { formatCurrency, formatPercent } from './utils/formatters';
import { LayoutDashboard, Eye, Settings, TrendingUp, Plus, Trash2 } from 'lucide-react';

type Tab = 'portfolio' | 'watchlist' | 'settings';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('portfolio');
  const [showStockForm, setShowStockForm] = useState(false);
  const [editingStock, setEditingStock] = useState<any>(null);
  const { 
    stocks, setStocks, 
    quotes, setQuotes,
    watchlist, setWatchlist,
    loading, setLoading,
    wsConnected
  } = useStockStore();
  
  // 連接 WebSocket
  useWebSocket();
  
  // 初始載入資料
  useEffect(() => {
    async function loadData() {
      try {
        const portfolioData = await fetchPortfolio();
        const stockList = Object.entries(portfolioData).map(([code, data]: [string, any]) => ({
          code,
          ...data
        }));
        setStocks(stockList);
        
        if (stockList.length > 0) {
          const codes = stockList.map((s: any) => s.code);
          const quotesData = await fetchQuotes(codes);
          setQuotes(quotesData);
        }
        
        const watchlistData = await fetchWatchlist();
        setWatchlist(watchlistData);
        
      } catch (err) {
        console.error('Load data error:', err);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, []);
  
  // 計算總損益
  const totalCost = stocks.reduce((sum, s) => sum + s.cost * s.shares, 0);
  const totalValue = stocks.reduce((sum, s) => {
    const q = quotes[s.code];
    return sum + (q?.price || 0) * s.shares;
  }, 0);
  const totalProfit = totalValue - totalCost;
  const profitPct = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;
  
  // 新增持股
  const handleAddStock = async (stock: any) => {
    try {
      await addStock(stock);
      // 重新載入
      const portfolioData = await fetchPortfolio();
      const stockList = Object.entries(portfolioData).map(([code, data]: [string, any]) => ({
        code,
        ...data
      }));
      setStocks(stockList);
      setShowStockForm(false);
    } catch (err) {
      console.error('Add stock error:', err);
      alert('新增失敗');
    }
  };
  
  // 編輯持股
  const handleEditStock = (stock: any) => {
    setEditingStock(stock);
    setShowStockForm(true);
  };
  
  // 儲存編輯
  const handleSaveEdit = async (stock: any) => {
    try {
      await updateStock(stock.code, stock);
      // 重新載入
      const portfolioData = await fetchPortfolio();
      const stockList = Object.entries(portfolioData).map(([code, data]: [string, any]) => ({
        code,
        ...data
      }));
      setStocks(stockList);
      setShowStockForm(false);
      setEditingStock(null);
    } catch (err) {
      console.error('Update stock error:', err);
      alert('更新失敗');
    }
  };
  
  // 刪除持股
  const handleDeleteStock = async (code: string) => {
    if (!confirm('確定要刪除這檔股票嗎？')) return;
    try {
      await deleteStock(code);
      const portfolioData = await fetchPortfolio();
      const stockList = Object.entries(portfolioData).map(([code, data]: [string, any]) => ({
        code,
        ...data
      }));
      setStocks(stockList);
    } catch (err) {
      console.error('Delete stock error:', err);
      alert('刪除失敗');
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-gray-500">載入中...</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-500 text-white p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-8 h-8" />
            <h1 className="text-xl font-bold">台股智能分析系統</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm">{wsConnected ? '即時' : '離線'}</span>
          </div>
        </div>
      </header>
      
      {/* Summary Cards */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">總市值</div>
            <div className="text-2xl font-bold">{formatCurrency(totalValue)}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">總成本</div>
            <div className="text-2xl font-bold">{formatCurrency(totalCost)}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">總損益</div>
            <div className={`text-2xl font-bold ${totalProfit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {formatCurrency(totalProfit)}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm">報酬率</div>
            <div className={`text-2xl font-bold ${profitPct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {formatPercent(profitPct)}
            </div>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="flex border-b">
            <button
              className={`flex items-center gap-2 px-6 py-3 font-medium ${activeTab === 'portfolio' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('portfolio')}
            >
              <LayoutDashboard className="w-4 h-4" />
              持股
            </button>
            <button
              className={`flex items-center gap-2 px-6 py-3 font-medium ${activeTab === 'watchlist' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('watchlist')}
            >
              <Eye className="w-4 h-4" />
              觀察名單
            </button>
            <button
              className={`flex items-center gap-2 px-6 py-3 font-medium ${activeTab === 'settings' ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
              onClick={() => setActiveTab('settings')}
            >
              <Settings className="w-4 h-4" />
              設定
            </button>
          </div>
          
          {/* Content */}
          <div className="p-4">
            {activeTab === 'portfolio' && (
              <div>
                {/* Action Bar */}
                <div className="flex justify-end mb-4">
                  <button
                    onClick={() => { setEditingStock(null); setShowStockForm(true); }}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                  >
                    <Plus className="w-4 h-4" />
                    新增持股
                  </button>
                </div>
                
                {/* Stock Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {stocks.length === 0 ? (
                    <div className="col-span-full text-center text-gray-500 py-8">
                      尚無持股資料，點擊上方「新增持股」開始
                    </div>
                  ) : (
                    stocks.map((stock) => (
                      <div key={stock.code} className="relative group">
                        <StockCard 
                          key={stock.code} 
                          stock={stock} 
                          quote={quotes[stock.code]} 
                        />
                        {/* Hover Actions */}
                        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => handleEditStock(stock)}
                            className="p-1.5 bg-blue-500 text-white rounded hover:bg-blue-600"
                            title="編輯"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDeleteStock(stock.code)}
                            className="p-1.5 bg-red-500 text-white rounded hover:bg-red-600"
                            title="刪除"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
            
            {activeTab === 'watchlist' && (
              <div>
                {watchlist.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">尚無觀察名單</div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {watchlist.map((item) => (
                      <div key={item.code} className="bg-gray-50 rounded-lg p-4">
                        <div className="font-bold">{item.name}</div>
                        <div className="text-gray-500 text-sm">{item.code}</div>
                        <div className="text-xs text-gray-400 mt-1">{item.industry}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'settings' && (
              <div className="text-center text-gray-500 py-8">
                <Settings className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>設定功能開發中...</p>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Stock Form Modal */}
      {showStockForm && (
        <StockForm
          stock={editingStock}
          onSubmit={editingStock ? handleSaveEdit : handleAddStock}
          onCancel={() => { setShowStockForm(false); setEditingStock(null); }}
        />
      )}
    </div>
  );
}

export default App;