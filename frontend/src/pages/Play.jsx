import StoryWindow from '../components/StoryWindow'
import MapDisplay from '../components/MapDisplay'
import InfoWindow from '../components/InfoWindow'
import Header from '../components/Header'
import AccountWindow from '../components/AccountWindow'
import { useWorld } from '../hooks/useWorld'
import { useState, useMemo } from 'react'
import { usePlayer } from '../hooks/usePlayer'
import MapToolbar from '../components/MapToolbar'
import { useMovePlayerMutation } from '../queries/queries'
import { buildBorderSegments } from '../utils/regions'
import { createWorld, refreshAll, getCellRegions } from '../utils/world-editing'


function Play({ user }) {
    const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
    const [interactionMode, setInteractionMode] = useState('view') // 'view' or 'move'

    const movePlayer = useMovePlayerMutation()
    const { playerLocation } = usePlayer()

    const { dimensions, maxRegionsPerCell, noRegionId, 
            biomeMap, biomeLookup, regionMap, regionLookup, elevationMap, detailMap, componentMap, detailLookup, componentLookup
    } = useWorld()

    const world = useMemo(() => {
        if (!dimensions || !biomeMap || !elevationMap || !regionMap) return null
        const w = createWorld({
            width: dimensions.width,
            height: dimensions.height,
            biomeLookup, regionLookup, detailLookup, componentLookup,
            biome: biomeMap,
            elevation: elevationMap,
            region: regionMap,
            detail: detailMap,
            component: componentMap,
        })
        refreshAll(w)
        return w
    }, [dimensions, biomeMap, elevationMap, regionMap, biomeLookup, regionLookup, detailMap, componentMap, detailLookup, componentLookup])

    const imageData = useMemo(
        () => world && new ImageData(world.rgba, world.width, world.height),
        [world]
    )

    function handleCellClick({x, y}) {
        if (interactionMode === 'move') {
            movePlayer.mutate({ x, y })
        } else {
            setSelectedCell(getCellData(x, y))
        }
    }

    const borderSegments = useMemo(
        () => dimensions && buildBorderSegments({
            regionMap,
            rows: dimensions.height,
            cols: dimensions.width,
            maxRegionsPerCell,
            noRegionId,
            regionLookup,
        }),
        [regionMap, dimensions, maxRegionsPerCell, noRegionId, regionLookup]
    )

    function getTooltipLabel({cellX, cellY}) {
        if (!biomeMap || !regionMap) return null
        const cellData = getCellData(cellX, cellY)
        const biomeName = cellData.biomeData?.name ?? 'Unknown Biome'
        const regionNames = cellData.regionData.map(r => r.title).join(', ') || 'No Regions'
        const componentName = cellData.componentData?.name ?? ''
        const detailName = cellData.detailData?.name ?? ''
        return [`${biomeName} | ${regionNames}` + (componentName ? ` | ${componentName}` : (detailName ? ` | ${detailName}` : ''))]
    }
    
    function getBiomeDataAtCell(cellX, cellY) {
        const index = cellY * dimensions.width + cellX
        return biomeLookup[biomeMap[index]]
    }

    function getDetailDataAtCell(cellX, cellY) {
        if (!detailMap) return null
        const index = cellY * dimensions.width + cellX
        return detailLookup[detailMap[index]]
    }

    function getComponentDataAtCell(cellX, cellY) {
        if (!componentMap) return null
        const index = cellY * dimensions.width + cellX
        return componentLookup[componentMap[index]]
    }

    function getRegionDataAtCell(cellX, cellY) {
        const index = cellY * dimensions.width + cellX
        return [...getCellRegions(world, index)]
            .filter((id) => id !== noRegionId)
            .map((id) => regionLookup[id])
    }

    function getCellData(cellX, cellY) {
        const biomeData = getBiomeDataAtCell(cellX, cellY)
        const regionData = getRegionDataAtCell(cellX, cellY)
        const detailData = getDetailDataAtCell(cellX, cellY)
        const componentData = getComponentDataAtCell(cellX, cellY)
        return { x: cellX, y: cellY, biomeData: biomeData, regionData: regionData, detailData: detailData, componentData: componentData }
    }

    function getCellsToHover({ cellX, cellY }) {
        if (!world) return null
        const index = cellY * world.width + cellX
        const cid = world.component[index]
        if (cid === 0) return new Set([index])
        return world.componentLocations[cid] ?? new Set([index])
    }



    return (
        <>
            <div className="display">
                <StoryWindow user={user} />
                <InfoWindow 
                    selectedCell={selectedCell} 
                />
                <MapDisplay
                    imageData={imageData}
                    borderSegments={borderSegments}
                    onCellClick={handleCellClick}
                    getMouseTooltipLabel={getTooltipLabel}
                    selectedCell={selectedCell}
                    playerLocation={playerLocation}
                    getHoveredCells={getCellsToHover}
                > 
                    <MapToolbar interactionMode={interactionMode} onInteractionModeChange={setInteractionMode} />
                </MapDisplay>
            </div>
        </>
    )
}

export default Play