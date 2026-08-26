
import { hexToRgb, lighten, darken } from './colour'
import { generateFractalNoiseMap } from './terrain'

export const SEA_LEVEL = 6
export const MOUNTAIN_LEVEL = 44

export const BIOME_LOOKUP = {
    0: { name: 'ocean', colour: '#0000ff' },
    1: { name: 'plains', colour: '#019201' },
    2: { name: 'mountains', colour: '#888888' }
}

export const DETAIL_LOOKUP = {
    1: { name: "path", colour: '#a76d03', height: -1 },
}

export const NO_REGION = 255
export const MAX_REGIONS_PER_CELL = 4

export const NO_COMPONENT = 0


export function createWorld({ width, height, biome, elevation, region, rgba, biomeLookup, regionLookup, detail, detailLookup, component, componentLookup }) {
    const cells = width * height
    const componentMap = component ?? new Uint8Array(cells).fill(NO_COMPONENT)
    return {
        width,
        height,
        biome: biome ?? new Uint8Array(cells),
        elevation: elevation ? new Uint8ClampedArray(elevation) : new Uint8ClampedArray(cells).fill(SEA_LEVEL),
        rgba: rgba ? new Uint8ClampedArray(rgba) : new Uint8ClampedArray(cells * 4),
        region: region ?? new Uint8Array(cells * 4).fill(NO_REGION),
        biomeLookup: biomeLookup ?? BIOME_LOOKUP,
        regionLookup: regionLookup ?? {},
        highlight: new Uint8Array(cells),
        detail: detail ?? new Uint8Array(cells),
        detailLookup: detailLookup ?? DETAIL_LOOKUP,
        component: componentMap,
        componentLookup: componentLookup ?? {},
        componentLocations: buildComponentLocations(componentMap),
    }
}

// ---------------------------------------------------------------- cells


export function updateBiome(world, index) {
    const e = world.elevation[index]
    world.biome[index] = e < SEA_LEVEL ? 0 : e > MOUNTAIN_LEVEL ? 2 : 1
}

export function updateHighlight(world, index) {
    if (world.biome[index] === 0) {
        const elevation = world.elevation[index]
        if (elevation > SEA_LEVEL-2) {
            world.highlight[index] = 1
        } else if (elevation > SEA_LEVEL-3) {
            world.highlight[index] = 3
        } else {
            world.highlight[index] = 2
        }
    }  else {
        const up = index - world.width
        if (up < 0) {
            world.highlight[index] = 0
            return
        }
        const above = world.elevation[up]
        const here = world.elevation[index]
        world.highlight[index] = above < here ? 1 : above > here ? 2 : 0
    }
}

export function writeCell(world, index) {
    const colour = world.detailLookup[world.detail[index]]?.colour
        ?? world.biomeLookup[world.biome[index]]?.colour
        ?? '#000000';
    let [r, g, b] = hexToRgb(colour);

    if (world.highlight[index] === 1) {
        [r, g, b] = lighten(r, g, b, 0.2)
    } else if (world.highlight[index] === 2) {
        [r, g, b] = darken(r, g, b, 0.2)
    }

    const p = index * 4
    world.rgba[p] = r
    world.rgba[p + 1] = g
    world.rgba[p + 2] = b
    world.rgba[p + 3] = 255
}

export function refreshCell(world, index) {
    updateHighlight(world, index)
    writeCell(world, index)
}

export function refreshAll(world) {
    for (let i = 0; i < world.biome.length; i++) {
        refreshCell(world, i)
    }
}

// ---------------------------------------------------------------- brush


export function getBrushOutline(radius) {
    const rSq = radius * radius
    const inBrush = (dx, dy) => dx * dx + dy * dy <= rSq

    const segments = []
    for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
            if (!inBrush(dx, dy)) continue
            if (!inBrush(dx, dy - 1)) segments.push([dx, dy, dx + 1, dy])
            if (!inBrush(dx, dy + 1)) segments.push([dx, dy + 1, dx + 1, dy + 1])
            if (!inBrush(dx - 1, dy)) segments.push([dx, dy, dx, dy + 1])
            if (!inBrush(dx + 1, dy)) segments.push([dx + 1, dy, dx + 1, dy + 1])
        }
    }
    return segments
}


