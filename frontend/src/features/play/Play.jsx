import StoryWindow from './StoryWindow'
import MapDisplay from '../../components/MapDisplay'
import InfoWindow from './InfoWindow'
import { useWorld } from '../../hooks/useWorld'
import { useState, useMemo, useRef, useEffect } from 'react'
import { usePlayer } from '../../hooks/usePlayer'
import MapToolbar from './MapToolbar'
import { useMovePlayerMutation } from '../../queries/queries'
import { buildBorderSegments } from '../../utils/regions'
import { getCellRegions } from '../../utils/world-editing'

const MOVE_INTERVAL_MS = 150; 

const DELTAS = {
        KeyW:       { x:  0, y: -1 },
        KeyS:       { x:  0, y:  1 },
        KeyA:       { x: -1, y:  0 },
        KeyD:       { x:  1, y:  0 },
        ArrowUp:    { x: 0,  y: -1 },
        ArrowDown:  { x: 0,  y:  1 },
        ArrowLeft:  { x: -1, y:  0 },
        ArrowRight: { x: 1,  y:  0 },
    };

function Play({ user }) {
    const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
    const [interactionMode, setInteractionMode] = useState('view') // 'view' or 'move'

    const movePlayer = useMovePlayerMutation()
    const player = usePlayer()

    const { world, maxRegionsPerCell, noRegionId, isLoading } = useWorld()

    const heldKeysRef = useRef(new Set());
    const intervalRef = useRef(null);

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

    function handleKeyDown(event) {
        if (event.ctrlKey || event.metaKey || event.altKey) return;

        if (!DELTAS[event.code]) return;
        event.preventDefault();
        if (heldKeysRef.current.has(event.code)) return;
        heldKeysRef.current.add(event.code);
        movePlayer.mutate(DELTAS[event.code]);
        startRepeat();
    }

    function handleKeyUp(event) {
        heldKeysRef.current.delete(event.code)
        if (heldKeysRef.current.size === 0) stopRepeat();
    }

    function handleUnfocus() {
        heldKeysRef.current.clear();
        stopRepeat();
    }

    useEffect(() => stopRepeat, []);

    useEffect(() => {
        const id = setInterval(() => {
            const code = Array.from(heldKeysRef.current).at(-1);
            if (!code) return;
            movePlayer.mutate(DELTAS[code]);
        }, MOVE_INTERVAL_MS);

        return () => clearInterval(id);
    }, [movePlayer]);

    function stopRepeat() {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
    }

    function startRepeat() {
        stopRepeat();                       // restart the clock from now
        intervalRef.current = setInterval(() => {
            const code = Array.from(heldKeysRef.current).at(-1);
            if (!code) return;
            movePlayer.mutate(DELTAS[code]);
        }, MOVE_INTERVAL_MS);
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
                    revealed_tiles={player.revealed_tiles}
                    initialZoom={16}
                    handleKeyDown={handleKeyDown}
                    handleKeyUp={handleKeyUp}
                    handleUnfocus={handleUnfocus}
                > 
                    <MapToolbar interactionMode={interactionMode} onInteractionModeChange={setInteractionMode} />
                </MapDisplay>
            </div>
        </>
    )
}

export default Play