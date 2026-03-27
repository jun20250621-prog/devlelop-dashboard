// 新增/編輯持股表單元件

import { useState } from 'react';
import { X } from 'lucide-react';

interface StockFormProps {
  stock?: {
    code: string;
    name: string;
    cost: number;
    shares: number;
    stop_loss?: number;
    stop_profit?: number;
    industry?: string;
    application?: string;
    buy_date?: string;
  };
  onSubmit: (stock: any) => void;
  onCancel: () => void;
}

interface FormData {
  code: string;
  name: string;
  cost: number;
  shares: number;
  stop_loss: string;
  stop_profit: string;
  industry: string;
  application: string;
  buy_date: string;
}

export function StockForm({ stock, onSubmit, onCancel }: StockFormProps) {
  const [formData, setFormData] = useState<FormData>({
    code: stock?.code || '',
    name: stock?.name || '',
    cost: stock?.cost ?? 0,
    shares: stock?.shares ?? 0,
    stop_loss: stock?.stop_loss?.toString() ?? '',
    stop_profit: stock?.stop_profit?.toString() ?? '',
    industry: stock?.industry ?? '',
    application: stock?.application ?? '',
    buy_date: stock?.buy_date ?? '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      code: formData.code,
      name: formData.name,
      cost: formData.cost,
      shares: formData.shares,
      stop_loss: formData.stop_loss ? parseFloat(formData.stop_loss) : undefined,
      stop_profit: formData.stop_profit ? parseFloat(formData.stop_profit) : undefined,
      industry: formData.industry || undefined,
      application: formData.application || undefined,
      buy_date: formData.buy_date || undefined,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-lg font-bold">
            {stock ? '編輯持股' : '新增持股'}
          </h2>
          <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                股票代碼 *
              </label>
              <input
                type="text"
                required
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="如: 2330"
                disabled={!!stock}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                股票名稱 *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="如: 台積電"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                購入均價 *
              </label>
              <input
                type="number"
                step="0.01"
                required
                value={formData.cost}
                onChange={(e) => setFormData({ ...formData, cost: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                股數 *
              </label>
              <input
                type="number"
                required
                value={formData.shares}
                onChange={(e) => setFormData({ ...formData, shares: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                停損價
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.stop_loss}
                onChange={(e) => setFormData({ ...formData, stop_loss: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="選填"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                停利價
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.stop_profit}
                onChange={(e) => setFormData({ ...formData, stop_profit: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="選填"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                產業
              </label>
              <input
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="選填"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                應用
              </label>
              <input
                type="text"
                value={formData.application}
                onChange={(e) => setFormData({ ...formData, application: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="選填"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              購入日期
            </label>
            <input
              type="date"
              value={formData.buy_date}
              onChange={(e) => setFormData({ ...formData, buy_date: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              {stock ? '儲存' : '新增'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}