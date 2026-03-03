export function formatValue(value, colName = '') {
  if (value === null || value === undefined) return '—'

  const col = colName.toLowerCase()

  // Currency columns
  if (col.includes('revenue') || col.includes('amount') ||
      col.includes('price') || col.includes('cost') ||
      col.includes('total') || col.includes('profit') ||
      col.includes('quota') || col.includes('sales')) {
    if (typeof value === 'number') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD', maximumFractionDigits: 0,
      }).format(value)
    }
  }

  // Percentage columns
  if (col.includes('pct') || col.includes('percent') || col.includes('rate') || col.includes('margin')) {
    if (typeof value === 'number') return `${value.toFixed(1)}%`
  }

  // Large numbers
  if (typeof value === 'number') {
    if (Number.isInteger(value)) return value.toLocaleString()
    return parseFloat(value.toFixed(2)).toLocaleString()
  }

  return String(value)
}
