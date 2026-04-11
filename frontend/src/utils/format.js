export function fmt(v, digits = 2, suffix = '') {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toFixed(digits)}${suffix ? ' ' + suffix : ''}`
}

/** 5 V шина Raspberry */
export function color5v(volts) {
  if (volts == null || Number.isNaN(volts)) return 'grey-5'
  if (volts >= 4.85) return 'positive'
  if (volts >= 4.55) return 'warning'
  return 'negative'
}

/** Аккумулятор привода ~7.4 V (2S), грубые пороги */
export function colorDrivePack(volts) {
  if (volts == null || Number.isNaN(volts)) return 'grey-5'
  if (volts >= 7.2) return 'positive'
  if (volts >= 6.5) return 'warning'
  return 'negative'
}
