/**
 * Minimal SQL syntax highlighter — returns HTML string.
 * Used for displaying generated SQL in a readable format.
 */
const KEYWORDS = [
  'SELECT','FROM','WHERE','JOIN','LEFT','RIGHT','INNER','OUTER','FULL',
  'ON','GROUP','BY','ORDER','HAVING','LIMIT','OFFSET','AS','AND','OR',
  'NOT','IN','IS','NULL','LIKE','BETWEEN','CASE','WHEN','THEN','ELSE',
  'END','DISTINCT','COUNT','SUM','AVG','MIN','MAX','WITH','UNION','ALL',
  'EXISTS','ASC','DESC','CAST','COALESCE','STRFTIME','ROUND','SUBSTR',
]

export function highlightSQL(sql) {
  if (!sql) return ''

  // Escape HTML first
  let escaped = sql
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Comments
  escaped = escaped.replace(/(--[^\n]*)/g, '<span class="sql-comment">$1</span>')

  // String literals
  escaped = escaped.replace(/('(?:[^'\\]|\\.)*')/g, '<span class="sql-string">$1</span>')

  // Numbers
  escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, '<span class="sql-number">$1</span>')

  // Keywords (case-insensitive, word boundary)
  KEYWORDS.forEach(kw => {
    const re = new RegExp(`\\b(${kw})\\b`, 'gi')
    escaped = escaped.replace(re, '<span class="sql-keyword">$1</span>')
  })

  return escaped
}