export function getBrushIndexes(world, x, y, radius) {
    const indexes = []
    const rSq = radius * radius
    for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
            if (dx * dx + dy * dy > rSq) continue
            const bx = x + dx
            const by = y + dy
            if (bx < 0 || bx >= world.width || by < 0 || by >= world.height) continue
            indexes.push(by * world.width + bx)
        }
    }
    return indexes
}

export function paintBiome(world, indexes, biomeId) {
    for (const index of indexes) {
        world.biome[index] = biomeId
        refreshCell(world, index)
    }

}

export function paintDetail(world, indexes, detailId) {
    for (const index of indexes) {
        world.detail[index] = detailId
        refreshCell(world, index)
    }
}

export function alterElevation(world, indexes, amount = 1) {
    for (const index of indexes) {
        world.elevation[index] += amount
    }
    refreshElevationEdit(world, indexes)
}

export function smoothElevation(world, indexes) {
    const { width, height } = world
    const source = world.elevation.slice()   // read from a snapshot so the pass doesn't feed on itself

    for (const index of indexes) {
        const x = index % width
        const y = (index / width) | 0

        let total = source[index]
        let count = 1

        if (y > 0)          { total += source[index - width]; count++ }
        if (y < height - 1) { total += source[index + width]; count++ }
        if (x > 0)          { total += source[index - 1];     count++ }
        if (x < width - 1)  { total += source[index + 1];     count++ }

        world.elevation[index] = total / count
    }

    refreshElevationEdit(world, indexes)
}

export function flattenElevation(world, indexes, targetHeight) {
    for (const index of indexes) {
        world.elevation[index] = targetHeight
    }
    refreshElevationEdit(world, indexes)
}

// an elevation change alters the highlight of the edited cell and the one below it
function refreshElevationEdit(world, indexes) {
    const cells = world.biome.length
    for (const index of indexes) {
        updateBiome(world, index)
        refreshCell(world, index)
        const below = index + world.width
        if (below < cells) refreshCell(world, below)
    }
}

// ---------------------------------------------------------------- components

export function writeComponent(world, index, componentId) {
    const previous = world.component[index]
    if (previous === componentId) return
    if (previous !== NO_COMPONENT) removeComponentLocation(world.componentLocations, index, previous)
    world.component[index] = componentId
    addComponentLocation(world.componentLocations, index, componentId)
}

export function removeComponent(world, index) {
    const previous = world.component[index]
    if (previous === NO_COMPONENT) return
    world.component[index] = NO_COMPONENT
    removeComponentLocation(world.componentLocations, index, previous)
}

export function addComponentLocation(componentLocations, index, componentId) {
    (componentLocations[componentId] ??= new Set()).add(index)
}

export function removeComponentLocation(componentLocationsDict, index, componentId) {
    const locations = componentLocationsDict[componentId]
    if (!locations) return
    locations.delete(index)
    if (locations.size === 0) delete componentLocationsDict[componentId]
}

export function buildComponentLocations(componentMap) {
    const locations = {}
    for (let index = 0; index < componentMap.length; index++) {
        const cid = componentMap[index]
        if (cid === NO_COMPONENT) continue
        (locations[cid] ??= new Set()).add(index)
    }
    return locations
}
// ---------------------------------------------------------------- regions

export function writeRegion(world, index, regionId) {
    const base = index * MAX_REGIONS_PER_CELL
    for (let s = 0; s < MAX_REGIONS_PER_CELL; s++) {
        const id = world.region[base + s]
        if (id === regionId) return true       // already present
        if (id === NO_REGION) {
            world.region[base + s] = regionId
            return true
        }
    }
    return false                                // cell full
}


