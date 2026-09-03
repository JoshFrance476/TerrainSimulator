// src/queries/queries.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// ---------------------------------------------------------------- keys

export const worldKey = ['world']
export const biomeMapKey = ['biome-map']
export const biomeLookupKey = ['biome-lookup']
export const regionMapKey = ['region-map']
export const regionLookupKey = ['region-lookup']
export const elevationMapKey = ['elevation-map']
export const storyKey = ['story']
export const sceneKey = ['scene']
export const playerKey = ['player']
export const tokenUsageKey = ['token-usage']
export const modelKey = ['model']
export const worldsKey = ['worlds']
export const sessionKey = ['session']
export const detailMapKey = ['detail-map']
export const componentMapKey = ['component-map']
export const detailLookupKey = ['detail-lookup']
export const componentLookupKey = ['component-lookup']

export const editorWorldKey = (worldId) => ['editor-world', worldId]


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
    if (!res.ok) {
        const detail = await res.json().catch(() => null)
        throw new Error(detail?.detail ?? `${url} failed: ${res.status}`)
    }
    return res.json()
}

// ---------------------------------------------------------------- world

const binaryOptions = { structuralSharing: false}


export function useNewSessionMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (worldId) => postJson('/api/session', { world_id: worldId }),
        onSuccess: () => queryClient.resetQueries({
            predicate: (query) => query.queryKey[0] !== worldsKey[0],
        }),
    })
}

export function useSessionSetupMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ 
            worldDescription, 
            character, 
            storyFocus,
            regionLookup,
            componentLookup,
        }) => postJson('/api/session/submit-setup', { 
            world_description: worldDescription, 
            character_description: character, 
            story_description: storyFocus, 
            region_lookup: regionLookup, 
            component_lookup: componentLookup 
        }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: sessionKey }),
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
        queryFn: async () => new Uint8Array(await getBuffer('/api/world/region-map')),
        ...binaryOptions,
    })
}

export function useElevationMapQuery() {
    return useQuery({
        queryKey: elevationMapKey,
        queryFn: async () => new Uint8ClampedArray(await getBuffer('/api/world/elevation-map')),
        ...binaryOptions,
    })
}

export function useDetailMapQuery() {
    return useQuery({
        queryKey: detailMapKey,
        queryFn: async () => new Uint8Array(await getBuffer('/api/world/detail-map')),
        ...binaryOptions,
    })
}

export function useComponentMapQuery() {
    return useQuery({
        queryKey: componentMapKey,
        queryFn: async () => new Uint8Array(await getBuffer('/api/world/component-map')),
        ...binaryOptions,
    })
}

export function useDetailLookupQuery() {
    return useQuery({
        queryKey: detailLookupKey,
        queryFn: () => getJson('/api/world/detail-lookup'),
    })
}

export function useComponentLookupQuery() {
    return useQuery({
        queryKey: componentLookupKey,
        queryFn: () => getJson('/api/world/component-lookup'),
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
    return postJson('/api/scene/generate-interaction', { x, y })
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

// ---------------------------------------------------------------- editor

export function useSaveEditorWorldMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (worldData) => {
            return putJson('/api/editor/save-world', worldData)
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey: worldsKey }),
    })
}

export const fetchEditorWorld = (worldId) => getJson(`/api/load-world/${worldId}`)

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

export function useGenerateSceneSummaryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => postJson('/api/scene/generate-summary', {}),
    onError: (err) => console.error('Summary failed:', err),
    onSuccess: () => {
        queryClient.invalidateQueries({queryKey: sceneKey})
        queryClient.invalidateQueries({queryKey: storyKey})
        queryClient.invalidateQueries({queryKey: tokenUsageKey})
    }
  })
}