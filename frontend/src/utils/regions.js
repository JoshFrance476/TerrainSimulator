// src/utils/regions.js

export function buildBorderSegments({
    regionMap,
    rows,
    cols,
    maxRegionsPerCell,
    noRegionId,
    regionLookup,
}) {
    if (!regionMap) return null

    const segmentsByColour = new Map()

    function cellHasRegion(x, y, rid) {
        // off-grid counts as "not in the region" — draws a border at the map's edge
        if (x < 0 || x >= cols || y < 0 || y >= rows) return false

        const base = (y * cols + x) * maxRegionsPerCell
        for (let d = 0; d < maxRegionsPerCell; d++) {
            const id = regionMap[base + d]
            if (id === noRegionId) break
            if (id === rid) return true
        }
        return false
    }

    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const base = (y * cols + x) * maxRegionsPerCell

            for (let d = 0; d < maxRegionsPerCell; d++) {
                const rid = regionMap[base + d]
                if (rid === noRegionId) break

                const region = regionLookup[rid]
                if (!region) continue

                const colourKey = 'rgb(255,255,255)'
                if (!segmentsByColour.has(colourKey)) segmentsByColour.set(colourKey, [])
                const segments = segmentsByColour.get(colourKey)

                if (!cellHasRegion(x, y - 1, rid)) segments.push([x, y, x + 1, y])
                if (!cellHasRegion(x, y + 1, rid)) segments.push([x, y + 1, x + 1, y + 1])
                if (!cellHasRegion(x - 1, y, rid)) segments.push([x, y, x, y + 1])
                if (!cellHasRegion(x + 1, y, rid)) segments.push([x + 1, y, x + 1, y + 1])
            }
        }
    }

    return segmentsByColour
}