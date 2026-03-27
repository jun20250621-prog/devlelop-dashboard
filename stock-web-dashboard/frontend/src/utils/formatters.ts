// 數字格式化工具

export function formatNumber(num: number, decimals: number = 0): string {
  if (num === undefined || num === null) return '-';
  return num.toLocaleString('zh-TW', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

export function formatCurrency(num: number): string {
  if (num === undefined || num === null) return '-';
  return '$' + formatNumber(Math.round(num));
}

export function formatPercent(num: number): string {
  if (num === undefined || num === null) return '-';
  const sign = num >= 0 ? '+' : '';
  return sign + num.toFixed(2) + '%';
}

export function formatPrice(price: number): string {
  if (!price || price === 0) return '-';
  return '$' + price.toFixed(2);
}