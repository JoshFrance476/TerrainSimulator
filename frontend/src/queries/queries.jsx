// src/queries/queries.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// ---------------------------------------------------------------- keys

export const worldKey = ['world']
export const biomeMapKey = ['biome-map']
export const biomeLookupKey = ['biome-lookup']
export const regionMapKey = ['region-map']
export const regionLookupKey = ['region-lookup']
export const rgbKey = ['rgb']
export const storyKey = ['story']
export const sceneKey = ['scene']
export const playerKey = ['player']
export const tokenUsageKey = ['token-usage']

// ---------------------------------------------------------------- fetchers

async function getJson(url) {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    return res.json()
}

async function getBuffer(url) {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    return res.arrayBuffer()
}

async function postJson(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    return res.json()
}

// ---------------------------------------------------------------- world

const binaryOptions = { structuralSharing: false}

export function useWorldQuery() {
    return useQuery({ 
        queryKey: worldKey, 
        queryFn: () => getJson('/api/world') 
    })
}

export function useBiomeLookupQuery() {
    return useQuery({
        queryKey: biomeLookupKey,
        queryFn: () => getJson('/api/world/biome-lookup'),
    })
}

export function useRegionLookupQuery() {
    return useQuery({
        queryKey: regionLookupKey,
        queryFn: () => getJson('/api/world/region-lookup'),
    })
}

export function useBiomeMapQuery() {
    return useQuery({
        queryKey: biomeMapKey,
        queryFn: async () => new Uint8Array(await getBuffer('/api/world/biome-map')),
        ...binaryOptions,
    })
}

export function useRegionMapQuery() {
    return useQuery({
        queryKey: regionMapKey,
        queryFn: async () => new Uint16Array(await getBuffer('/api/world/region-map')),
        ...binaryOptions,
    })
}

export function useRgbQuery() {
    return useQuery({
        queryKey: rgbKey,
        queryFn: async () => new Uint8ClampedArray(await getBuffer('/api/world/rgb')),
        ...binaryOptions,
    })
}

// ---------------------------------------------------------------- story & scene

export function useStoryQuery() {
    return useQuery({ 
        queryKey: storyKey, 
        queryFn: () => getJson('/api/story') 
    })
}

export function useSceneQuery() {
    return useQuery({
        queryKey: sceneKey,
        queryFn: () => getJson('/api/scene'),
    })
}

export function promptScene({ x, y }) {
    return postJson('/api/scene/prompt', { x, y })
}

export function usePlayerQuery() {
    return useQuery({ 
        queryKey: playerKey, 
        queryFn: () => getJson('/api/player') 
    })
}

export function useTokenUsageQuery() {
    return useQuery({
        queryKey: tokenUsageKey,
        queryFn: () => getJson('/api/token-usage'),
    })
}

// ---------------------------------------------------------------- mutations

export function useMovePlayerMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ x, y }) => postJson('/api/player/move', { x, y }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: playerKey }),
    })
}

export function useSubmitActionMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (action) => postJson('/api/scene/action', { action }),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: tokenUsageKey })
            queryClient.invalidateQueries({ queryKey: sceneKey })
            if (data.ended) {
                queryClient.invalidateQueries({ queryKey: storyKey })
                queryClient.invalidateQueries({ queryKey: regionMapKey })
                queryClient.invalidateQueries({ queryKey: regionLookupKey })
            }
        },
    })
}