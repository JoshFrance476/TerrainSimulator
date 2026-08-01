import {
    useStoryQuery
} from '../queries/queries'

export function useStory() {
    const storyQuery = useStoryQuery()
    return {
        characterHistory: storyQuery.data?.character_history,
        questsList: storyQuery.data?.quests_list,
        outputTokens: storyQuery.data?.output_tokens ?? 0,
        inputTokens: storyQuery.data?.input_tokens ?? 0,
        isLoading: storyQuery.isLoading,
        isError: storyQuery.isError,
    }
}
