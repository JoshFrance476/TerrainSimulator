import { useState, useRef, useEffect } from 'react'
import WorldbuilderWindow from '../components/WorldbuilderWindow'
import MapDisplay from '../components/MapDisplay'
import './worldbuilder.css'
import {
    BIOME_LOOKUP, createWorld, refreshAll, generateTerrain, getCellRegions, NO_REGION,
    getBrushIndexes, paintBiome, alterElevation, smoothElevation, flattenElevation, writeRegion, removeRegion, buildRegionBorders
} from '../utils/world-editing'

function Worldbuilder() {
    const [dimensions, setDimensions] = useState({ width: 768, height: 512 })
    const worldRef = useRef(null)

    const [imageData, setImageData] = useState(null)
    const [biomeBrush, setBiomeBrush] = useState(null)
    const [elevationEditType, setElevationEditType] = useState(null)   // 'layer', 'continuous', 'flatten', 'smoothing'
    const [regionBrush, setRegionBrush] = useState(255)
    const [brushRadius, setBrushRadius] = useState(4)

    const [biomeLookup, setBiomeLookup] = useState(BIOME_LOOKUP)
    const [regionLookup, setRegionLookup] = useState({})

    const [borderSegments, setBorderSegments] = useState(null)

    const strokeCells = useRef(new Set())

    const strokeStartLocation = useRef(null)

    useEffect(() => {
        const world = createWorld({ ...dimensions, biomeLookup })
        refreshAll(world)
        worldRef.current = world
        commit()
    }, [dimensions])

    useEffect(() => {
        if (worldRef.current) {
            worldRef.current.biomeLookup = biomeLookup
        }
    }, [biomeLookup])

    useEffect(() => {
        if (worldRef.current) {
            worldRef.current.regionLookup = regionLookup
        }
    }, [regionLookup])

    function buildBorders() {
        setBorderSegments(buildRegionBorders(worldRef.current, regionLookup))
    }

    // hand the mutated buffer back to React as a new ImageData wrapper
    function commit() {
        const world = worldRef.current
        setImageData(new ImageData(world.rgba, world.width, world.height))
    }

    function handleGenerate(options) {
        generateTerrain(worldRef.current, options)
        commit()
    }

    function handleCellInteraction({ cellX, cellY }, button) {
        const world = worldRef.current
        const indexes = getBrushIndexes(world, cellX, cellY, brushRadius)

        if (elevationEditType === 'layer') {
            const fresh = indexes.filter((i) => !strokeCells.current.has(i))
            for (const i of fresh) strokeCells.current.add(i)
            if (fresh.length) {
                if (button === 0) {
                    alterElevation(world, fresh, 1)
                } else if (button === 2) {
                    alterElevation(world, fresh, -1)
                }
            }
        } else if (elevationEditType === 'smoothing') {
            smoothElevation(world, indexes)
        } else if (elevationEditType === "flatten") {
            if (strokeStartLocation.current) {
                flattenElevation(world, indexes, world.elevation[strokeStartLocation.current.y * world.width + strokeStartLocation.current.x])
            }
        } else if (biomeBrush !== null) {
            paintBiome(world, indexes, biomeBrush)
        } else if (regionBrush !== null) {
            if (button === 0) {
                for (const index of indexes) {
                    writeRegion(world, index, regionBrush)
                }
            } else if (button === 2) {
                for (const index of indexes) {
                    removeRegion(world, index, regionBrush)
                }
            }
            buildBorders()
            commit()
        }
    }

    function handleContinuousCellInteraction({ cellX, cellY }, button) {
        const world = worldRef.current
        const indexes = getBrushIndexes(world, cellX, cellY, brushRadius)
        if (elevationEditType === 'continuous') {
            if (button === 0) {
                alterElevation(world, indexes, 1)
            } else if (button === 2) {
                alterElevation(world, indexes, -1)
            }
        }
        commit()
    }

    function getTooltipLabel({ cellX, cellY }) {
        const world = worldRef.current
        if (!world) return null

        const index = cellY * world.width + cellX

        const biome = world.biomeLookup[world.biome[index]]?.name ?? 'Unknown'
        const elevation = world.elevation[index]

        const regions = [...getCellRegions(world, index)]
            .filter((id) => id !== NO_REGION)
            .map((id) => regionLookup[id]?.name ?? `region ${id}`)

        return `${biome} | Elevation: ${elevation} | Regions: ${regions.join(', ') || 'None'}`
    }

    function startStroke({ cellX, cellY }) {
        strokeStartLocation.current = { x: cellX, y: cellY }
        strokeCells.current.clear()
    }

    function addBiome(biome) {
        const next = { ...biomeLookup, [Object.keys(biomeLookup).length]: biome }
        setBiomeLookup(next)
    }

    function addRegion(region) {
        const next = { ...regionLookup, [Object.keys(regionLookup).length]: region }
        setRegionLookup(next)
    }

    return (
        <div className="display">
            <WorldbuilderWindow
                biomeLookup={biomeLookup}
                setBiomeBrush={setBiomeBrush}
                biomeBrush={biomeBrush}
                generateRandomMap={handleGenerate}
                addBiome={addBiome}
                setBrushRadius={setBrushRadius}
                setElevationEditType={setElevationEditType}
                elevationEditType={elevationEditType}
                addRegion={addRegion}
                regionLookup={regionLookup}
                regionBrush={regionBrush}
                setRegionBrush={setRegionBrush}
            />
            <MapDisplay
                imageData={imageData}
                onCellClick={() => {}}
                handleMouseDownDrag={handleCellInteraction}
                getTooltipLabel={getTooltipLabel}
                onStrokeStart={startStroke}
                brushRadius={brushRadius}
                handleMouseDown={handleContinuousCellInteraction}
                borderSegments={borderSegments}
            />
        </div>
    )
}

export default Worldbuilder