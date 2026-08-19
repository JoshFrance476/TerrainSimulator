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


function Play({ user }) {
    const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
    const [showAccountWindow, setShowAccountWindow] = useState(false)
    const [interactionMode, setInteractionMode] = useState('view') // 'view' or 'move'

    const movePlayer = useMovePlayerMutation()

    const { dimensions, maxRegionsPerCell, noRegionId, 
            biomeMap, biomeLookup, regionMap, regionLookup, rgbMap
    } = useWorld()

    const imageData = useMemo(() => {
        if (!rgbMap || !dimensions) return null
        return new ImageData(rgbMap, dimensions.width, dimensions.height)
    }, [rgbMap, dimensions])

    const { playerLocation } = usePlayer()

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
        return `${biomeName} | ${regionNames}`
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
                    getTooltipLabel={getTooltipLabel}
                    selectedCell={selectedCell}
                    playerLocation={playerLocation}
                >
                    <MapToolbar interactionMode={interactionMode} onInteractionModeChange={setInteractionMode} />
                </MapDisplay>
            </div>
        </>
    )
}

export default Play