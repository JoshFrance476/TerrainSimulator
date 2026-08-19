import MapDisplay from '../components/MapDisplay'
import { useEditorWorldMetadataQuery, useEditorBiomeMapQuery, useEditorRGBMapQuery, useEditorRegionMapQuery } from '../queries/queries'
import { useRef, useEffect, useState, useMemo } from 'react'
import { hexToRgb, rgbToHex } from '../utils/colour'
import { buildBorderSegments } from '../utils/regions'
import EditorWindow from '../components/EditorWindow'
import Header from '../components/Header'

function Editor({ worldId }) {
    const { data: metadata } = useEditorWorldMetadataQuery(worldId)
    const { data: cachedBiomeMap } = useEditorBiomeMapQuery(worldId)
    const { data: cachedRGBMap } = useEditorRGBMapQuery(worldId)
    const { data: cachedRegionMap } = useEditorRegionMapQuery(worldId)

    const biomeMapRef = useRef(null)
    const rgbMapRef = useRef(null)
    const regionMapRef = useRef(null)

    const [imageData, setImageData] = useState(null)

    const [borderSegments, setBorderSegments] = useState(null)

    const [interactionType, setInteractionType] = useState('brush') // 'brush', 'eyedropper'
    const [brushColour, setBrushColour] = useState('#ff0000')
    const [colourPresets, setColourPresets] = useState([])


    useEffect(() => {
        if (!cachedBiomeMap || !cachedRGBMap || !cachedRegionMap || !metadata) return
        biomeMapRef.current = cachedBiomeMap.slice()  
        rgbMapRef.current = cachedRGBMap.slice()       
        regionMapRef.current = cachedRegionMap.slice() 

        setImageData(new ImageData(rgbMapRef.current, metadata.cols, metadata.rows))

        buildBorders()

    }, [cachedBiomeMap, cachedRGBMap, cachedRegionMap, metadata])

    function addColourPreset(colour) {
        setColourPresets(prev => {
            if (prev.includes(colour)) return prev
            return [...prev, colour]
        })
    }


    function buildBorders() {
        setBorderSegments(
            buildBorderSegments({
                regionMap: regionMapRef.current,
                rows: metadata.rows,
                cols: metadata.cols,
                maxRegionsPerCell: metadata.max_regions_per_cell,
                noRegionId: metadata.no_region_id,
                regionLookup: metadata.region_list,
        }))
    }

    function getCellColour({cellX, cellY}) {
        if (!rgbMapRef.current || !metadata) return null
        const index = (cellY * metadata.cols + cellX) * 4
        const r = rgbMapRef.current[index]
        const g = rgbMapRef.current[index + 1]
        const b = rgbMapRef.current[index + 2]
        return rgbToHex(r, g, b)
    }

    function handleMouseDownDrag({cellX, cellY}) {
        if (interactionType === 'brush') {
            paintCell({cellX, cellY})
        }
        else if (interactionType === 'eyedropper') {
            let colour = getCellColour({cellX, cellY})
            setBrushColour(colour)
            addColourPreset(colour)
            setInteractionType('brush')
        }
    }

    function paintCell({cellX, cellY}) {
        if (!rgbMapRef.current || !metadata || !brushColour) return
            const [r, g, b] = hexToRgb(brushColour)
            const index = (cellY * metadata.cols + cellX) * 4
            rgbMapRef.current[index] = r
            rgbMapRef.current[index + 1] = g
            rgbMapRef.current[index + 2] = b
            rgbMapRef.current[index + 3] = 255
            setImageData(new ImageData(rgbMapRef.current, metadata.cols, metadata.rows))
    }


    return (
        <div className="display">
            <EditorWindow 
                interactionType={interactionType}
                brushColour={brushColour}
                colourPresets={colourPresets}
                setBrushColour={setBrushColour}
                setInteractionType={setInteractionType}
            />
            <MapDisplay
                imageData={imageData}
                borderSegments={borderSegments}
                getTooltipLabel={() => null}
                onCellClick={paintCell}
                handleMouseDownDrag={handleMouseDownDrag}
            />
        </div>
    )
}

export default Editor