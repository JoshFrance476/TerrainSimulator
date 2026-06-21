import { useEffect, useState } from 'react'
import { api, hsvToCss, regionColor } from '../api'

const EMPTY_BIOME = { name: '', h: 0.3, s: 0.5, v: 0.6, traversal_cost: 1, description: '' }

export default function EditPanel({
  biomes, regions, editTool, setEditTool, selectedBiome, setSelectedBiome,
  selectedRegion, setSelectedRegion, paintMode, setPaintMode,
  brushSize, setBrushSize, brushStrength, setBrushStrength,
  selectedCell, onWorldChanged, onRegionsChanged,
}) {
  const [tab, setTab] = useState('biomes')
  const [form, setForm] = useState(null)        // {index|null, ...biome}
  const [regionForm, setRegionForm] = useState(null)
  const [cellInfo, setCellInfo] = useState(null)
  const [elevUpdatesBiome, setElevUpdatesBiome] = useState(false)

  useEffect(() => {
    if (selectedCell) api.cell(...selectedCell).then(setCellInfo).catch(() => {})
  }, [selectedCell])

  useEffect(() => {
    api.setBrush({ size: brushSize, strength: brushStrength,
      elevation_updates_biome: elevUpdatesBiome }).catch(() => {})
  }, [brushSize, brushStrength, elevUpdatesBiome])

  const saveBiome = async (e) => {
    e.preventDefault()
    const body = { ...form, h: +form.h, s: +form.s, v: +form.v, traversal_cost: +form.traversal_cost }
    if (form.index == null) await api.addBiome(body)
    else await api.editBiome(form.index, body)
    setForm(null)
    onWorldChanged()
  }

  const newRegion = async () => {
    const { id } = await api.createRegion()
    setSelectedRegion(id)
    setEditTool('region')
    setRegionForm({ id, title: '', visible_desc: '', hidden_desc: '' })
  }

  const saveRegion = async (e) => {
    e.preventDefault()
    await api.setRegionInfo(regionForm.id, regionForm)
    setRegionForm(null)
    onRegionsChanged()
  }

  return (
    <div className="panel">
      <header className="panel-head">
        <h2>Editor</h2>
        <div className="seg">
          {['biomes', 'terrain', 'regions'].map(t => (
            <button key={t} className={tab === t ? 'on' : ''} onClick={() => setTab(t)}>{t}</button>
          ))}
        </div>
      </header>

      <div className="panel-body">
        {tab === 'biomes' && (
          <>
            <div className="row">
              <div className="seg">
                <button className={paintMode === 'brush' ? 'on' : ''} onClick={() => setPaintMode('brush')}>Brush</button>
                <button className={paintMode === 'fill' ? 'on' : ''} onClick={() => setPaintMode('fill')}>Fill</button>
              </div>
              <label className="mono slider-label">size {brushSize}
                <input type="range" min="1" max="20" value={brushSize}
                  onChange={(e) => setBrushSize(+e.target.value)} />
              </label>
            </div>

            <ul className="biome-list">
              {biomes.map((b, i) => (
                <li key={i}
                  className={editTool === 'biome' && selectedBiome === i ? 'on' : ''}
                  onClick={() => { setSelectedBiome(i); setEditTool('biome') }}>
                  <span className="swatch" style={{ background: hsvToCss(b.h, b.s, b.v) }} />
                  <span className="biome-name">{b.name}</span>
                  <span className="mono dim">cost {b.traversal_cost}</span>
                  <button className="ghost" onClick={(e) => { e.stopPropagation(); setForm({ index: i, ...b }) }}>edit</button>
                </li>
              ))}
            </ul>
            <button className="ghost" onClick={() => setForm({ index: null, ...EMPTY_BIOME })}>+ New biome</button>

            {form && (
              <form className="stack" onSubmit={saveBiome}>
                <input required placeholder="Name" value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} />
                <div className="row">
                  {['h', 's', 'v'].map(k => (
                    <label key={k} className="mono slider-label">{k} {(+form[k]).toFixed(2)}
                      <input type="range" min="0" max="1" step="0.01" value={form[k]}
                        onChange={(e) => setForm({ ...form, [k]: e.target.value })} />
                    </label>
                  ))}
                  <span className="swatch big" style={{ background: hsvToCss(+form.h, +form.s, +form.v) }} />
                </div>
                <label className="mono slider-label">traversal cost
                  <input type="number" step="0.1" value={form.traversal_cost}
                    onChange={(e) => setForm({ ...form, traversal_cost: e.target.value })} />
                </label>
                <textarea rows="3" placeholder="Description — the storyteller reads this"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })} />
                <div className="row">
                  <button type="submit">Save biome</button>
                  <button type="button" className="ghost" onClick={() => setForm(null)}>Cancel</button>
                </div>
              </form>
            )}
          </>
        )}

        {tab === 'terrain' && (
          <>
            <div className="seg vertical">
              <button className={editTool === 'elevate' ? 'on' : ''} onClick={() => setEditTool('elevate')}>Raise elevation</button>
              <button className={editTool === 'lower' ? 'on' : ''} onClick={() => setEditTool('lower')}>Lower elevation</button>
              <button className={editTool === 'smooth' ? 'on' : ''} onClick={() => setEditTool('smooth')}>Smooth</button>
              <button className={editTool === 'inspect' ? 'on' : ''} onClick={() => setEditTool('inspect')}>Inspect</button>
            </div>
            <label className="mono slider-label">size {brushSize}
              <input type="range" min="1" max="20" value={brushSize}
                onChange={(e) => setBrushSize(+e.target.value)} />
            </label>
            <label className="mono slider-label">strength {brushStrength.toFixed(3)}
              <input type="range" min="0.005" max="0.1" step="0.005" value={brushStrength}
                onChange={(e) => setBrushStrength(+e.target.value)} />
            </label>
            <label className="check">
              <input type="checkbox" checked={elevUpdatesBiome}
                onChange={(e) => setElevUpdatesBiome(e.target.checked)} />
              Elevation re-derives biome
            </label>
            <p className="dim">Left-drag raises, right-drag lowers. Smoothing averages under the brush.</p>

            {cellInfo && (
              <div className="cell-info mono">
                <h4>{cellInfo.Biome}</h4>
                <p>elev {cellInfo.elevation?.toFixed(3)} · temp {cellInfo.temperature?.toFixed(2)} · rain {cellInfo.rainfall?.toFixed(2)} · cost {cellInfo.traversal_cost?.toFixed(2)}</p>
              </div>
            )}
          </>
        )}

        {tab === 'regions' && (
          <>
            <p className="dim">Regions are named areas with visible and hidden lore. The storyteller weaves them into scenes; finished scenes can write new ones back.</p>
            <button onClick={newRegion}>+ New region (then paint it)</button>
            <ul className="biome-list">
              {regions.map((r) => (
                <li key={r.id}
                  className={editTool === 'region' && selectedRegion === r.id ? 'on' : ''}
                  onClick={() => { setSelectedRegion(r.id); setEditTool('region') }}>
                  <span className="swatch" style={{ background: regionColor(r.id) }} />
                  <span className="biome-name">{r.title}</span>
                  <span className="mono dim">{r.cells.length} cells</span>
                  <button className="ghost" onClick={(e) => { e.stopPropagation(); setRegionForm({ id: r.id, title: r.title, visible_desc: r.visible_desc, hidden_desc: r.hidden_desc }) }}>edit</button>
                </li>
              ))}
            </ul>
            <p className="dim mono">left-drag paints · right-drag erases</p>

            {regionForm && (
              <form className="stack" onSubmit={saveRegion}>
                <input required placeholder="Title" value={regionForm.title}
                  onChange={(e) => setRegionForm({ ...regionForm, title: e.target.value })} />
                <textarea rows="3" placeholder="Visible description — what a traveller would notice"
                  value={regionForm.visible_desc}
                  onChange={(e) => setRegionForm({ ...regionForm, visible_desc: e.target.value })} />
                <textarea rows="3" placeholder="Hidden description — secrets the storyteller may reveal"
                  value={regionForm.hidden_desc}
                  onChange={(e) => setRegionForm({ ...regionForm, hidden_desc: e.target.value })} />
                <div className="row">
                  <button type="submit">Save region</button>
                  <button type="button" className="ghost" onClick={() => setRegionForm(null)}>Cancel</button>
                </div>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  )
}
