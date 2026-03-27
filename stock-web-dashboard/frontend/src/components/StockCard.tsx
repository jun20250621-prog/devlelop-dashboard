// 持股卡片元件

import { formatNumber } from '../utils/formatters';

export function StockCard({ stock, quote }: { stock: any; quote: any }) {
  const currentPrice = quote?.price || 0;
  const cost = stock.cost || 0;
  const shares = stock.shares || 0;
  const profit = currentPrice > 0 ? (currentPrice - cost) * shares : 0;
  const profitPct = cost > 0 ? ((currentPrice - cost) / cost) * 100 : 0;
  
  const isProfit = profit >= 0;
  
  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="font-bold text-lg">{stock.name}</div>
          <div className="text-gray-500 text-sm">{stock.code}</div>
        </div>
        <div className={`text-lg font-bold ${isProfit ? 'text-green-500' : 'text-red-500'}`}>
          {profit >= 0 ? '+' : ''}{profitPct.toFixed(1)}%
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <div className="text-gray-500">現價</div>
          <div className="font-medium">${currentPrice.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-gray-500">成本</div>
          <div className="font-medium">${cost.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-gray-500">股數</div>
          <div className="font-medium">{formatNumber(shares)}</div>
        </div>
        <div>
          <div className="text-gray-500">損益</div>
          <div className={`font-medium ${isProfit ? 'text-green-500' : 'text-red-500'}`}>
            ${formatNumber(profit)}
          </div>
        </div>
      </div>
      
      {stock.stop_loss || stock.stop_profit ? (
        <div className="mt-2 pt-2 border-t text-xs text-gray-500">
          {stock.stop_loss && <span>停損: ${stock.stop_loss} </span>}
          {stock.stop_profit && <span>停利: ${stock.stop_profit}</span>}
        </div>
      ) : null}
    </div>
  );
}