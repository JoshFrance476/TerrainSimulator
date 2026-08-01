import { useMemo } from 'react'
import { usePlayerQuery } from '../queries/queries'

export function usePlayer() {
    const query = usePlayerQuery()
    const location = query.data?.player_location

    // backend sends (row, col); frontend uses {x, y} = (col, row)
    const playerLocation = useMemo(
        () => (location ? { x: location[1], y: location[0] } : null),
        [location?.[0], location?.[1]]
    )

    return { playerLocation, isLoading: query.isLoading, isError: query.isError }
}