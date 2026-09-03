// useWorld.jsx
import { useMemo } from 'react'
import { createWorld, refreshAll } from '../utils/world-editing'
import {
    useWorldQuery, useBiomeMapQuery, useBiomeLookupQuery,
    useRegionMapQuery, useRegionLookupQuery, useElevationMapQuery,
    useDetailMapQuery, useComponentMapQuery, useDetailLookupQuery,
    useComponentLookupQuery,
} from '../queries/queries'

export function useWorld() {
    const world = useWorldQuery()
    const biomeMap = useBiomeMapQuery()
    const biomeLookup = useBiomeLookupQuery()
    const regionMap = useRegionMapQuery()
    const regionLookup = useRegionLookupQuery()
    const elevationMap = useElevationMapQuery()
    const detailMap = useDetailMapQuery()
    const componentMap = useComponentMapQuery()
    const detailLookup = useDetailLookupQuery()
    const componentLookup = useComponentLookupQuery()

    const queries = [world, biomeMap, biomeLookup, regionMap, regionLookup, elevationMap, detailMap, componentMap, detailLookup, componentLookup]
    const isLoading = queries.some((q) => q.isLoading)

    const builtWorld = useMemo(() => {
        if (isLoading || !world.data) return null
        const w = createWorld({
            width: world.data.width,
            height: world.data.height,
            biomeLookup: biomeLookup.data ?? {},
            regionLookup: regionLookup.data ?? {},
            detailLookup: detailLookup.data ?? {},
            componentLookup: componentLookup.data ?? {},
            biome: biomeMap.data,
            elevation: elevationMap.data,
            region: regionMap.data,
            detail: detailMap.data,
            component: componentMap.data,
        })
        refreshAll(w)
        return w
    }, [isLoading, world.data, biomeMap.data, biomeLookup.data, regionMap.data, regionLookup.data, elevationMap.data, detailMap.data, componentMap.data, detailLookup.data, componentLookup.data])

    return {
        world: builtWorld,
        maxRegionsPerCell: world.data?.max_regions_per_cell,
        noRegionId: world.data?.no_region_id,
        regionMap: regionMap.data,       // still needed raw for buildBorderSegments
        regionLookup: regionLookup.data ?? {},
        isLoading,
        isFetching: queries.some((q) => q.isFetching),
        isError: queries.some((q) => q.isError),
        error: queries.find((q) => q.isError)?.error ?? null,
    }
}