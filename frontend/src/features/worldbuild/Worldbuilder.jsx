import { useState, useRef, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import WorldbuilderWindow from './WorldbuilderWindow'
import MapDisplay from '../../components/MapDisplay'
import './worldbuilder.css'
import {
    createWorld, refreshAll, generateTerrain, getCellRegions, NO_REGION,
    getBrushIndexes, paintBiome, paintDetail, alterElevation, smoothElevation, flattenElevation, writeRegion, removeRegion, buildRegionBorders, writeComponent, removeComponent, buildComponentBorders, mergeSegmentMaps,
} from '../../utils/world-editing'
import { useSaveEditorWorldMutation, editorWorldKey, fetchEditorWorld } from '../../queries/queries'

function Worldbuilder({ initialWorldId = null }) {
    const [worldId, setWorldId] = useState(initialWorldId)
    const [dimensions, setDimensions] = useState({ width: 768, height: 512 })
    const worldRef = useRef(null)

    const [imageData, setImageData] = useState(null)
    const [biomeBrush, setBiomeBrush] = useState(null)
    const [detailBrush, setDetailBrush] = useState(null)
    const [elevationEditType, setElevationEditType] = useState(null)   // 'layer', 'continuous', 'flatten', 'smoothing'
    const [regionBrush, setRegionBrush] = useState(null)
    const [brushRadius, setBrushRadius] = useState(4)
    const [componentBrush, setComponentBrush] = useState(null)

    const [biomeLookup, setBiomeLookup] = useState({})
    const [regionLookup, setRegionLookup] = useState({})
    const [detailLookup, setDetailLookup] = useState({})
    const [componentLookup, setComponentLookup] = useState({})

    const [borderSegments, setBorderSegments] = useState(null)

    const strokeCells = useRef(new Set())

    const strokeStartLocation = useRef(null)

    const saveWorldMutation = useSaveEditorWorldMutation()

    const queryClient = useQueryClient()

    useEffect(() => {
        if (worldId != null) {
            loadWorld(worldId)
            return
        }
        setupBlankWorld()
    }, [dimensions, worldId])


    function setupBlankWorld() {
        const world = createWorld({ ...dimensions })
        refreshAll(world)
        worldRef.current = world
        setBiomeLookup(world.biomeLookup)
        setRegionLookup(world.regionLookup)
        setDetailLookup(world.detailLookup)
        setComponentLookup(world.componentLookup)
        commit()
    }

    async function loadWorld(id) {
        const data = await queryClient.fetchQuery({
            queryKey: editorWorldKey(id),
            queryFn: () => fetchEditorWorld(id),
            staleTime: Infinity,
        })

        const world = createWorld({
            width: data.width,
            height: data.height,
            startingLocation: data.starting_location,
            biomeLookup: data.biome_lookup,
            regionLookup: data.region_lookup,
            biome: Uint8Array.fromBase64(data.biome),
            elevation: Uint8Array.fromBase64(data.elevation),
            region: Uint8Array.fromBase64(data.region),
            detail: Uint8Array.fromBase64(data.detail),
            detailLookup: data.detail_lookup,
            component: Uint8Array.fromBase64(data.component),
            componentLookup: data.component_lookup,
        })
        refreshAll(world)
        worldRef.current = world
        setBiomeLookup(world.biomeLookup)
        setRegionLookup(world.regionLookup)
        setDetailLookup(world.detailLookup)
        setComponentLookup(world.componentLookup)
        setBorderSegments(mergeSegmentMaps(
            buildRegionBorders(worldRef.current, world.regionLookup),
            buildComponentBorders(worldRef.current, world.componentLookup),
        ))  
        commit()
    }
    

    function buildBorders() {
        const world = worldRef.current
        setBorderSegments(mergeSegmentMaps(
            buildRegionBorders(world, regionLookup),
            buildComponentBorders(world, componentLookup),
        ))
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
        } if (componentBrush !== null) {
            if (button === 0) {
                for (const index of indexes) {
                    writeComponent(world, index, componentBrush)
                }
            } else if (button === 2) {
                for (const index of indexes) {
                    removeComponent(world, index)
                }
            }
            buildBorders()
        }
        commit()
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
        const detail = world.detailLookup[world.detail[index]]?.name ?? null
        const elevation = world.elevation[index]

        const regions = [...getCellRegions(world, index)]
            .filter((id) => id !== NO_REGION)
            .map((id) => regionLookup[id]?.title)
        
        const component = world.componentLookup[world.component[index]]?.name ?? null

        const parts = [biome]
        if (detail) parts.push(`${detail}`)
        parts.push(`x: ${cellX}, y: ${cellY}`)
        parts.push(`Elevation: ${elevation}`)

        parts.push(`Regions: ${regions.join(', ') || 'None'}`)
        parts.push(`Component: ${component}`)

        return parts
    }

    function startStroke({ cellX, cellY }) {
        strokeStartLocation.current = { x: cellX, y: cellY }
        strokeCells.current.clear()
    }

    function addBiome(biome) {
        const next = { ...biomeLookup, [Object.keys(biomeLookup).length]: biome }
        setBiomeLookup(next)
        worldRef.current.biomeLookup = next
    }

    function editBiome({ biomeBrush, name, colour }) {
        const next = { ...biomeLookup }
        if (biomeBrush !== null && next[biomeBrush]) {
            next[biomeBrush] = { ...next[biomeBrush], name, colour }
        }
        setBiomeLookup(next)
        worldRef.current.biomeLookup = next
        refreshAll(worldRef.current)
        commit()
    }

    function addDetail(detail) {
        // +1 is a cheap fix for the lookup table starting at 1 instead of 0, with 0 being reserved for "no detail"
        const next = {...detailLookup, [Object.keys(detailLookup).length+1]: detail }
        setDetailLookup(next)
        worldRef.current.detailLookup = next
    }

    function addRegion(region) {
        const next = { ...regionLookup, [Object.keys(regionLookup).length]: region }
        setRegionLookup(next)
        worldRef.current.regionLookup = next
    }

    function addComponent(component) {
        const next = { ...componentLookup, [Object.keys(componentLookup).length+1]: component }
        setComponentLookup(next)
        worldRef.current.componentLookup = next
    }

    function setStartingLocation(location) {
        worldRef.current.startingLocation = location
        commit()
    }

    function saveWorld(name, description) {
        const worldData = {
                name: name,
                description: description,
                width: worldRef.current.width,
                height: worldRef.current.height,
                starting_location: worldRef.current.startingLocation,
                biome: worldRef.current.biome.toBase64(),
                elevation: new Uint8Array(worldRef.current.elevation).toBase64(),
                region: worldRef.current.region.toBase64(),
                colour: new Uint8Array(worldRef.current.rgba).toBase64(),
                biome_lookup: worldRef.current.biomeLookup,
                region_lookup: worldRef.current.regionLookup,
                detail_lookup: worldRef.current.detailLookup,
                component_lookup: worldRef.current.componentLookup,
                detail: worldRef.current.detail.toBase64(),
                component: worldRef.current.component.toBase64(),
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
                editBiome={editBiome}
                setBrushRadius={setBrushRadius}
                setElevationEditType={setElevationEditType}
                elevationEditType={elevationEditType}
                addRegion={addRegion}
                regionLookup={regionLookup}
                regionBrush={regionBrush}
                setRegionBrush={setRegionBrush}
                saveWorld={saveWorld}
                saveWorldMutation={saveWorldMutation}
                setDetailBrush={setDetailBrush}
                detailLookup={detailLookup}
                addDetail={addDetail}
                detailBrush={detailBrush}
                addComponent={addComponent}
                setComponentBrush={setComponentBrush}
                componentLookup={componentLookup}
                componentBrush={componentBrush}
                setStartingLocation={setStartingLocation}
            />
            <MapDisplay
                imageData={imageData}
                onCellClick={() => {}}
                handleMouseDownDrag={handleCellInteraction}
                getScreenTooltipLabel={getTooltipLabel}
                onStrokeStart={startStroke}
                brushRadius={brushRadius}
                handleMouseDown={handleContinuousCellInteraction}
                borderSegments={borderSegments}
                initialZoom={2}
            />
        </div>
    )
}

export default Worldbuilder