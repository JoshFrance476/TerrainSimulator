import { usePlayerQuery } from '../queries/queries'

export function usePlayer() {
    const query = usePlayerQuery()
    const location = query.data?.location ?? null
    const stats = query.data?.stats ?? null
    const inventory = query.data?.inventory ?? null
    const notebook = query.data?.notebook ?? null

    return { location, stats, inventory, notebook, isLoading: query.isLoading, isError: query.isError }
}