export function removeRegion(world, index, regionId) {
    const base = index * MAX_REGIONS_PER_CELL
    for (let s = 0; s < MAX_REGIONS_PER_CELL; s++) {
        if (world.region[base + s] !== regionId) continue
        // shift the rest down so slots stay contiguous
        for (let k = s; k < MAX_REGIONS_PER_CELL - 1; k++) {
            world.region[base + k] = world.region[base + k + 1]
        }
        world.region[base + MAX_REGIONS_PER_CELL - 1] = NO_REGION
        return true
    }
    return false
}
    
export function getCellRegions(world, index) {
    const base = index * MAX_REGIONS_PER_CELL
    return world.region.subarray(base, base + MAX_REGIONS_PER_CELL)
}

export function hasRegion(world, index, regionId) {
    const base = index * MAX_REGIONS_PER_CELL
    for (let s = 0; s < MAX_REGIONS_PER_CELL; s++) {
        const id = world.region[base + s]
        if (id === NO_REGION) return false     // slots fill front-to-back
        if (id === regionId) return true
    }
    return false
}

export function buildRegionBorders(world, regionLookup) {
    const { width, height } = world
    const segmentsByColour = new Map()

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const index = y * width + x
            const base = index * MAX_REGIONS_PER_CELL

            for (let s = 0; s < MAX_REGIONS_PER_CELL; s++) {
                const rid = world.region[base + s]
                if (rid === NO_REGION) break        // slots fill front-to-back

                const region = regionLookup[rid]
                if (!region) continue

                let segments = segmentsByColour.get(region.colour)
                if (!segments) {
                    segments = []
                    segmentsByColour.set(region.colour, segments)
                }

                if (!cellHasRegion(world, x, y - 1, rid)) segments.push([x, y, x + 1, y])
                if (!cellHasRegion(world, x, y + 1, rid)) segments.push([x, y + 1, x + 1, y + 1])
                if (!cellHasRegion(world, x - 1, y, rid)) segments.push([x, y, x, y + 1])
                if (!cellHasRegion(world, x + 1, y, rid)) segments.push([x + 1, y, x + 1, y + 1])
            }
        }
    }

    return segmentsByColour
}

export function buildComponentBorders(world, componentLookup) {
    const { width, height } = world
    const segmentsByColour = new Map()

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const index = y * width + x
            const cid = world.component[index]
            if (cid === NO_COMPONENT) continue

            const component = componentLookup[cid]
            if (!component) continue

            let segments = segmentsByColour.get(component.colour)
            if (!segments) {
                segments = []
                segmentsByColour.set(component.colour, segments)
            }

            if (!cellIsComponent(world, x, y - 1, cid)) segments.push([x, y, x + 1, y])
            if (!cellIsComponent(world, x, y + 1, cid)) segments.push([x, y + 1, x + 1, y + 1])
            if (!cellIsComponent(world, x - 1, y, cid)) segments.push([x, y, x, y + 1])
            if (!cellIsComponent(world, x + 1, y, cid)) segments.push([x + 1, y, x + 1, y + 1])
        }
    }

    return segmentsByColour
}

// off-grid counts as "not in the component" — draws a border at the map's edge
function cellIsComponent(world, x, y, componentId) {
    if (x < 0 || x >= world.width || y < 0 || y >= world.height) return false
    return world.component[y * world.width + x] === componentId
}

// off-grid counts as "not in the region" — draws a border at the map's edge
function cellHasRegion(world, x, y, regionId) {
    if (x < 0 || x >= world.width || y < 0 || y >= world.height) return false
    return hasRegion(world, y * world.width + x, regionId)
}

export function mergeSegmentMaps(...maps) {
    const merged = new Map()
    for (const map of maps) {
        for (const [colour, segments] of map) {
            const existing = merged.get(colour)
            if (existing) existing.push(...segments)
            else merged.set(colour, [...segments])
        }
    }
    return merged
}

// ---------------------------------------------------------------- generation

export function generateTerrain(world, options = {}) {
    const { width, height } = world
    const noise = generateFractalNoiseMap({
        width, height, scale: 90, persistence: 0.38, lacunarity: 2, octaves: 8,
        ...options,
    })

    for (let i = 0; i < width * height; i++) {
        world.elevation[i] = Math.pow(noise[i], 3) *64
        updateBiome(world, i)
    }
    refreshAll(world)
}