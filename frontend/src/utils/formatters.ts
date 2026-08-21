/**
 * Utility functions for numeric and locale-specific formatting.
 */

/**
 * Formats a number using the Spanish (Argentina / es-AR) locale,
 * ensuring comma (,) is used as the decimal separator.
 *
 * @param value Number to format
 * @param decimals Fixed number of decimal digits (default: 2)
 * @returns Formatted string (e.g. 1.5372 with 3 decimals -> "1,537")
 */
export function formatNumber(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }

  return value.toLocaleString('es-AR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Formats a percentage using comma as the decimal separator and appends '%'.
 *
 * @param value The value to format (e.g. 0.313 for 31.3% if isRatio=true, or 31.3 if isRatio=false)
 * @param decimals Fixed number of decimal digits (default: 1)
 * @param isRatio If true (default), multiplies value by 100 before formatting.
 * @returns Formatted percentage string (e.g. "31,3%")
 */
export function formatPercent(
  value: number | null | undefined,
  decimals: number = 1,
  isRatio: boolean = true
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-%';
  }

  const numericValue = isRatio ? value * 100 : value;
  return `${formatNumber(numericValue, decimals)}%`;
}
