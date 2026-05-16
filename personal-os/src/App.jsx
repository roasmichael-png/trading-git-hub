import { useState, useEffect, useCallback } from 'react'

const SCANNER = [
  { ticker: 'PWR',  name: 'Quanta Services' },
  { ticker: 'IESC', name: 'IES Holdings' },
  { ticker: 'POWL', name: 'Powell Industries' },
  { ticker: 'ETN',  name: 'Eaton Corp' },
  { ticker: 'MOD',  name: 'Modine Mfg' },
  { ticker: 'CARR', name: 'Carrier Global' },
  { ticker: 'MLI',  name: 'Mueller Industries' },
  { ticker: 'BE',   name: 'Bloom Energy' },
]

const CRYPTO = [
  { id: 'bitcoin',  ticker: 'BTC', name: 'Bitcoin' },
  { id: 'ethereum', ticker: 'ETH', name: 'Ethereum' },
  { id: 'solana',   ticker: 'SOL', name: 'Solana' },
]

const EVENTS = [
  { date: 'May 16', title: 'La Jolla 5K', sub: 'Del Mar → La Jolla Cove', tag: 'meet women', tc: '#e879f9', tb: '#1a0a1a', url: 'https://lajollahalfmarathon.com/' },
  { date: 'May 21', title: 'F1 Canadian GP', sub: 'Montreal · from $300', tag: 'high-class', tc: '#818cf8', tb: '#0a0a2a', url: 'https://f1experiences.com/2026-canadian-grand-prix' },
  { date: 'Jun 1',  title: 'MLcon San Diego', sub: 'Hyatt La Jolla · AI + founders', tag: 'networking', tc: '#38bdf8', tb: '#001a2a', url: 'https://mlconference.ai/san-diego/' },
  { date: 'Aug 18', title: 'Monterey Car Week', sub: 'Pebble Beach · Ferrari crowd', tag: 'high-class', tc: '#818cf8', tb: '#0a0a2a', url: 'https://www.pebblebeachconcours.net/' },
]

const BODY_ITEMS = [
  { id: 1, label: 'Hit macros', sub: 'Protein 180g · Carbs 140g' },
  { id: 2, label: '15k steps', sub: 'Midday jog or walk' },
  { id: 3, label: 'Arms + shoulders', sub: 'Log progressive overload' },
  { id: 4, label: 'Energy log', sub: 'Track headaches tonight' },
  { id: 5, label: '2 interactions', sub: 'In person · apps · events' },
]

const fmtP = (n) => n == null ? '—' : '$' + Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const fmtC = (n) => n == null ? '' : (n > 0 ? '+' : '') + Number(n).toFixed(2) + '%'
const sigColor = (n) => n == null ? '#555' : n > 0 ? '#4ade80' : '#f87171'
const getSig = (n) => n == null ? { l: '—', bg: '#1a1a1e', c: '#555' } : n > 1.5 ? { l: 'Buy', bg: '#0a2a0f', c: '#4ade80' } : n > 0 ? { l: 'Watch', bg: '#2a1a00', c: '#fbbf24' } : { l: 'Wait', bg: '#1a1a1e', c: '#555' }

async function callClaude(messages, useSearch = false) {
  const body = { model: 'claude-sonnet-4-6', max_tokens: 1200, messages }
  if (useSearch) body.tools = [{ type: 'web_search_20250305', name: 'web_search' }]
  const r = await fetch('/api/claude', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e?.error?.message || r.statusText) }
  const d = await r.json()
  return (d.content || []).filter(b => b.type === 'text').map(b => b.text).join('')
}

