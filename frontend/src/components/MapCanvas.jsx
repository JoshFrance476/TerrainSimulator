import { useEffect, useRef, useState, useCallback } from 'react'
import { api, regionColor } from '../api'

const ZOOM_LEVELS = [3, 4, 6, 8, 12, 16, 24, 32]

export default function MapCanvas({
  world, regions, mode, editTool, selectedBiome, selectedRegion,
  paintMode, brushSize, playTool, selectedCell,
  onSelectCell, onPlacePlayer, onWorldChanged,
}) {
  const canvasRef = useRef(null)
  const wrapRef = useRef(null)
  const imgRef = useRef(null)
  const [zoomIdx, setZoomIdx] = useState(4)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [hover, setHover] = useState(null)
  const [imgTick, setImgTick] = useState(0)
  const stroke = useRef({ active: false, negative: false, cells: [], seen: new Set(), timer: null })
  const panRef = useRef(null)

  const scale = ZOOM_LEVELS[zoomIdx]
  const rows = world?.rows ?? 0
  const cols = world?.cols ?? 0

  // ---- load map image whenever the world version changes ----
  useEffect(() => {
    if (!world) return
    const img = new Image()
    img.onload = () => { imgRef.current = img; setImgTick(t => t + 1) }
    img.src = api.mapUrl(world.version)
  }, [world?.version])

  const clampOffset = useCallback((o, sc) => {
    const wrap = wrapRef.current
    if (!wrap) return o
    const maxX = Math.max(0, cols * sc - wrap.clientWidth)
    const maxY = Math.max(0, rows * sc - wrap.clientHeight)
    return { x: Math.min(Math.max(0, o.x), maxX), y: Math.min(Math.max(0, o.y), maxY) }
  }, [rows, cols])

  // centre on the player when the map first loads
  useEffect(() => {
    if (!world || !wrapRef.current) return
    const [pr, pc] = world.player
    setOffset(clampOffset({
      x: pc * scale - wrapRef.current.clientWidth / 2,
      y: pr * scale - wrapRef.current.clientHeight / 2,
    }, scale))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [world?.rows, world?.cols])

  const cellAt = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left + offset.x
    const y = e.clientY - rect.top + offset.y
    const c = Math.floor(x / scale)
    const r = Math.floor(y / scale)
    if (r < 0 || c < 0 || r >= rows || c >= cols) return null
    return [r, c]
  }

  // ---- drawing ----
  useEffect(() => {
    const canvas = canvasRef.current
    const wrap = wrapRef.current
    if (!canvas || !wrap) return
    canvas.width = wrap.clientWidth
    canvas.height = wrap.clientHeight
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#101319'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    const img = imgRef.current
    if (!img) return

    ctx.imageSmoothingEnabled = false
    ctx.drawImage(img, 0, 0, cols, rows, -offset.x, -offset.y, cols * scale, rows * scale)

    // region borders
    if (regions?.length) {
      ctx.lineWidth = Math.max(1.5, scale / 8)
      for (const region of regions) {
        const set = new Set(region.cells.map(([r, c]) => `${r},${c}`))
        ctx.strokeStyle = regionColor(region.id)
        ctx.beginPath()
        for (const [r, c] of region.cells) {
          const px = c * scale - offset.x
          const py = r * scale - offset.y
          if (px < -scale || py < -scale || px > canvas.width || py > canvas.height) continue
          if (!set.has(`${r},${c - 1}`)) { ctx.moveTo(px, py); ctx.lineTo(px, py + scale) }
          if (!set.has(`${r},${c + 1}`)) { ctx.moveTo(px + scale, py); ctx.lineTo(px + scale, py + scale) }
          if (!set.has(`${r - 1},${c}`)) { ctx.moveTo(px, py); ctx.lineTo(px + scale, py) }
          if (!set.has(`${r + 1},${c}`)) { ctx.moveTo(px, py + scale); ctx.lineTo(px + scale, py + scale) }
        }
        ctx.stroke()
      }
    }

    // selected cell
    if (selectedCell) {
      const [r, c] = selectedCell
      ctx.strokeStyle = '#E9E4D6'
      ctx.lineWidth = 2
      ctx.strokeRect(c * scale - offset.x, r * scale - offset.y, scale, scale)
    }

    // brush cursor
    if (hover && mode === 'edit' && editTool !== 'inspect') {
      const [r, c] = hover
      ctx.strokeStyle = 'rgba(201,163,92,0.9)'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.arc(c * scale - offset.x + scale / 2, r * scale - offset.y + scale / 2,
        brushSize * scale, 0, Math.PI * 2)
      ctx.stroke()
    }

    // player marker
    if (world?.player) {
      const [r, c] = world.player
      const px = c * scale - offset.x + scale / 2
      const py = r * scale - offset.y + scale / 2
      ctx.beginPath()
      ctx.arc(px, py, Math.max(4, scale * 0.45), 0, Math.PI * 2)
      ctx.fillStyle = '#C9A35C'
      ctx.fill()
      ctx.lineWidth = 2
      ctx.strokeStyle = '#14171E'
      ctx.stroke()
    }
  }, [world, regions, offset, scale, hover, selectedCell, mode, editTool, brushSize, imgTick, rows, cols])

  // ---- stroke batching ----
  const flushStroke = useCallback(() => {
    const s = stroke.current
    if (!s.cells.length) return
    const cells = s.cells
    s.cells = []
    const body =
      editTool === 'biome' ? { tool: 'paint_biome', cells, biome_id: selectedBiome, fill: paintMode === 'fill' }
      : editTool === 'region' ? { tool: 'region', cells, region_id: selectedRegion, negative: s.negative }
      : editTool === 'smooth' ? { tool: 'smooth', cells }
      : { tool: 'elevate', cells, negative: editTool === 'lower' }
    api.stroke(body).then(onWorldChanged).catch(console.error)
  }, [editTool, selectedBiome, selectedRegion, paintMode, onWorldChanged])

  const addToStroke = (cell, repeatOk) => {
    const s = stroke.current
    const key = `${cell[0]},${cell[1]}`
    if (!repeatOk && s.seen.has(key)) return
    s.seen.add(key)
    s.cells.push(cell)
    if (!s.timer) s.timer = setTimeout(() => { s.timer = null; flushStroke() }, 120)
  }

  const startStroke = (cell, negative) => {
    if (editTool === 'biome' && selectedBiome == null) return
    if (editTool === 'region' && selectedRegion == null) return
    stroke.current = { active: true, negative, cells: [], seen: new Set(), timer: null }
    addToStroke(cell, true)
    if (paintMode === 'fill' && editTool === 'biome') endStroke()
  }

  const endStroke = () => {
    if (!stroke.current.active) return
    stroke.current.active = false
    if (stroke.current.timer) { clearTimeout(stroke.current.timer); stroke.current.timer = null }
    flushStroke()
  }

  // ---- pointer events ----
  const onMouseDown = (e) => {
    const cell = cellAt(e)
    if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
      panRef.current = { x: e.clientX, y: e.clientY, ox: offset.x, oy: offset.y }
      return
    }
    if (!cell) return
    if (mode === 'edit' && editTool !== 'inspect') {
      if (e.button === 0) startStroke(cell, false)
      else if (e.button === 2 && (editTool === 'region' || editTool === 'elevate' || editTool === 'lower')) {
        startStroke(cell, true)
      }
      return
    }
    if (e.button !== 0) return
    if (mode === 'play' && playTool === 'move') onPlacePlayer(cell)
    else onSelectCell(cell)
  }

  const onMouseMove = (e) => {
    if (panRef.current) {
      const p = panRef.current
      setOffset(clampOffset({ x: p.ox - (e.clientX - p.x), y: p.oy - (e.clientY - p.y) }, scale))
      return
    }
    const cell = cellAt(e)
    setHover(cell)
    if (cell && stroke.current.active) {
      const repeatOk = editTool === 'elevate' || editTool === 'lower' || editTool === 'smooth'
      addToStroke(cell, repeatOk)
    }
  }

  const onMouseUp = () => { panRef.current = null; endStroke() }

  const onWheel = (e) => {
    e.preventDefault()
    const dir = e.deltaY < 0 ? 1 : -1
    const next = Math.min(ZOOM_LEVELS.length - 1, Math.max(0, zoomIdx + dir))
    if (next === zoomIdx) return
    const rect = canvasRef.current.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const wx = (offset.x + mx) / scale
    const wy = (offset.y + my) / scale
    const ns = ZOOM_LEVELS[next]
    setZoomIdx(next)
    setOffset(clampOffset({ x: wx * ns - mx, y: wy * ns - my }, ns))
  }

  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const handler = (e) => onWheel(e)
    el.addEventListener('wheel', handler, { passive: false })
    return () => el.removeEventListener('wheel', handler)
  })

  return (
    <div className="map-wrap" ref={wrapRef}>
      <canvas
        ref={canvasRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={() => { setHover(null); onMouseUp() }}
        onContextMenu={(e) => e.preventDefault()}
      />
      <div className="map-readout mono">
        {hover ? `r ${hover[0]} · c ${hover[1]}` : '—'}
        <span className="readout-dim"> · {scale}px/cell · shift-drag to pan</span>
      </div>
    </div>
  )
}
