/** Kenyan shillings, e.g. 4500 -> "KSh 4,500". */
export const formatKES = (amount) => `KSh ${Number(amount || 0).toLocaleString('en-KE')}`

/** "a, b, c" -> ['a', 'b', 'c'] (service.conditions_treated is stored comma-separated). */
export const splitList = (text) => (text || '').split(',').map((s) => s.trim()).filter(Boolean)

/** Build a wa.me link from any phone format, or null if blank. */
export const whatsappLink = (phone) => {
  const digits = (phone || '').replace(/\D/g, '')
  return digits ? `https://wa.me/${digits}` : null
}
