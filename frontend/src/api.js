const BASE = '/api'

async function req(path, opts = {}) {
  const headers = opts.body && !(opts.body instanceof FormData)
    ? { 'Content-Type': 'application/json' }
    : {}
  const r = await fetch(BASE + path, { headers, ...opts })
  if (!r.ok) {
    const txt = await r.text()
    throw new Error(`${r.status} ${txt}`)
  }
  return r.status === 204 ? null : r.json()
}

const json = (method, body) => ({ method, body: JSON.stringify(body) })

export const api = {
  foods: {
    list: (q = '') => req(`/foods${q ? `?q=${encodeURIComponent(q)}` : ''}`),
    create: (f) => req('/foods', json('POST', f)),
    update: (id, f) => req(`/foods/${id}`, json('PUT', f)),
    remove: (id) => req(`/foods/${id}`, { method: 'DELETE' }),
  },
  dishes: {
    list: () => req('/dishes'),
    create: (d) => req('/dishes', json('POST', d)),
    update: (id, d) => req(`/dishes/${id}`, json('PUT', d)),
    remove: (id) => req(`/dishes/${id}`, { method: 'DELETE' }),
  },
  diary: {
    get: (date) => req(`/diary?date=${date}`),
    add: (item) => req('/diary', json('POST', item)),
    update: (id, item) => req(`/diary/${id}`, json('PUT', item)),
    remove: (id) => req(`/diary/${id}`, { method: 'DELETE' }),
  },
  weight: {
    list: (from = '', to = '') => {
      const p = new URLSearchParams()
      if (from) p.set('from', from)
      if (to) p.set('to', to)
      const qs = p.toString()
      return req(`/weight${qs ? `?${qs}` : ''}`)
    },
    add: (e) => req('/weight', json('POST', e)),
    remove: (id) => req(`/weight/${id}`, { method: 'DELETE' }),
  },
  balance: {
    get: (date) => req(`/balance?date=${date}`),
    suggest: (date) => req(`/balance/suggest?date=${date}`),
  },
  profile: {
    get: () => req('/profile'),
    update: (p) => req('/profile', json('PUT', p)),
  },
  activities: {
    list: (date = '') => req(`/activities${date ? `?date=${date}` : ''}`),
    add: (a) => req('/activities', json('POST', a)),
    remove: (id) => req(`/activities/${id}`, { method: 'DELETE' }),
  },
  ocr: {
    label: (file) => {
      const fd = new FormData()
      fd.append('image', file)
      return req('/ocr/label', { method: 'POST', body: fd })
    },
  },
}

export function todayISO() {
  const d = new Date()
  const off = d.getTimezoneOffset()
  return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10)
}
