import StoryWindow from './StoryWindow'
import MapDisplay from '../../components/MapDisplay'
import InfoWindow from './InfoWindow'
import { useWorld } from '../../hooks/useWorld'
import { useState, useMemo } from 'react'
import { usePlayer } from '../../hooks/usePlayer'
import MapToolbar from './MapToolbar'
import { useMovePlayerMutation } from '../../queries/queries'
import { buildBorderSegments } from '../../utils/regions'
import { getCellRegions } from '../../utils/world-editing'


function Play({ user }) {
    const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
    const [interactionMode, setInteractionMode] = useState('view') // 'view' or 'move'

    const movePlayer = useMovePlayerMutation()
    const player = usePlayer()

    const { world, maxRegionsPerCell, noRegionId, isLoading } = useWorld()


    const imageData = useMemo(
        () => world && new ImageData(world.rgba, world.width, world.height),
        [world]
    )

    function handleCellClick({x, y}) {
        if (interactionMode === 'move') {
            movePlayer.mutate({ x, y })
        } else {
            setSelectedCell(getCellData(world, x, y, noRegionId))
        }
    }

    const borderSegments = useMemo(
        () => world && buildBorderSegments({
            regionMap: world.region,
            rows: world.height,
            cols: world.width,
            maxRegionsPerCell,
            noRegionId,
            regionLookup: world.regionLookup,
        }),
        [world, maxRegionsPerCell, noRegionId]
    )

    function getCellData(world, cellX, cellY, noRegionId) {
        const index = cellY * world.width + cellX
        return {
            x: cellX,
            y: cellY,
            biomeData: world.biomeLookup[world.biome[index]],
            detailData: world.detailLookup[world.detail[index]],
            componentData: world.componentLookup[world.component[index]],
            regionData: [...getCellRegions(world, index)]
                .filter((id) => id !== noRegionId)
                .map((id) => world.regionLookup[id]),
        }
    }

    function getTooltipLabel({ cellX, cellY }) {
        if (!world) return null
        const cellData = getCellData(world, cellX, cellY, noRegionId)
        const biomeName = cellData.biomeData?.name ?? 'Unknown Biome'
        const regionNames = cellData.regionData.map(r => r.title).join(', ')
        const componentName = cellData.componentData?.name ?? null
        const detailName = cellData.detailData?.name ?? null
        return [(componentName ?? detailName ?? biomeName) + (regionNames.length > 0 ? ` | ${regionNames}` : '')]
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
                    player={player}
                />
                <MapDisplay
                    imageData={imageData}
                    borderSegments={borderSegments}
                    onCellClick={handleCellClick}
                    getMouseTooltipLabel={getTooltipLabel}
                    selectedCell={selectedCell}
                    playerLocation={player.location}
                    getHoveredCells={getCellsToHover}
                > 
                    <MapToolbar interactionMode={interactionMode} onInteractionModeChange={setInteractionMode} />
                </MapDisplay>
            </div>
        </>
    )
}

export default Play