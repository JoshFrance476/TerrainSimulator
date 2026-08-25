import { useState, useRef, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import WorldbuilderWindow from '../components/WorldbuilderWindow'
import MapDisplay from '../components/MapDisplay'
import './worldbuilder.css'
import {
    createWorld, refreshAll, generateTerrain, getCellRegions, NO_REGION,
    getBrushIndexes, paintBiome, paintDetail, alterElevation, smoothElevation, flattenElevation, writeRegion, removeRegion, buildRegionBorders
} from '../utils/world-editing'
import { useSaveEditorWorldMutation, editorWorldKey, fetchEditorWorld } from '../queries/queries'

function Worldbuilder({ initialWorldId = null }) {
    const [worldId, setWorldId] = useState(initialWorldId)
    const [dimensions, setDimensions] = useState({ width: 768, height: 512 })
    const worldRef = useRef(null)

    const [imageData, setImageData] = useState(null)
    const [biomeBrush, setBiomeBrush] = useState(null)
    const [detailBrush, setDetailBrush] = useState(null)
    const [elevationEditType, setElevationEditType] = useState(null)   // 'layer', 'continuous', 'flatten', 'smoothing'
    const [regionBrush, setRegionBrush] = useState(255)
    const [brushRadius, setBrushRadius] = useState(4)

    const [biomeLookup, setBiomeLookup] = useState({})
    const [regionLookup, setRegionLookup] = useState({})
    const [detailLookup, setDetailLookup] = useState({})

    const [borderSegments, setBorderSegments] = useState(null)

    const strokeCells = useRef(new Set())

    const strokeStartLocation = useRef(null)

    const saveWorldMutation = useSaveEditorWorldMutation()

    const queryClient = useQueryClient()

    useEffect(() => {
        if (initialWorldId != null) {
            loadWorld(initialWorldId)
            return
        }
        const world = createWorld({ ...dimensions })
        refreshAll(world)
        worldRef.current = world
        setBiomeLookup(world.biomeLookup)
        setRegionLookup(world.regionLookup)
        setDetailLookup(world.detailLookup)
        commit()
    }, [dimensions])

    async function loadWorld(id) {
        const data = await queryClient.fetchQuery({
            queryKey: editorWorldKey(id),
            queryFn: () => fetchEditorWorld(id),
            staleTime: Infinity,
        })

        const world = createWorld({
            width: data.width,
            height: data.height,
            biomeLookup: data.biome_lookup,
            regionLookup: data.region_lookup,
            biome: Uint8Array.fromBase64(data.biome),
            elevation: Uint8Array.fromBase64(data.elevation),
            region: Uint8Array.fromBase64(data.region),
        })

        setWorldId(id)
        refreshAll(world)
        worldRef.current = world
        setBiomeLookup(world.biomeLookup)
        setRegionLookup(world.regionLookup)
        setDetailLookup(world.detailLookup)
        setBorderSegments(buildRegionBorders(worldRef.current, world.regionLookup))
        commit()
    }

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

    useEffect(() => {
        if (worldRef.current) {
            worldRef.current.detailLookup = detailLookup
        }
    }, [detailLookup])

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
        } if (elevationEditType === 'smoothing') {
            smoothElevation(world, indexes)
        } if (elevationEditType === "flatten") {
            if (strokeStartLocation.current) {
                flattenElevation(world, indexes, world.elevation[strokeStartLocation.current.y * world.width + strokeStartLocation.current.x])
            }
        } if (biomeBrush !== null) {
            paintBiome(world, indexes, biomeBrush)
        } if (detailBrush !== null) {
            paintDetail(world, indexes, detailBrush)
            const elevation = detailLookup[detailBrush].height
            // Cheap copy of layer elevation branch editing
            const fresh = indexes.filter((i) => !strokeCells.current.has(i))
            for (const i of fresh) strokeCells.current.add(i)
            if (fresh.length) {
                if (button === 0) {
                    alterElevation(world, fresh, elevation)
            }}
        } if (regionBrush !== null) {
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
            .map((id) => regionLookup[id]?.title)

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

    function addDetail(detail) {
        // +1 is a cheap fix for the lookup table starting at 1 instead of 0, with 0 being reserved for "no detail"
        const next = {...detailLookup, [Object.keys(detailLookup).length+1]: detail }
        setDetailLookup(next)
    }

    function addRegion(region) {
        const next = { ...regionLookup, [Object.keys(regionLookup).length]: region }
        setRegionLookup(next)
    }

    function saveWorld(name, description) {
        console.log("Saving world with name:", name, "and description:", description)
        const worldData = {
                name: name,
                description: description,
                width: worldRef.current.width,
                height: worldRef.current.height,
                biome: worldRef.current.biome.toBase64(),
                elevation: new Uint8Array(worldRef.current.elevation).toBase64(),
                region: worldRef.current.region.toBase64(),
                colour: new Uint8Array(worldRef.current.rgba).toBase64(),
                biome_lookup: worldRef.current.biomeLookup,
                region_lookup: worldRef.current.regionLookup,
                story_setup: {},
            }
        saveWorldMutation.mutate(worldData)
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
                saveWorld={saveWorld}
                saveWorldMutation={saveWorldMutation}
                loadWorld={loadWorld}
                setDetailBrush={setDetailBrush}
                detailLookup={detailLookup}
                addDetail={addDetail}
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