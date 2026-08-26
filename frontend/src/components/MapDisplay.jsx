import { useState, useRef, useEffect, useMemo } from 'react'
import { getBrushOutline } from '../utils/world-editing'


function MapDisplay({ imageData, borderSegments, onCellClick, getMouseTooltipLabel, getScreenTooltipLabel, handleMouseDown, handleMouseDownDrag, onStrokeStart, selectedCell, playerLocation = null, children, brushRadius, getHoveredCells }) {
    const baseMapRef = useRef(null) //base map canvas - RBG map
    const overlayRef = useRef(null) //overlay canvas - regions
    const interactionRef = useRef(null) //interaction canvas - hovered cell, selected cell, tooltip

    const [lastHoveredCell, setLastHoveredCell] = useState(null) // shape: {x, y, biomeData}
    const [hoveredCells, setHoveredCells] = useState([]) // shape: [{x, y}]

    const lastDrawn = useRef(null)

    const [mouseTooltip, setMouseTooltip] = useState(null) //shape: {x, y, list}
    const [screenTooltip, setScreenTooltip] = useState(null) //shape: {list}

    const SCALE = 4 // Interaction layer scale factor

    const [zoom, setZoom] = useState(5)
    const [pan, setPan] = useState({ x: 0, y: 0 })

    const MIN_ZOOM = 0.5
    const MAX_ZOOM = 25

    const isPanning = useRef(false)
    const lastPanPos = useRef({ x: 0, y: 0 })   

    const isPainting = useRef(false)

    const paintButton = useRef(null)

    const brushOutline = useMemo(
        () => (brushRadius ? getBrushOutline(brushRadius) : null),
        [brushRadius]
    )

    // Load RGB map into base map canvas when it changes
    useEffect(() => {
        if (!imageData) return

        baseMapRef.current.getContext('2d').putImageData(imageData, 0, 0)
    }, [imageData])

    // Redraw interaction layer
    useEffect(() => {
        drawInteractionLayer(hoveredCells, lastHoveredCell, selectedCell, playerLocation)
    }, [imageData, selectedCell, playerLocation, hoveredCells, lastHoveredCell])

    useEffect(() => {
        if (!imageData) return

        baseMapRef.current.width = imageData.width
        baseMapRef.current.height = imageData.height

        for (const ref of [overlayRef, interactionRef]) {
            ref.current.width = imageData.width * SCALE
            ref.current.height = imageData.height * SCALE
        }

        baseMapRef.current.getContext('2d').putImageData(imageData, 0, 0)
    }, [imageData?.width, imageData?.height])

    // Draw hovered cell and selected cell on interaction layer
    function drawInteractionLayer(hovered, hoveredCell, selected, player = null) {
        if (!imageData) return
        const ctx = interactionRef.current.getContext('2d')

        if (lastDrawn.current) {
            for (const { x, y, r = 0 } of lastDrawn.current) {
                const pad = r + 1
                ctx.clearRect(
                    (x - pad) * SCALE, (y - pad) * SCALE,
                    (pad * 2 + 1) * SCALE, (pad * 2 + 1) * SCALE
                )
            }
        }
        
        ctx.save()
        ctx.scale(SCALE, SCALE)
        
        const hoveredPoints = []
        if (hovered.size > 0) {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.35)'
            for (const index of hovered) {
                const x = index % imageData.width
                const y = (index / imageData.width) | 0
                hoveredPoints.push({ x, y })
                ctx.fillRect(x, y, 1, 1)
            }
        }
        if (hoveredCell && brushOutline) {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)'
            const lw = 1 / SCALE
            ctx.lineWidth = lw
            ctx.beginPath()
            for (const [x1, y1, x2, y2] of brushOutline) {
                if (y1 === y2) {
                    const y = hoveredCell.y + y1 + lw / 2
                    ctx.moveTo(hoveredCell.x + x1, y)
                    ctx.lineTo(hoveredCell.x + x2, y)
                } else {
                    const x = hoveredCell.x + x1 + lw / 2
                    ctx.moveTo(x, hoveredCell.y + y1)
                    ctx.lineTo(x, hoveredCell.y + y2)
                }
            }
            ctx.stroke()
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
        lastDrawn.current = [
            ...hoveredPoints,
            hoveredCell && { ...hoveredCell, r: brushRadius },
            selected,
            player,
        ].filter(Boolean)
    }

    useEffect(() => {
        if (!borderSegments) return
        drawRegionBorders(borderSegments)
    }, [borderSegments, zoom, imageData])

    function drawRegionBorders(segmentsByColour) {
        const canvas = overlayRef.current
        const ctx = canvas.getContext('2d')

        ctx.clearRect(0, 0, canvas.width, canvas.height)

        ctx.save()
        ctx.scale(SCALE, SCALE)

        const screenScale = canvas.getBoundingClientRect().width / canvas.width

        const lw = Math.max(1, 1 / screenScale) / SCALE
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
            imageData.width - 1,
            Math.max(0, Math.floor((e.clientX - rect.left) * (imageData.width / rect.width)))
        )
        const cellY = Math.min(
            imageData.height - 1,
            Math.max(0, Math.floor((e.clientY - rect.top) * (imageData.height / rect.height)))
        )
        return { cellX, cellY }
    }

    function isNewHoveredCell(cellX, cellY) {
        return !lastHoveredCell || lastHoveredCell.x !== cellX || lastHoveredCell.y !== cellY
    }

    function handleHover(e) {
        if (!imageData) return

        const { cellX, cellY } = eventToCell(e)

        const mouseTooltipLabel = getMouseTooltipLabel?.({ cellX, cellY }) ?? null
        const screenTooltipLabel = getScreenTooltipLabel?.({ cellX, cellY }) ?? null
        if (!mouseTooltipLabel) {
            setMouseTooltip(null)
        } else {
            setMouseTooltip({ x: e.clientX, y: e.clientY, data: mouseTooltipLabel })
        }

        if (!screenTooltipLabel) {
            setScreenTooltip(null)
        } else {
            setScreenTooltip({ data: screenTooltipLabel })
        }

        if (isPainting.current && handleMouseDown) {
            handleMouseDown(eventToCell(e), paintButton.current)
        }

        if (isNewHoveredCell(cellX, cellY)) {
            setLastHoveredCell({ x: cellX, y: cellY })
            setHoveredCells(getHoveredCells?.({ cellX, cellY }) ?? [])
            if (isPainting.current && handleMouseDownDrag) {
                handleMouseDownDrag(eventToCell(e), paintButton.current)
            }
        }
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
        setMouseTooltip(null)
        setHoveredCells([])
        setLastHoveredCell(null)
        setScreenTooltip(null)
    }

    function handleClick(e) {
        if (!imageData) return

        const { cellX, cellY } = eventToCell(e)
        onCellClick({ x: cellX, y: cellY })
    }
    
    function handlePanStart(e) {
        if (e.button === 1) {
            e.preventDefault()
            isPanning.current = true
            lastPanPos.current = { x: e.clientX, y: e.clientY }
        }
        else if (e.button === 0 || e.button === 2) {
            isPainting.current = true
            if (onStrokeStart) {
                onStrokeStart(eventToCell(e))
                paintButton.current = e.button
            }
            if (handleMouseDownDrag) {
                handleMouseDownDrag(eventToCell(e), paintButton.current)
            }
        }
    }

    function handlePanMove(e) {
        if (isPanning.current) {
            const dx = e.clientX - lastPanPos.current.x
            const dy = e.clientY - lastPanPos.current.y
            setPan((prev) => ({ x: prev.x + dx, y: prev.y + dy }))
            lastPanPos.current = { x: e.clientX, y: e.clientY }
        }
    }

    function handlePanEnd() {
        isPanning.current = false
        isPainting.current = false
    }

     return (
        <div className="map-viewport" 
            onWheel={handleWheel}
            onMouseDown={handlePanStart}
            onMouseMove={handlePanMove}
            onMouseUp={handlePanEnd}
            onMouseLeave={handlePanEnd}
            onContextMenu={(e) => e.preventDefault()}
        >
            <div
                className="map-stack"
                style={{
                    width: imageData ? imageData.width : 0,
                    height: imageData ? imageData.height : 0,
                    transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                }}
            >
                <canvas ref={baseMapRef} className="map-layer" />
                <canvas ref={overlayRef} className="map-layer" />
                <canvas ref={interactionRef} className="map-layer"
                    onMouseMove={handleHover}
                    onMouseLeave={handleMouseLeave}
                    onClick={handleClick}
                />
            </div>

            {children}

            {mouseTooltip && (
                <div
                    className="tooltip capitalise"
                    style={{ left: mouseTooltip.x + 4, top: mouseTooltip.y - 20 }}
                >
                    {mouseTooltip.data.map((line, index) => (
                        <div key={index}>{line}</div>
                    ))}
                </div>
            )}
            {screenTooltip && (
                <div
                    className="tooltip capitalise screen"
                >
                    {screenTooltip.data.map((line, index) => (
                        <div key={index}>{line}</div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default MapDisplay