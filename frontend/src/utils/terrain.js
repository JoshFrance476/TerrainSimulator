// utils/terrain.js
import { createNoise2D } from 'simplex-noise'

// returns Float32Array of length width * height, values roughly 0–1
export function generateNoiseMap({ width, height, scale = 64, seed }) {
    const noise2D = seed === undefined
        ? createNoise2D()
        : createNoise2D(mulberry32(seed))

    const map = new Float32Array(width * height)

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const v = noise2D(x / scale, y / scale)   // -1 to 1
            map[y * width + x] = (v + 1) / 2          // 0 to 1
        }
    }

    return map
}

// small seeded PRNG — simplex-noise takes any () => number in [0, 1)
function mulberry32(seed) {
    let a = seed >>> 0
    return function () {
        a = (a + 0x6D2B79F5) | 0
        let t = Math.imul(a ^ (a >>> 15), 1 | a)
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296
    }
}

// octaves: layered detail. persistence < 1 makes each octave quieter.
export function generateFractalNoiseMap({
    width, height, scale = 64, octaves = 4,
    persistence = 0.5, lacunarity = 2, seed,
}) {
    const noise2D = seed === undefined
        ? createNoise2D()
        : createNoise2D(mulberry32(seed))

    const map = new Float32Array(width * height)
    let min = Infinity
    let max = -Infinity

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            let value = 0
            let amplitude = 1
            let frequency = 1 / scale

            for (let o = 0; o < octaves; o++) {
                value += noise2D(x * frequency, y * frequency) * amplitude
                amplitude *= persistence
                frequency *= lacunarity
            }

            const i = y * width + x
            map[i] = value
            if (value < min) min = value
            if (value > max) max = value
        }
    }

    // normalise to 0–1 using the actual range, not the theoretical one
    const span = max - min || 1
    for (let i = 0; i < map.length; i++) {
        map[i] = (map[i] - min) / span
    }

    return map
}