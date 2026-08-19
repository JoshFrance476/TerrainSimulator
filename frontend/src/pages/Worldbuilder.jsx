import { useState, useRef, useEffect } from 'react'
import WorldbuilderWindow from '../components/WorldbuilderWindow'
import MapDisplay from '../components/MapDisplay'
import './worldbuilder.css'
import { hexToRgb, lighten, darken } from '../utils/colour'
import { generateFractalNoiseMap } from '../utils/terrain'


function Worldbuilder() {
    const seaLevel = 7
    const [dimensions, setDimensions] = useState({ width: 512, height: 512 })
    const biomeMapRef = useRef(new Uint8Array(dimensions.width * dimensions.height).fill(0))
    const elevationMapRef = useRef(new Uint8ClampedArray(dimensions.width * dimensions.height).fill(seaLevel))
    const rgbMapRef = useRef(new Uint8ClampedArray(dimensions.width * dimensions.height * 4))
    const highlightMapRef = useRef( new Uint8Array(dimensions.width * dimensions.height).fill(0))

    const biomeLookup = useRef({
        0: { name: 'ocean', colour: '#0000ff' },
        1: { name: 'plains', colour: '#019201' },
        2: { name: 'mountains', colour: '#888888' },
    })

    const [imageData, setImageData] = useState(null)

    const [biomeBrush, setBiomeBrush] = useState(1) 

    const [brushType, setBrushType] = useState('paint') // 'paint' or 'elevation'

    const [brushRadius, setBrushRadius] = useState(4)

    function generateRandomMap() {
        const { width, height } = dimensions
        const noise = generateFractalNoiseMap({width, height, scale: 64, persistence: 0.5, lacunarity: 2, octaves: 4})
        for (let i = 0; i < width * height; i++) {
            elevationMapRef.current[i] = (Math.pow(noise[i],2)) * 32
            if (elevationMapRef.current[i] < seaLevel) {
                biomeMapRef.current[i] = 0
            } else if (elevationMapRef.current[i] > 30) {
                biomeMapRef.current[i] = 2
            } else {
                biomeMapRef.current[i] = 1
            }
        }
        for (let i = 0; i < width * height; i++) {
            refreshCell(i)
        }
        setImageData(new ImageData(rgbMapRef.current, width, height))
    }

    useEffect(() => {
        const { width, height } = dimensions
        if (biomeMapRef.current.length !== width * height) {
            biomeMapRef.current = new Uint8Array(width * height)
        }
        rgbMapRef.current = new Uint8ClampedArray(width * height * 4)
        for (let i = 0; i < width * height; i++) {
            refreshCell(i)
        }
        setImageData(new ImageData(rgbMapRef.current, width, height))
    }, [dimensions])

    function updateHighlight(index) {
        const elevation = elevationMapRef.current[index]
        const up = getCellTopNeighbour(index, dimensions.width)

        if (up === -1) {
            highlightMapRef.current[index] = 0
            return
        }

        const above = elevationMapRef.current[up]
        highlightMapRef.current[index] = above < elevation ? 1 : above > elevation ? 2 : 0
    }

    function writeCell(index) {
        const hex = biomeLookup.current[biomeMapRef.current[index]]?.colour ?? '#000000'
        let [r, g, b] = hexToRgb(hex);

        if (highlightMapRef.current[index] === 1) {
            [r, g, b] = lighten(r, g, b, 0.2)
        } else if (highlightMapRef.current[index] === 2) {
            [r, g, b] = darken(r, g, b, 0.2)
        }

        const p = index * 4
        rgbMapRef.current[p] = r
        rgbMapRef.current[p + 1] = g
        rgbMapRef.current[p + 2] = b
        rgbMapRef.current[p + 3] = 255
    }

    function getCellTopNeighbour(index, cols) {
        const top = index - cols
        return top >= 0 ? top : -1
    }

    function refreshCell(index) {
        updateHighlight(index)
        writeCell(index)
    }
        


    function paintCell({x, y}) {
        if (x < 0 || x >= dimensions.width || y < 0 || y >= dimensions.height) return
        const indexes = getBrushIndexes({x, y})
        for (const index of indexes) {
            biomeMapRef.current[index] = biomeBrush
            writeCell(index)
        }
        setImageData(new ImageData(rgbMapRef.current, dimensions.width, dimensions.height))
    }

    function getBrushIndexes({x, y}) {
        const indexes = []
        for (let dy = -brushRadius; dy <= brushRadius; dy++) {
            for (let dx = -brushRadius; dx <= brushRadius; dx++) {
                const bx = x + dx
                const by = y + dy
                if (bx < 0 || bx >= dimensions.width || by < 0 || by >= dimensions.height) continue
                indexes.push(by * dimensions.width + bx)
            }
        }
        return indexes
    }

    function getTooltipLabel({cellX, cellY}) {
        return `Elevation: ${elevationMapRef.current[cellY * dimensions.width + cellX]}`
    }

    function handleCellInteraction({cellX, cellY}) {
        if (brushType === 'paint') {
            paintCell({x: cellX, y: cellY})
        } else if (brushType === 'elevation') {
            const indexes = getBrushIndexes({x: cellX, y: cellY})
            for (const index of indexes) {
                elevationMapRef.current[index]++
                refreshCell(index)
                const below = index + dimensions.width
                if (below < dimensions.width * dimensions.height) refreshCell(below)
                if (elevationMapRef.current[index] < seaLevel) {
                    biomeMapRef.current[index] = 0
                } else if (elevationMapRef.current[index] > 200) {
                    biomeMapRef.current[index] = 2
                } else {
                    biomeMapRef.current[index] = 1
                }
            }
            setImageData(new ImageData(rgbMapRef.current, dimensions.width, dimensions.height))
    }
    }



    return (
        <div className="display">
            <WorldbuilderWindow 
                biomeLookup={biomeLookup.current}
                setBiomeBrush={setBiomeBrush}
                setBrushType={setBrushType}
                brushType={brushType}
                biomeBrush={biomeBrush}
                generateRandomMap={generateRandomMap}
            />
            <MapDisplay
                imageData={imageData}
                onCellClick={() => {}}
                handleMouseDownDrag={({cellX, cellY}) => handleCellInteraction({cellX, cellY})}
                getTooltipLabel={getTooltipLabel}
            />
        </div>
    )
}

export default Worldbuilder