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
export const modelKey = ['model']
export const worldsKey = ['worlds']
export const sessionKey = ['session']

// ---------------------------------------------------------------- fetchers

async function getJson(url) {
    const res = await fetch(url,  { credentials: 'include' })
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    return res.json()
}

async function getBuffer(url) {
    const res = await fetch(url,  { credentials: 'include' })
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    return res.arrayBuffer()
}

async function postJson(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'include',
    })
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    return res.json()
}

async function putJson(url, body) {
    const res = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'include',
    })
    if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
    if (res.status === 204) return null
    return res.json()
}

// ---------------------------------------------------------------- world

const binaryOptions = { structuralSharing: false}


export function useNewSessionMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (worldId) => postJson('/api/session', { world_id: worldId }),
        onSuccess: () => queryClient.resetQueries(),
    })
}

export function useWorldsQuery() {
  return useQuery({
    queryKey: worldsKey,
    queryFn: () => getJson('/api/worlds'),
    staleTime: Infinity,
  })
}

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

// ---------------------------------------------------------------- engine


export const promptTemplateKey = (name) => ['prompt-template', name]

export function usePromptTemplateQuery(name) {
    return useQuery({
        queryKey: promptTemplateKey(name),
        queryFn: () => getJson(`/api/scene/templates/${name}`),
    })
}

export function useSavePromptTemplateMutation(name) {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ text, temperature, max_tokens, reasoning_effort }) => putJson(`/api/scene/templates/${name}`, { text, temperature, max_tokens, reasoning_effort }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: promptTemplateKey(name) }),
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