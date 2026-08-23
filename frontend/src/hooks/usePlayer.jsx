import { useMemo } from 'react'
import { usePlayerQuery } from '../queries/queries'

export function usePlayer() {
    const query = usePlayerQuery()
    const location = query.data ?? null

    return { playerLocation: location, isLoading: query.isLoading, isError: query.isError }
}