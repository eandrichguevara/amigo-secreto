const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { codigo } = req.body || {};
  if (!codigo) return res.status(400).json({ error: 'missing code' });

  const dbPath = path.join(__dirname, '..', 'db_amigo_secreto.json');
  try {
    const raw = fs.readFileSync(dbPath, 'utf8');
    const datos = JSON.parse(raw);
    const codigoBuscar = String(codigo).toUpperCase();
    const match = datos.find(item => (item.codigo_acceso || '').toUpperCase() === codigoBuscar);
    if (!match) return res.status(404).json({ error: 'not found' });
    return res.status(200).json(match);
  } catch (err) {
    console.error('Error reading DB:', err);
    return res.status(500).json({ error: 'internal error' });
  }
};
