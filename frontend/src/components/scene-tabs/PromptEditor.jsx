import { useRef } from 'react'
import { usePromptTemplateQuery, useSavePromptTemplateMutation } from '../../queries/queries'

function PromptEditor({ name }) {
    const { data, isLoading, isError } = usePromptTemplateQuery(name)
    const save = useSavePromptTemplateMutation(name)
    const textRef = useRef(null)
    const temperatureRef = useRef(null)
    const maxTokensRef = useRef(null)
    const reasoningEffortRef = useRef(null)

    return (
        <div className="interaction-tab">
            <textarea
                className="prompt-textbox"
                defaultValue={data?.text ?? ''}
                placeholder={isLoading ? 'Loading prompt…' : ''}
                disabled={isLoading || isError}
                ref={textRef}
            />

            <div className="prompt-settings">
                <label htmlFor={`${name}-temperature`}>Temperature</label>
                <input 
                    id={`${name}-temperature`}
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    defaultValue={data?.temperature ?? ''}
                    disabled={isLoading || isError}
                    ref={temperatureRef}
                />

                <label htmlFor={`${name}-max-tokens`}>Max Tokens</label>
                <input 
                    id={`${name}-max-tokens`}
                    type="number"
                    step="100"
                    min="100"
                    defaultValue={data?.max_tokens ?? ''}
                    disabled={isLoading || isError}
                    ref={maxTokensRef}
                />

                <label htmlFor={`${name}-reasoning-effort`}>Reasoning Effort</label>
                <select 
                    id={`${name}-reasoning-effort`}
                    defaultValue={data?.reasoning_effort ?? ''}
                    disabled={isLoading || isError}
                    ref={reasoningEffortRef}

                    /* React only applies a select's defaultValue on mount, unlike an
                    input's — the key remounts it once the fetched value arrives. */
                    key={data?.reasoning_effort ?? 'loading'}
                >
                    <option value="none">None</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                </select>
            </div>

            <button
                type="button"
                onClick={() => save.mutate({
                    text: textRef.current.value,
                    temperature: Number(temperatureRef.current.value),
                    max_tokens: Number(maxTokensRef.current.value),
                    reasoning_effort: reasoningEffortRef.current.value,
                })}
                disabled={isLoading || isError || save.isPending}
            >
                {save.isPending ? 'Saving…' : 'Save'}
            </button>
            {isError && <p>Couldn't load prompt.</p>}
        </div>
    )
}

export default PromptEditor