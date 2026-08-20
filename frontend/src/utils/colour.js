export function hexToRgb(hex) {
    const n = parseInt(hex.slice(1), 16)
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

export function rgbToHex(r, g, b) {
    return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')
}


export function buildColourLookup(biomes) {
    const lookup = new Float32Array(biomes.length * 3)
    biomes.forEach(({ colour }, id) => {
        lookup[id * 3] = colour.h
        lookup[id * 3 + 1] = colour.s
        lookup[id * 3 + 2] = colour.v
    })
    return lookup
}


// Computes one cell's colour from the terrain rules and writes it
// into `rgba` at cell index i. Reads elevation/steepness/biome at i.
export function writeCellColour({
    i, elevation, steepness, biome, rgba,
    colourLookup, oceanId, mountainsId, variation = true,
}) {
    const id = biome[i]
    const c = id * 3
    const h = colourLookup[c]
    let s = colourLookup[c + 1]
    let v = colourLookup[c + 2]

    if (id === oceanId) {
        let f = steepness[i] * 0.2
        s = s * (1 - f)
        v = v * (1 - f)

        f = (Math.min(elevation[i], 0) + 1) / 2
        s = s * (1 - f) + 0.37 * f
        v = v * (1 - f) + 1.0 * f
    } else if (variation) {
        if (id === mountainsId) {
            let f = steepness[i] * 0.3
            s = s * (1 - f)
            v = v * (1 - f)

            f = elevation[i] / 2
            s = s * (1 - f)
            v = v * (1 - f) + 0.4 * f
        } else {
            let f = steepness[i] * 0.3
            s = s * (1 - f)
            v = v * (1 - f) + 0.2 * f

            f = elevation[i] / 4
            s = s * (1 - f)
            v = v * (1 - f) + 0.8 * f
        }
    }

    const hue = ((h % 360) + 360) % 360
    s = Math.min(1, Math.max(0, s))
    v = Math.min(1, Math.max(0, v))

    const sector = hue / 60
    const k = Math.floor(sector)
    const frac = sector - k
    const p = v * (1 - s)
    const q = v * (1 - s * frac)
    const t = v * (1 - s * (1 - frac))

    let r, g, b
    switch (k % 6) {
        case 0: r = v; g = t; b = p; break
        case 1: r = q; g = v; b = p; break
        case 2: r = p; g = v; b = t; break
        case 3: r = p; g = q; b = v; break
        case 4: r = t; g = p; b = v; break
        default: r = v; g = p; b = q; break
    }

    const o = i * 4
    rgba[o] = r * 255
    rgba[o + 1] = g * 255
    rgba[o + 2] = b * 255
    rgba[o + 3] = 255
}

export function generateColourMapRGBA({
    elevation, steepness, biome,
    colourLookup, oceanId, mountainsId, variation = true,
}) {
    const n = biome.length
    const rgba = new Uint8ClampedArray(n * 4)

    const cell = {
        i: 0, elevation, steepness, biome, rgba,
        colourLookup, oceanId, mountainsId, variation,
    }

    for (let i = 0; i < n; i++) {
        cell.i = i
        writeCellColour(cell)
    }

    return rgba
}

// amount 0–1: 0 = unchanged, 1 = white
export function lighten(r, g, b, amount) {
    return [
        r + (255 - r) * amount,
        g + (255 - g) * amount,
        b + (255 - b) * amount,
    ]
}

// amount 0–1: 0 = unchanged, 1 = black
export function darken(r, g, b, amount) {
    const f = 1 - amount
    return [r * f, g * f, b * f]
}