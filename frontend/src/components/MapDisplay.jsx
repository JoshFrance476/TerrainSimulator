import { useState, useRef, useEffect } from 'react'
import { useWorldData } from '../hooks/useWorldData'

function MapDisplay({ selectedCell, onCellSelect }) {
    const baseMapRef = useRef(null) //base map canvas - RBG map
    const overlayRef = useRef(null) //overlay canvas - regions
    const interactionRef = useRef(null) //interaction canvas - hovered cell, selected cell, tooltip
    const imageDataRef = useRef(null) // ImageData object containing Uint8Array RGB map data

    const { version, dimensions, maxRegionsPerCell, noRegionId, 
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

    // Resize the canvases when the dimensions change
    useEffect(() => {
        if (!dimensions) return
        for (const ref of [baseMapRef, overlayRef]) {
            ref.current.width = dimensions.width
            ref.current.height = dimensions.height
        }

        interactionRef.current.width = dimensions.width * SCALE
        interactionRef.current.height = dimensions.height * SCALE
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
        drawInteractionLayer(lastHoveredCell, selectedCell)
    }, [selectedCell, dimensions])

    // Draw hovered cell and selected cell on interaction layer
    function drawInteractionLayer(hovered, selected) {
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

    function handleHover(e) {
        if (!biomeMap || !biomeLookup || !dimensions) return
        
        const { cellX, cellY } = eventToCell(e)

        let cellData
        if (isNewHoveredCell(cellX, cellY)) {
            cellData = getCellData(cellX, cellY)
            setLastHoveredCell(cellData)
            drawInteractionLayer({ x: cellX, y: cellY }, selectedCell)
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
        drawInteractionLayer(null, selectedCell)
    }

    function handleClick(e) {
        if (!dimensions || !biomeMap || !biomeLookup) return

        const { cellX, cellY } = eventToCell(e)
        onCellSelect(getCellData(cellX, cellY))
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