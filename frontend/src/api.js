const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function req(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) {
    let detail = res.statusText
    try { detail = (await res.json()).detail || detail } catch { /* ignore */ }
    throw new Error(detail)
  }
  return res.json()
}

const get = (p) => req(p)
const post = (p, body) => req(p, { method: 'POST', body: JSON.stringify(body ?? {}) })
const put = (p, body) => req(p, { method: 'PUT', body: JSON.stringify(body ?? {}) })

export const api = {
  base: BASE,
  mapUrl: (version) => `${BASE}/api/map.png?v=${version}`,

  world: () => get('/api/world'),
  regions: () => get('/api/regions'),
  biomes: () => get('/api/biomes'),
  cell: (r, c) => get(`/api/cell/${r}/${c}`),
  path: (start, end) => post('/api/path', { start, end }),

  setBrush: (body) => post('/api/edit/brush', body),
  stroke: (body) => post('/api/edit/stroke', body),
  addBiome: (body) => post('/api/biomes', body),
  editBiome: (i, body) => put(`/api/biomes/${i}`, body),
  createRegion: () => post('/api/regions'),
  setRegionInfo: (id, body) => put(`/api/regions/${id}`, body),

  movePlayer: (direction) => post('/api/player/move', { direction }),
  placePlayer: (cell) => post('/api/player/place', { cell }),

  scene: () => get('/api/scene'),
  promptScene: (cell) => post('/api/scene/prompt', { cell }),
  sceneAction: (index) => post('/api/scene/action', { index }),
  sceneCustom: (text) => post('/api/scene/custom', { text }),
  exitScene: () => post('/api/scene/exit'),

  character: () => get('/api/character'),
  getSetup: () => get('/api/story/setup'),
  putSetup: (body) => put('/api/story/setup', body),
  characterSetup: () => post('/api/story/character-setup'),
  usage: () => get('/api/usage'),

  listMaps: () => get('/api/maps'),
  generateMap: () => post('/api/maps/generate'),
  saveMap: (name) => post('/api/maps/save', { name }),
  loadMap: (name) => post('/api/maps/load', { name }),
}

export function hsvToCss(h, s, v) {
  // h,s,v in 0..1 (matching the backend colour maps)
  const i = Math.floor(h * 6)
  const f = h * 6 - i
  const p = v * (1 - s)
  const q = v * (1 - f * s)
  const t = v * (1 - (1 - f) * s)
  const [r, g, b] = [
    [v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q],
  ][i % 6]
  return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`
}

export function regionColor(id) {
  // mirrors produce_border_maps.region_id_to_color
  return `rgb(${(id * 97) % 256}, ${(id * 57) % 256}, ${(id * 17) % 256})`
}
