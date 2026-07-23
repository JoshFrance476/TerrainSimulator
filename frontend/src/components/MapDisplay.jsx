import { useState, useRef, useEffect } from 'react'

function MapDisplay({ selectedCell, onCellSelect }) {
    const baseMapRef = useRef(null) //base map canvas - RBG map
    const overlayRef = useRef(null) //overlay canvas - regions
    const interactionRef = useRef(null) //interaction canvas - hovered cell, selected cell, tooltip
    const imageDataRef = useRef(null) // ImageData object containing Uint8Array RGB map data
    const [version, setVersion] = useState(0) 
    const [dimensions, setDimensions] = useState(null) // shape: {width, height}

    const [lastHoveredCell, setLastHoveredCell] = useState(null) // shape: {x, y, biomeData}

    const [biomeMap, setBiomeMap] = useState(null)  // Uint8Array of biome IDs
    const [biomeLookup, setBiomeLookup] = useState(null) // Dict mapping biome IDs to biome data

    const [tooltip, setTooltip] = useState(null) //shape: {x, y, biomeName}

    const SCALE = 4 // Scale factor for rendering map interaction layer

    // Fetch biome lookup data from backend
    useEffect(() => {
        async function fetchBiomeLookup() {
            const res = await fetch('/api/world/biome-lookup')
            if (!res.ok) {
                console.error('Failed to fetch biome lookup data', await res.text())
                return
            }
            const data = await res.json()
            setBiomeLookup(data)
        }
        fetchBiomeLookup()
    }, [])

    // Fetch biome map data from backend
    useEffect(() => {
        async function fetchBiomeMap() {
            const res = await fetch('/api/world/biome-map?v=${version}')
        
            if (!res.ok) {
                console.error('Failed to fetch biome map data', await res.text())
                return
            }
            const buffer = await res.arrayBuffer()
            const data = new Uint8Array(buffer)
            setBiomeMap(data)
        }
        fetchBiomeMap()
    }, [version])

    // Fetch the world data from the backend on component mount
    useEffect(() => {
        async function fetchWorld() {
            const res = await fetch('/api/world')
            const data = await res.json()
            setVersion(data.version)
            setDimensions({ width: data.cols, height: data.rows })
        }
        fetchWorld()
    }, [])


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
            ctx.lineWidth = 1 / SCALE
            ctx.strokeRect(selected.x + 0.5 / SCALE, selected.y + 0.5 / SCALE, 1, 1)
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

    function isNewHoveredCell(cellX, cellY) {
        return !lastHoveredCell || lastHoveredCell.x !== cellX || lastHoveredCell.y !== cellY
    }

    function handleHover(e) {
        if (!biomeMap || !biomeLookup || !dimensions) return
        
        const { cellX, cellY } = eventToCell(e)

        let biomeData
        if (isNewHoveredCell(cellX, cellY)) {
            biomeData = getBiomeDataAtCell(cellX, cellY)
            setLastHoveredCell({ x: cellX, y: cellY, biomeData: biomeData })
            drawInteractionLayer({ x: cellX, y: cellY }, selectedCell)
        }
        else {
            biomeData = lastHoveredCell.biomeData
        }
        
        setTooltip({ x: e.clientX, y: e.clientY, biomeName: biomeData.name })
    }

    function handleMouseLeave() {
        setTooltip(null)
        drawInteractionLayer(null, selectedCell)
    }

    function handleClick(e) {
        if (!dimensions || !biomeMap || !biomeLookup) return

        const { cellX, cellY } = eventToCell(e)
        const biomeData = getBiomeDataAtCell(cellX, cellY)

        onCellSelect({ x: cellX, y: cellY, biomeData: biomeData })

        console.log(`Biome: ${biomeData.name} at (${cellX}, ${cellY})`)
    }

    function handleBrushStart() {
        
    }

    return (
        <div className="map-stack">
            <canvas ref={baseMapRef} className="map-layer" />
            <canvas ref={overlayRef} className="map-layer" />
            <canvas ref={interactionRef} className="map-layer"
                onMouseMove={handleHover}
                onMouseLeave={handleMouseLeave}
                onClick={handleClick}
                onMouseDown={handleBrushStart}
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