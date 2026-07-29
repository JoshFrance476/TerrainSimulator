
import { createContext, useContext } from 'react'
import { useWorldData } from '../hooks/useWorldData'

const WorldDataContext = createContext(null)

export function WorldDataProvider({ children }) {
    const worldData = useWorldData()
    return (
        <WorldDataContext.Provider value={worldData}>
            {children}
        </WorldDataContext.Provider>
    )
}

export function useWorldDataContext() {
    const context = useContext(WorldDataContext)
    if (context === null) {
        throw new Error('useWorldDataContext must be used inside a WorldDataProvider')
    }
    return context
}