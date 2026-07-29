import {useEffect, useState} from 'react'

export function useWorldData() {
    const [version, setVersion] = useState(0)
    const [dimensions, setDimensions] = useState(null)
    const [maxRegionsPerCell, setMaxRegionsPerCell] = useState(null)
    const [noRegionId, setNoRegionId] = useState(null)
    const [biomeMap, setBiomeMap] = useState(null)
    const [biomeLookup, setBiomeLookup] = useState({})
    const [regionMap, setRegionMap] = useState(null)
    const [regionLookup, setRegionLookup] = useState({})
    const [playerLocation, setPlayerLocation] = useState(null)

    // Fetch the world data from the backend on component mount
    useEffect(() => {
        async function fetchWorld() {
            const res = await fetch(`/api/world?v=${version}`)
            const data = await res.json()
            setVersion(data.version)
            setDimensions({ width: data.cols, height: data.rows })
            setMaxRegionsPerCell(data.max_regions_per_cell)
            setNoRegionId(data.no_region_id)
            setPlayerLocation(data.player_location)
        }
        fetchWorld()
    }, [])

    useEffect(() => {
        async function fetchBiomeLookup() {
            const res = await fetch(`/api/world/biome-lookup?v=${version}`)
            const data = await res.json()

            if (!res.ok) {
                console.error('Failed to fetch biome lookup:', await res.text())
                return
            }
            setBiomeLookup(data)
        }
        fetchBiomeLookup()
    }, [version])

    useEffect(() => {
        async function fetchBiomeMap() {
            const res = await fetch(`/api/world/biome-map?v=${version}`)

            if (!res.ok) {
                console.error('Failed to fetch biome map:', await res.text())
                return
            }
            const buffer = await res.arrayBuffer()
            setBiomeMap(new Uint8Array(buffer))
        }
        fetchBiomeMap()
    }, [version])

    useEffect(() => {
        async function fetchRegionLookup() {
            const res = await fetch(`/api/world/region-lookup?v=${version}`)
            const data = await res.json()

            if (!res.ok) {
                console.error('Failed to fetch region lookup:', await res.text())
                return
            }
            setRegionLookup(data)
        }
        fetchRegionLookup()
    }, [version])

    useEffect(() => {
        async function fetchRegionMap() {
            const res = await fetch(`/api/world/region-map?v=${version}`)
            if (!res.ok) {
                console.error('Failed to fetch region map:', await res.text())
                return
            }
            const buffer = await res.arrayBuffer()
            setRegionMap(new Uint16Array(buffer))
        }
        fetchRegionMap()
    }, [version])

    return {
        version,
        setVersion,
        dimensions,
        maxRegionsPerCell,
        noRegionId,
        biomeMap,
        biomeLookup,
        regionMap,
        regionLookup,
        playerLocation
    }
}