import { useMemo } from 'react'
import {
    useWorldQuery,
    useBiomeMapQuery,
    useBiomeLookupQuery,
    useRegionMapQuery,
    useRegionLookupQuery,
    useElevationMapQuery,
    useDetailMapQuery,
    useComponentMapQuery,
    useDetailLookupQuery,
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

    // stable reference so `dimensions` can safely sit in effect dependency arrays
    const dimensions = useMemo(
        () => (world.data ? { width: world.data.width, height: world.data.height } : null),
        [world.data]
    )

    return {
        dimensions,
        maxRegionsPerCell: world.data?.max_regions_per_cell,
        noRegionId: world.data?.no_region_id,

        biomeMap: biomeMap.data,
        biomeLookup: biomeLookup.data ?? {},
        regionMap: regionMap.data,
        regionLookup: regionLookup.data ?? {},
        elevationMap: elevationMap.data,
        detailMap: detailMap.data,
        componentMap: componentMap.data,
        detailLookup: detailLookup.data ?? {},
        componentLookup: componentLookup.data ?? {},

        isLoading: queries.some((q) => q.isLoading),
        isFetching: queries.some((q) => q.isFetching),
        isError: queries.some((q) => q.isError),
        error: queries.find((q) => q.isError)?.error ?? null,
    }
}