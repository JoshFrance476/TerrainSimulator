
import { hexToRgb, lighten, darken } from './colour'
import { generateFractalNoiseMap } from './terrain'

export const SEA_LEVEL = 6
export const MOUNTAIN_LEVEL = 50

export const BIOME_LOOKUP = {
    0: { name: 'ocean', colour: '#0000ff' },
    1: { name: 'plains', colour: '#019201' },
    2: { name: 'mountains', colour: '#888888' },
    3: { name: "path", colour: '#a76d03'}
}


export function createWorld({ width, height, biomeLookup = BIOME_LOOKUP }) {
    const cells = width * height
    return {
        width,
        height,
        biome: new Uint8Array(cells),
        elevation: new Uint8ClampedArray(cells).fill(SEA_LEVEL),
        highlight: new Uint8Array(cells),
        rgba: new Uint8ClampedArray(cells * 4),
        biomeLookup: biomeLookup,
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
    const hex = world.biomeLookup[world.biome[index]]?.colour ?? '#000000'
    let [r, g, b] = hexToRgb(hex);

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

// biome-only edit: elevation is unchanged, so highlights stay valid
export function paintBiome(world, indexes, biomeId) {
    for (const index of indexes) {
        world.biome[index] = biomeId
        writeCell(world, index)
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