export default function App() {
  const [tab, setTab] = useState('all')
  const [prices, setPrices] = useState({})
  const [crypto, setCrypto] = useState({})
  const [signals, setSignals] = useState([])
  const [checked, setChecked] = useState({})
  const [outfits, setOutfits] = useState([])
  const [outfitLoading, setOutfitLoading] = useState(false)
  const [outfitError, setOutfitError] = useState('')
  const [brief, setBrief] = useState('')
  const [briefLoading, setBriefLoading] = useState(false)
  const [briefError, setBriefError] = useState('')
  const [updated, setUpdated] = useState('')

  const fetchCrypto = useCallback(async () => {
    try {
      const r = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true')
      if (!r.ok) return
      const d = await r.json()
      const map = {}
      CRYPTO.forEach(c => { const e = d[c.id]; if (e) map[c.ticker] = { price: e.usd, change: e.usd_24h_change } })
      setCrypto(map)
    } catch {}
  }, [])

  const fetchStocks = useCallback(async () => {
    try {
      const syms = SCANNER.map(s => s.ticker).join(',')
      const r = await fetch(`/api/stocks?symbols=${syms}`)
      if (!r.ok) return
      const d = await r.json()
      const map = {}
      ;(d.quoteResponse?.result || []).forEach(q => { map[q.symbol] = { price: q.regularMarketPrice, change: q.regularMarketChangePercent } })
      setPrices(map)
    } catch {}
  }, [])

  const fetchSignals = useCallback(async () => {
    try {
      const url = 'https://raw.githubusercontent.com/roasmichael-png/trading-git-hub/claude/setup-trading-bot-NISEK/results/scanner_results.json'
      const r = await fetch(url)
      if (!r.ok) return
      const d = await r.json()
      const all = [...(d.scanner1 || []), ...(d.scanner3 || [])]
      setSignals(all)
    } catch {}
  }, [])

  const refresh = useCallback(async () => {
    await Promise.all([fetchCrypto(), fetchStocks(), fetchSignals()])
    setUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
  }, [fetchCrypto, fetchStocks, fetchSignals])

  useEffect(() => { refresh() }, [refresh])

  const loadOutfits = async () => {
    setOutfitLoading(true); setOutfitError(''); setOutfits([])
    try {
      const text = await callClaude([{ role: 'user', content: `Find 4 specific men's clothing items to buy right now from Ralph Lauren, J.Crew, or Todd Snyder. Old money style: 1 linen shirt, 1 blazer, 1 chino, 1 loafer. Find the actual product page and a direct product image URL (.jpg or .png from their CDN). Return ONLY a raw JSON array with no markdown:\n[{"name":"...","brand":"...","price":"$...","image_url":"https://...","buy_url":"https://...","vibe":"..."}]` }], true)
      const s = text.indexOf('['); const e = text.lastIndexOf(']')
      if (s === -1) throw new Error('Could not parse products')
      setOutfits(JSON.parse(text.slice(s, e + 1)))
    } catch (e) { setOutfitError(e.message) }
    setOutfitLoading(false)
  }

  const generateBrief = async () => {
    setBriefLoading(true); setBriefError(''); setBrief('')
    try {
      const text = await callClaude([{ role: 'user', content: `Today is ${new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}. Personal lifestyle assistant for a man in San Diego. Old money style. Goals: meet high quality women, elite network, 10% body fat. Search for one real upcoming fitness event in La Jolla/Del Mar/Encinitas in the next 14 days. Write a 3-sentence morning brief: one action to meet women today, one high-class event to book, one money move. Under 80 words. Plain text only.` }], true)
      setBrief(text)
    } catch (e) { setBriefError(e.message) }
    setBriefLoading(false)
  }

  const buys = SCANNER.filter(s => prices[s.ticker]?.change > 1.5).length
  const done = Object.values(checked).filter(Boolean).length
  const tabs = ['all', 'scanner', 'crypto', 'life os', 'body']
  const show = (panels) => {
    const map = { all: true, scanner: ['scanner', 'crypto'].includes(panels), crypto: panels === 'crypto', 'life os': ['events', 'outfits', 'brief'].includes(panels), body: panels === 'body' }
    return map[tab] !== false && (tab === 'all' || map[tab])
  }

  const s = {
    os: { background: '#0d0d0f', borderRadius: 16, padding: 20, color: '#f0f0f0' },
    card: { background: '#111113', border: '0.5px solid #1a1a1e', borderRadius: 12, padding: '14px 15px' },
    lbl: { fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#555', fontWeight: 500, marginBottom: 12 },
    row: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: '0.5px solid #1a1a1e' },
    metric: { background: '#111113', border: '0.5px solid #1a1a1e', borderRadius: 10, padding: '10px 12px' },
  }

  return (
    <div style={s.os}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 18, paddingBottom: 16, borderBottom: '0.5px solid #1e1e22' }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 500, color: '#fff', letterSpacing: '-0.02em' }}>Personal OS</div>
          <div style={{ fontSize: 11, color: '#555', marginTop: 3 }}>
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
            {updated && ` · Updated ${updated}`}
          </div>
        </div>
        <button onClick={refresh} style={{ fontSize: 11, padding: '5px 12px', borderRadius: 20, border: '0.5px solid #2a2a2e', background: 'transparent', color: '#888', cursor: 'pointer', fontFamily: 'inherit', display: 'flex', alignItems: 'center', gap: 5 }}>
          ↺ Refresh
        </button>
      </div>

      <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ fontSize: 11, padding: '4px 12px', borderRadius: 20, border: '0.5px solid #222', background: tab === t ? '#fff' : 'transparent', color: tab === t ? '#000' : '#666', cursor: 'pointer', fontFamily: 'inherit', textTransform: 'capitalize', transition: 'all 0.15s' }}>
            {t}
          </button>
        ))}
      </div>

      {(tab === 'all' || tab === 'scanner' || tab === 'crypto') && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8, marginBottom: 14 }}>
          {[
            { val: buys || '—', lbl: 'Buy signals' },
            { val: crypto['BTC']?.price ? '$' + Math.round(crypto['BTC'].price / 1000) + 'k' : '—', lbl: 'BTC' },
            { val: crypto['ETH']?.price ? '$' + Math.round(crypto['ETH'].price).toLocaleString() : '—', lbl: 'ETH' },
            { val: '9d', lbl: 'To F1 Canada' },
          ].map((m, i) => (
            <div key={i} style={s.metric}>
              <div style={{ fontSize: 17, fontWeight: 500, color: '#fff', fontFamily: 'DM Mono, monospace' }}>{m.val}</div>
              <div style={{ fontSize: 10, color: '#555', marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{m.lbl}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>

        {(tab === 'all' || tab === 'scanner') && (
          <div style={{ ...s.card, gridColumn: '1 / -1' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <div style={{ ...s.lbl, marginBottom: 0 }}>📡 Scanner signals</div>
              <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 10, background: '#0a2a0f', color: '#4ade80', border: '0.5px solid #1a4a1f' }}>
                {signals.length > 0 ? `${signals.length} signals` : 'Updates 10am EST'}
              </span>
            </div>
            <div style={{ fontSize: 10, color: '#444', marginBottom: 10 }}>StochRSI + MACD + Volume — same signals sent to Telegram</div>
            {signals.length === 0 && (
              <div style={{ fontSize: 12, color: '#444', textAlign: 'center', padding: '16px 0' }}>No signals yet — updates daily at 10am EST</div>
            )}
            {signals.map((h, i) => {
              const ratingColor = h.rating === 'STRONG BUY' ? '#4ade80' : h.rating === 'BUY' ? '#fbbf24' : '#888'
              const ratingBg    = h.rating === 'STRONG BUY' ? '#0a2a0f' : h.rating === 'BUY' ? '#2a1a00' : '#1a1a1e'
              return (
                <div key={i} style={{ ...s.row, borderBottom: i === signals.length - 1 ? 'none' : '0.5px solid #1a1a1e', flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 500, color: '#fff', fontFamily: 'DM Mono, monospace' }}>{h.symbol}</span>
                      <span style={{ fontSize: 9, padding: '2px 7px', borderRadius: 8, background: ratingBg, color: ratingColor, border: `0.5px solid ${ratingColor}44` }}>{h.rating}</span>
                    </div>
                    <span style={{ fontSize: 12, color: '#fff', fontFamily: 'DM Mono, monospace' }}>${h.close?.toFixed(2)}</span>
                  </div>
                  <div style={{ fontSize: 10, color: '#555' }}>{h.note}</div>
                  <div style={{ fontSize: 10, color: '#444' }}>
                    Entry ${h.entry?.toFixed(2)} · Stop ${h.stop?.toFixed(2)} · Target ${h.target?.toFixed(2)}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {(tab === 'all' || tab === 'scanner' || tab === 'crypto') && (
          <div style={s.card}>
            <div style={s.lbl}>🪙 Crypto</div>
            {CRYPTO.map((c, i) => {
              const d = crypto[c.ticker]
              return (
                <div key={c.ticker} style={{ ...s.row, borderBottom: i === CRYPTO.length - 1 ? 'none' : '0.5px solid #1a1a1e' }}>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 500, color: '#fff', fontFamily: 'DM Mono, monospace' }}>{c.ticker}</div>
                    <div style={{ fontSize: 10, color: '#444', marginTop: 1 }}>{c.name}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 12, fontWeight: 500, color: '#fff', fontFamily: 'DM Mono, monospace' }}>{fmtP(d?.price)}</div>
                    <div style={{ fontSize: 10, color: sigColor(d?.change) }}>{fmtC(d?.change)}</div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {(tab === 'all' || tab === 'life os') && (
          <div style={s.card}>
            <div style={s.lbl}>📅 Events</div>
            {EVENTS.map((e, i) => (
              <a key={i} href={e.url} target="_blank" rel="noreferrer" style={{ display: 'flex', gap: 10, padding: '8px 0', borderBottom: i === EVENTS.length - 1 ? 'none' : '0.5px solid #1a1a1e', textDecoration: 'none' }}>
                <div style={{ fontSize: 10, fontWeight: 500, color: '#666', minWidth: 36, textAlign: 'center', background: '#1a1a1e', borderRadius: 8, padding: '4px 5px', lineHeight: 1.4, flexShrink: 0 }}>{e.date}</div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 500, color: '#f0f0f0' }}>{e.title}</div>
                  <div style={{ fontSize: 10, color: '#555', marginTop: 1 }}>{e.sub}</div>
                  <span style={{ display: 'inline-block', fontSize: 9, padding: '2px 6px', borderRadius: 8, marginTop: 3, fontWeight: 500, background: e.tb, color: e.tc, border: `0.5px solid ${e.tc}44` }}>{e.tag}</span>
                </div>
              </a>
            ))}
          </div>
        )}

        {(tab === 'all' || tab === 'life os') && (
          <div style={s.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={{ ...s.lbl, marginBottom: 0 }}>👔 Outfits to cop</div>
              <button onClick={loadOutfits} disabled={outfitLoading} style={{ fontSize: 12, padding: '5px 14px', borderRadius: 20, border: '0.5px solid #2a2a2e', background: outfitLoading ? '#1a1a1e' : 'transparent', color: '#ccc', cursor: outfitLoading ? 'not-allowed' : 'pointer', fontFamily: 'inherit' }}>
                {outfitLoading ? 'Loading…' : outfits.length ? 'Refresh →' : 'Load →'}
              </button>
            </div>
            {outfitError && <div style={{ fontSize: 11, color: '#f87171', marginBottom: 8 }}>{outfitError}</div>}
            {!outfits.length && !outfitLoading && !outfitError && (
              <div style={{ fontSize: 12, color: '#444', textAlign: 'center', padding: '20px 0' }}>Tap Load for today's picks with real photos</div>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {outfits.map((item, i) => (
                <a key={i} href={item.buy_url || '#'} target="_blank" rel="noreferrer" style={{ background: '#0a0a0c', border: '0.5px solid #1a1a1e', borderRadius: 10, overflow: 'hidden', textDecoration: 'none', display: 'block' }}>
                  <div style={{ width: '100%', height: 120, background: '#111113', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {item.image_url
                      ? <img src={item.image_url} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={e => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex' }} />
                      : null}
                    <div style={{ width: '100%', height: '100%', display: item.image_url ? 'none' : 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28 }}>👔</div>
                  </div>
                  <div style={{ padding: '8px 10px' }}>
                    <div style={{ fontSize: 11, fontWeight: 500, color: '#f0f0f0', lineHeight: 1.3 }}>{item.name}</div>
                    <div style={{ fontSize: 10, color: '#555', marginTop: 2 }}>{item.brand}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
                      <span style={{ fontSize: 11, fontWeight: 500, color: '#4ade80' }}>{item.price}</span>
                      <span style={{ fontSize: 10, color: '#444' }}>Shop →</span>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {(tab === 'all' || tab === 'body') && (
          <div style={{ ...s.card, gridColumn: '1 / -1' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={{ ...s.lbl, marginBottom: 0 }}>💪 Body check</div>
              <div style={{ fontSize: 11, color: '#555' }}>{done} / {BODY_ITEMS.length}</div>
            </div>
            {BODY_ITEMS.map((item, i) => (
              <div key={item.id} onClick={() => setChecked(p => ({ ...p, [item.id]: !p[item.id] }))} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderBottom: i === BODY_ITEMS.length - 1 ? 'none' : '0.5px solid #1a1a1e', cursor: 'pointer' }}>
                <div style={{ width: 18, height: 18, borderRadius: '50%', border: checked[item.id] ? 'none' : '1.5px solid #2a2a2e', background: checked[item.id] ? '#0a2a0f' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {checked[item.id] && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>}
                </div>
                <div>
                  <div style={{ fontSize: 12, color: checked[item.id] ? '#444' : '#f0f0f0', textDecoration: checked[item.id] ? 'line-through' : 'none' }}>{item.label}</div>
                  <div style={{ fontSize: 10, color: '#444', marginTop: 1 }}>{item.sub}</div>
                </div>
              </div>
            ))}
            <div style={{ height: 3, background: '#1a1a1e', borderRadius: 4, overflow: 'hidden', marginTop: 8 }}>
              <div style={{ height: '100%', width: `${(done / BODY_ITEMS.length) * 100}%`, background: '#4ade80', borderRadius: 4, transition: 'width 0.3s' }} />
            </div>
          </div>
        )}

        {(tab === 'all' || tab === 'life os') && (
          <div style={{ ...s.card, gridColumn: '1 / -1' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ ...s.lbl, marginBottom: 0 }}>⚡ Life OS brief</div>
              <button onClick={generateBrief} disabled={briefLoading} style={{ fontSize: 12, padding: '6px 16px', borderRadius: 20, border: '0.5px solid #2a2a2e', background: briefLoading ? '#1a1a1e' : 'transparent', color: '#ccc', cursor: briefLoading ? 'not-allowed' : 'pointer', fontFamily: 'inherit' }}>
                {briefLoading ? 'Generating…' : brief ? 'Regenerate →' : "Generate today's brief →"}
              </button>
            </div>
            {briefError && <div style={{ fontSize: 11, color: '#f87171', marginTop: 10 }}>{briefError}</div>}
            {brief && <div style={{ fontSize: 13, color: '#ccc', lineHeight: 1.7, marginTop: 10 }}>{brief}</div>}
          </div>
        )}

      </div>
    </div>
  )
}
