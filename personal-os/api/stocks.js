export default async function handler(req, res) {
  try {
    const { symbols } = req.query
    const response = await fetch(
      `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbols}`,
      { headers: { 'User-Agent': 'Mozilla/5.0' } }
    )
    const data = await response.json()
    res.json(data)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
}
