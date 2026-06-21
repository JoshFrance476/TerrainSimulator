import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import MapCanvas from './components/MapCanvas'
import PlayPanel from './components/PlayPanel'
import EditPanel from './components/EditPanel'
import WorldPanel from './components/WorldPanel'

const KEY_DIRS = {
  w: 'north', ArrowUp: 'north',
  s: 'south', ArrowDown: 'south',
  a: 'west', ArrowLeft: 'west',
  d: 'east', ArrowRight: 'east',
}

export default function App() {
  const [world, setWorld] = useState(null)
  const [regions, setRegions] = useState([])
  const [biomes, setBiomes] = useState([])
  const [scene, setScene] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const [mode, setMode] = useState('play')          // play | edit | world
  const [playTool, setPlayTool] = useState('move')  // move | select
  const [editTool, setEditTool] = useState('biome') // biome | elevate | lower | smooth | region | inspect
  const [paintMode, setPaintMode] = useState('brush')
  const [selectedBiome, setSelectedBiome] = useState(null)
  const [selectedRegion, setSelectedRegion] = useState(null)
  const [brushSize, setBrushSize] = useState(6)
  const [brushStrength, setBrushStrength] = useState(0.02)
  const [selectedCell, setSelectedCell] = useState(null)

  const fail = (e) => setError(String(e.message || e))

  const refreshWorld = useCallback(() => {
    api.world().then(setWorld).catch(fail)
    api.regions().then(setRegions).catch(fail)
    api.biomes().then(setBiomes).catch(fail)
  }, [])

  useEffect(() => {
    refreshWorld()
    api.scene().then((r) => setScene(r.scene)).catch(() => {})
  }, [refreshWorld])

  // keyboard movement in play mode
  useEffect(() => {
    const handler = async (e) => {
      if (mode !== 'play') return
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return
      const dir = KEY_DIRS[e.key]
      if (!dir) return
      e.preventDefault()
      try {
        const r = await api.movePlayer(dir)
        setWorld((w) => ({ ...w, player: r.player }))
        setSelectedCell(r.player)
      } catch (err) { fail(err) }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [mode])

  const withBusy = (fn) => async (...args) => {
    setBusy(true)
    setError(null)
    try { await fn(...args) } catch (e) { fail(e) } finally { setBusy(false) }
  }

  const promptScene = withBusy(async (cell) => {
    const r = await api.promptScene(cell || world.player)
    setScene(r.scene)
  })

  const chooseAction = withBusy(async (index) => {
    const r = await api.sceneAction(index)
    setScene(r.scene)
    refreshWorld() // scene summaries can add quest regions
  })

  const customAction = withBusy(async (text) => {
    const r = await api.sceneCustom(text)
    setScene(r.scene)
  })

  const exitScene = withBusy(async () => {
    await api.exitScene()
    setScene(null)
  })

  const placePlayer = async (cell) => {
    try {
      const r = await api.placePlayer(cell)
      setWorld((w) => ({ ...w, player: r.player }))
      setSelectedCell(cell)
    } catch (e) { fail(e) }
  }

  return (
    <div className="app">
      <nav className="rail">
        <div className="brand serif">W·S</div>
        {['play', 'edit', 'world'].map((m) => (
          <button key={m} className={mode === m ? 'on' : ''} onClick={() => setMode(m)}>
            {m}
          </button>
        ))}
      </nav>

      <main className="map-area">
        {world ? (
          <MapCanvas
            world={world} regions={regions} mode={mode}
            editTool={editTool} selectedBiome={selectedBiome}
            selectedRegion={selectedRegion} paintMode={paintMode}
            brushSize={brushSize} playTool={playTool}
            selectedCell={selectedCell}
            onSelectCell={setSelectedCell}
            onPlacePlayer={placePlayer}
            onWorldChanged={refreshWorld}
          />
        ) : (
          <div className="loading mono">
            {error ? `Can't reach the backend: ${error}` : 'Reaching the backend…'}
          </div>
        )}
      </main>

      <aside className="side">
        {mode === 'play' && (
          <PlayPanel
            world={world} scene={scene} busy={busy}
            onPromptScene={promptScene} onChooseAction={chooseAction}
            onCustomAction={customAction} onExitScene={exitScene}
            playTool={playTool} setPlayTool={setPlayTool}
            selectedCell={selectedCell}
          />
        )}
        {mode === 'edit' && (
          <EditPanel
            biomes={biomes} regions={regions}
            editTool={editTool} setEditTool={setEditTool}
            selectedBiome={selectedBiome} setSelectedBiome={setSelectedBiome}
            selectedRegion={selectedRegion} setSelectedRegion={setSelectedRegion}
            paintMode={paintMode} setPaintMode={setPaintMode}
            brushSize={brushSize} setBrushSize={setBrushSize}
            brushStrength={brushStrength} setBrushStrength={setBrushStrength}
            selectedCell={selectedCell}
            onWorldChanged={refreshWorld}
            onRegionsChanged={() => api.regions().then(setRegions).catch(fail)}
          />
        )}
        {mode === 'world' && (
          <WorldPanel world={world} onWorldChanged={refreshWorld} />
        )}
        {error && <div className="toast" onClick={() => setError(null)}>{error}</div>}
      </aside>
    </div>
  )
}
