import { useEffect, useState } from 'react'
import { api } from '../api'

export default function WorldPanel({ world, onWorldChanged }) {
  const [setup, setSetup] = useState({
    world_description: '', character_description: '', story_focus_description: '',
  })
  const [saved, setSaved] = useState(false)
  const [maps, setMaps] = useState([])
  const [saveName, setSaveName] = useState('')
  const [busy, setBusy] = useState(null)
  const [character, setCharacter] = useState(null)
  const [usage, setUsage] = useState('')

  useEffect(() => {
    api.getSetup().then(setSetup).catch(() => {})
    api.listMaps().then((r) => setMaps(r.maps)).catch(() => {})
    api.usage().then((r) => setUsage(r.usage)).catch(() => {})
  }, [world?.version])

  const save = async (e) => {
    e.preventDefault()
    await api.putSetup(setup)
    setSaved(true)
    setTimeout(() => setSaved(false), 1500)
  }

  const run = (label, fn) => async () => {
    setBusy(label)
    try { await fn() } finally { setBusy(null) }
  }

  return (
    <div className="panel">
      <header className="panel-head"><h2>World</h2></header>
      <div className="panel-body">
        <p className="dim">These three descriptions are the storyteller's whole brief. Any world you can describe, it can run — change them and the same map becomes a different game.</p>

        <form className="stack" onSubmit={save}>
          <label>World
            <textarea rows="5" value={setup.world_description}
              placeholder="What is this place? Its civilisations, dangers, tone…"
              onChange={(e) => setSetup({ ...setup, world_description: e.target.value })} />
          </label>
          <label>Character
            <textarea rows="4" value={setup.character_description}
              placeholder="Who is the player? What do they carry, want, fear…"
              onChange={(e) => setSetup({ ...setup, character_description: e.target.value })} />
          </label>
          <label>Story focus
            <textarea rows="3" value={setup.story_focus_description}
              placeholder="What kind of story should scenes lean toward?"
              onChange={(e) => setSetup({ ...setup, story_focus_description: e.target.value })} />
          </label>
          <button type="submit">{saved ? 'Saved' : 'Save setup'}</button>
        </form>

        <hr />

        <button disabled={!!busy} onClick={run('char', async () => {
          setCharacter(await api.characterSetup())
        })}>
          {busy === 'char' ? 'Generating…' : 'Generate character notebook & stats'}
        </button>
        {character && (
          <div className="cell-info">
            <h4 className="mono">Notebook</h4>
            {character.notebook.map((n, i) => <p key={i} className="serif">{typeof n === 'string' ? n : JSON.stringify(n)}</p>)}
            <h4 className="mono">Stats</h4>
            <p className="mono dim">{JSON.stringify(character.stats)}</p>
          </div>
        )}

        <hr />

        <h4 className="mono">Map</h4>
        <button disabled={!!busy} onClick={run('gen', async () => {
          await api.generateMap(); onWorldChanged()
        })}>
          {busy === 'gen' ? 'Generating…' : 'Generate new procedural map'}
        </button>

        <form className="row" onSubmit={async (e) => {
          e.preventDefault()
          if (!saveName.trim()) return
          await api.saveMap(saveName.trim())
          setMaps((await api.listMaps()).maps)
        }}>
          <input placeholder="Save as…" value={saveName}
            onChange={(e) => setSaveName(e.target.value)} />
          <button type="submit">Save</button>
        </form>

        <ul className="map-list">
          {maps.map((m) => (
            <li key={m}>
              <span>{m}</span>
              <button className="ghost" disabled={!!busy} onClick={run('load', async () => {
                await api.loadMap(m); onWorldChanged()
              })}>Load</button>
            </li>
          ))}
        </ul>

        {usage && <p className="mono dim usage">{usage}</p>}
      </div>
    </div>
  )
}
