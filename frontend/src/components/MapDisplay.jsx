import { useState, useRef, useEffect } from 'react'
import { useWorldData } from '../hooks/useWorldData'
import MapToolbar from './MapToolbar'

function MapDisplay({ selectedCell, onCellSelect, playerLocation, onPlayerLocationChange }) {
    const baseMapRef = useRef(null) //base map canvas - RBG map
    const overlayRef = useRef(null) //overlay canvas - regions
    const interactionRef = useRef(null) //interaction canvas - hovered cell, selected cell, tooltip
    const imageDataRef = useRef(null) // ImageData object containing Uint8Array RGB map data

    const { version, setVersion, dimensions, maxRegionsPerCell, noRegionId, 
        biomeMap, biomeLookup, regionMap, regionLookup
    } = useWorldData()

    const [lastHoveredCell, setLastHoveredCell] = useState(null) // shape: {x, y, biomeData}

    const [tooltip, setTooltip] = useState(null) //shape: {x, y, biomeName}

    const SCALE = 10 // Interaction layer scale factor

    const [zoom, setZoom] = useState(1)
    const [pan, setPan] = useState({ x: 0, y: 0 })

    const MIN_ZOOM = 0.5
    const MAX_ZOOM = 8

    const isPanning = useRef(false)
    const lastPanPos = useRef({ x: 0, y: 0 })   

    const [interactionMode, setInteractionMode] = useState('view') // 'view' or 'move'

    // Resize the canvases when the dimensions change
    useEffect(() => {
        if (!dimensions) return

        baseMapRef.current.width = dimensions.width
        baseMapRef.current.height = dimensions.height

        for (const ref of [overlayRef, interactionRef]) {
            ref.current.width = dimensions.width * SCALE
            ref.current.height = dimensions.height * SCALE
        }
    }, [dimensions])

    //Get the RGB map data from the backend and draw it on the base map canvas
    useEffect(() => {
        if (!dimensions) return

        async function fetchRGBMap() {
            const res = await fetch(`/api/world/rgb?v=${version}`)

            if (!res.ok) {
                console.error('Failed to fetch RGB map data', await res.text())
                return
            }

            const buffer = await res.arrayBuffer()
            const imageData = new ImageData(
                new Uint8ClampedArray(buffer),
                dimensions.width,
                dimensions.height
            )

            imageDataRef.current = imageData

            const ctx = baseMapRef.current.getContext('2d')
            ctx.putImageData(imageData, 0, 0)
        }
        fetchRGBMap()
    }, [version, dimensions])

    // Redraw interaction layer when selected cell changes
    useEffect(() => {
        if (!dimensions) return
        drawInteractionLayer(lastHoveredCell, selectedCell, playerLocation)
    }, [selectedCell, dimensions, playerLocation])

    // Draw hovered cell and selected cell on interaction layer
    function drawInteractionLayer(hovered, selected, player) {
        const ctx = interactionRef.current.getContext('2d')

        ctx.clearRect(0, 0, dimensions.width * SCALE, dimensions.height * SCALE)
        
        ctx.save()
        ctx.scale(SCALE, SCALE)
        
        if (hovered) {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.35)'
            ctx.fillRect(hovered.x, hovered.y, 1, 1)
        }

        if (selected) {
            ctx.strokeStyle = 'yellow'
            const lw = 1 / SCALE
            ctx.lineWidth = lw
            ctx.strokeRect(
                selected.x + lw / 2,
                selected.y + lw / 2,
                1 - lw,
                1 - lw
            )
        }
        
        if (player) {
            ctx.strokeStyle = 'white'
            const lw = 1 / SCALE
            ctx.lineWidth = lw

            const cx = player.x + 0.5
            const cy = player.y + 0.5
            const armLengthPx = Math.round(0.35 * SCALE)   // whole device pixels
            const armLength = armLengthPx / SCALE           // back into canvas-unit space

            ctx.beginPath()
            ctx.moveTo(cx - armLength, cy + lw / 2)
            ctx.lineTo(cx + armLength, cy + lw / 2)
            ctx.moveTo(cx + lw / 2, cy - armLength)
            ctx.lineTo(cx + lw / 2, cy + armLength)
            ctx.stroke()
        }
        ctx.restore()
    }

    function cellHasRegion(cellX, cellY, rid) {
        if (cellX < 0 || cellX >= dimensions.width || cellY < 0 || cellY >= dimensions.height) {
            return false   // off-grid counts as "not in the region" — draws a border at the map's edge
        }
        const base = (cellY * dimensions.width + cellX) * maxRegionsPerCell
        for (let d = 0; d < maxRegionsPerCell; d++) {
            const id = regionMap[base + d]
            if (id === noRegionId) break
            if (id === rid) return true
        }
        return false
    }

    useEffect(() => {
        if (!dimensions || !regionMap || !regionLookup) return
        drawRegionBorders()
    }, [dimensions, regionMap, regionLookup])

    function drawRegionBorders() {
        const ctx = overlayRef.current.getContext('2d')
        ctx.clearRect(0, 0, dimensions.width * SCALE, dimensions.height * SCALE)

        ctx.save()
        ctx.scale(SCALE, SCALE)

        const segmentsByColour = new Map()

        for (let y = 0; y < dimensions.height; y++) {
            for (let x = 0; x < dimensions.width; x++) {
                const base = (y * dimensions.width + x) * maxRegionsPerCell
                for (let d = 0; d < maxRegionsPerCell; d++) {
                    const rid = regionMap[base + d]
                    if (rid === noRegionId) break

                    const region = regionLookup[rid]
                    if (!region) continue
                    const colourKey = `rgb(${255},${255},${255})`
                    if (!segmentsByColour.has(colourKey)) segmentsByColour.set(colourKey, [])
                    const segments = segmentsByColour.get(colourKey)

                    if (!cellHasRegion(x, y - 1, rid)) segments.push([x, y, x + 1, y])
                    if (!cellHasRegion(x, y + 1, rid)) segments.push([x, y + 1, x + 1, y + 1])
                    if (!cellHasRegion(x - 1, y, rid)) segments.push([x, y, x, y + 1])
                    if (!cellHasRegion(x + 1, y, rid)) segments.push([x + 1, y, x + 1, y + 1])
                }
            }
        }

        const lw = 1 / SCALE
        ctx.lineWidth = lw

        for (const [colour, segments] of segmentsByColour) {
            ctx.strokeStyle = colour
            ctx.beginPath()
            for (const [x1, y1, x2, y2] of segments) {
                if (y1 === y2) {
                    // horizontal segment — nudge y onto a device-pixel center
                    const y = y1 + lw / 2
                    ctx.moveTo(x1, y)
                    ctx.lineTo(x2, y)
                } else {
                    // vertical segment — nudge x onto a device-pixel center
                    const x = x1 + lw / 2
                    ctx.moveTo(x, y1)
                    ctx.lineTo(x, y2)
                }
            }
            ctx.stroke()
        }

        ctx.restore()
    }

    // Convert mouse event coordinates to cell coordinates with clamping
    function eventToCell(e) {
        const rect = interactionRef.current.getBoundingClientRect()
        const cellX = Math.min(
            dimensions.width - 1,
            Math.max(0, Math.floor((e.clientX - rect.left) * (dimensions.width / rect.width)))
        )
        const cellY = Math.min(
            dimensions.height - 1,
            Math.max(0, Math.floor((e.clientY - rect.top) * (dimensions.height / rect.height)))
        )
        return { cellX, cellY }
    }

    function getBiomeDataAtCell(cellX, cellY) {
        const index = cellY * dimensions.width + cellX
        return biomeLookup[biomeMap[index]]
    }

    function getRegionDataAtCell(cellX, cellY) {
        const base = (cellY * dimensions.width + cellX) * maxRegionsPerCell
        const regions = []
        for (let d = 0; d < maxRegionsPerCell; d++) {
            const rid = regionMap[base + d]
            if (rid === noRegionId) break   // slots are filled front-to-back, so first NO_REGION means no more follow
            regions.push(regionLookup[rid])
        }
        return regions
    }

    function getCellData(cellX, cellY) {
        const biomeData = getBiomeDataAtCell(cellX, cellY)
        const regionData = getRegionDataAtCell(cellX, cellY)
        return { x: cellX, y: cellY, biomeData: biomeData, regionData: regionData }
    }

    function isNewHoveredCell(cellX, cellY) {
        return !lastHoveredCell || lastHoveredCell.x !== cellX || lastHoveredCell.y !== cellY
    }

    async function handlePlayerMove(cellX, cellY) {
        const res = await fetch('/api/player/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x: cellX, y: cellY })
        })
        if (!res.ok) {
            console.error('Failed to move player:', await res.text())
            return
        }
        const data = await res.json()
        setVersion(data.version)
        onPlayerLocationChange({ x: data.player_location[1], y: data.player_location[0] })
    }

    function handleHover(e) {
        if (!biomeMap || !biomeLookup || !dimensions) return
        
        const { cellX, cellY } = eventToCell(e)

        let cellData
        if (isNewHoveredCell(cellX, cellY)) {
            cellData = getCellData(cellX, cellY)
            setLastHoveredCell(cellData)
            drawInteractionLayer({ x: cellX, y: cellY }, selectedCell, playerLocation)
        }
        else {
            cellData = lastHoveredCell
        }
        
        setTooltip({ x: e.clientX, y: e.clientY, biomeName: cellData.biomeData.name })
    }

    function handleWheel(e) {
        e.preventDefault()

        const rect = e.currentTarget.getBoundingClientRect()
        const mouseX = e.clientX - rect.left
        const mouseY = e.clientY - rect.top

        const zoomFactor = e.deltaY < 0 ? 1.1 : 1 / 1.1
        const newZoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, zoom * zoomFactor))

        // keep the point under the cursor fixed on screen while zooming
        const worldX = (mouseX - pan.x) / zoom
        const worldY = (mouseY - pan.y) / zoom

        setPan({
            x: mouseX - worldX * newZoom,
            y: mouseY - worldY * newZoom
        })
        setZoom(newZoom)
    }

    function handleMouseLeave() {
        setTooltip(null)
        drawInteractionLayer(null, selectedCell, playerLocation)
    }

    function handleClick(e) {
        if (!dimensions || !biomeMap || !biomeLookup) return

        const { cellX, cellY } = eventToCell(e)

        if (interactionMode === 'move') {
            handlePlayerMove(cellX, cellY)
        }
        else {
            onCellSelect(getCellData(cellX, cellY))
        }
    }

    
    function handlePanStart(e) {
        if (e.button !== 1) return 
        e.preventDefault()
        isPanning.current = true
        lastPanPos.current = { x: e.clientX, y: e.clientY }
    }

    function handlePanMove(e) {
        if (!isPanning.current) return
        const dx = e.clientX - lastPanPos.current.x
        const dy = e.clientY - lastPanPos.current.y
        setPan((prev) => ({ x: prev.x + dx, y: prev.y + dy }))
        lastPanPos.current = { x: e.clientX, y: e.clientY }
    }

    function handlePanEnd() {
        isPanning.current = false
    }

    return (
        <div className="map-viewport" 
            onWheel={handleWheel}
            onMouseDown={handlePanStart}
            onMouseMove={handlePanMove}
            onMouseUp={handlePanEnd}
            onMouseLeave={handlePanEnd}
        >
            <div
                className="map-stack"
                style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }}
            >
                <canvas ref={baseMapRef} className="map-layer" />
                <canvas ref={overlayRef} className="map-layer" />
                <canvas ref={interactionRef} className="map-layer"
                    onMouseMove={handleHover}
                    onMouseLeave={handleMouseLeave}
                    onClick={handleClick}
                />
            </div>

            <MapToolbar
                interactionMode={interactionMode}
                onInteractionModeChange={setInteractionMode}
            />

            {tooltip && (
                <div
                    className="tooltip capitalise"
                    style={{ left: tooltip.x + 4, top: tooltip.y - 20 }}
                >
                    {tooltip.biomeName}
                </div>
            )}
        </div>
    )
}

export default MapDisplay