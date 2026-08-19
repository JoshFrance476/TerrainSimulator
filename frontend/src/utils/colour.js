export function hexToRgb(hex) {
    const n = parseInt(hex.slice(1), 16)
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

export function rgbToHex(r, g, b) {
    return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')
}