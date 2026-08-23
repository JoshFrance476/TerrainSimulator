export function hexToRgb(hex) {
    const n = parseInt(hex.slice(1), 16)
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
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