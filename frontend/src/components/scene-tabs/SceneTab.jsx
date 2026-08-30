function SceneTab( { 
    playerLocation , 
    scene , 
    streamedOutput , 
    onStartNewScene ,
    onPromptInteraction, 
    onRetryPrompt, 
    onSubmitAction, 
    user, 
    sceneGuideIsStreaming, 
    interactionIsStreaming,
    onSummariseScene
    } ) {

    return (
        <div className="scene-window">
            <p className="position">Position: ({playerLocation ? playerLocation.x : 'N/A'}, {playerLocation ? playerLocation.y : 'N/A'})</p>
            <div>
                {user && !scene && !sceneGuideIsStreaming && (
                    <button onClick={onStartNewScene}>Start Scene</button>
                )}
                {!user && (
                    <button disabled>Log in to prompt</button>
                )}
            </div>

            {scene && (
                <>
                    <div className="interaction-guide">
                        <p><b>Environment description:</b> {scene.guide.environment_description}</p>
                        <p><b>Precise location:</b> {scene.guide.location_precise}</p>
                        <p><b>Story suggestion:</b> {scene.guide.story_suggestion}</p>
                        <ul>
                            {scene.guide.suggested_outcomes.map((outcome, outcomeIndex) => (
                                <li key={outcomeIndex}>{outcome}</li>
                            ))}
                        </ul>
                    </div>
                    {!interactionIsStreaming && scene.interactions?.length === 0 && (
                        <button onClick={onPromptInteraction}>Prompt Interaction</button>
                    )}
                    {scene.interactions.map((interaction, index) => (
                        <div key={index}>                            
                            {interaction.completed && (
                                <>
                                    <p>{interaction.description}</p>
                                    <p className="action">{interaction.chosen_action}</p>
                                </>
                            )}
                            {!interaction.completed && (
                                <>
                                    <p>{interaction.description}</p>
                                    {interaction.actions.map((a, index) => (
                                        <button key={index} onClick={() => onSubmitAction({ action: a.action })}>
                                            {a.action} - {a.exit_flag ? 'Exit' : 'Continue'}
                                        </button>
                                    ))}
                                    <button onClick={() => onRetryPrompt()}>Retry Prompt</button>
                                </>
                            )}
                        </div>
                    ))}
                    {scene.ended && (
                        <button onClick={onSummariseScene}>Finish</button>
                    )}
                </>
            )}
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', width: '100%', boxSizing: 'border-box' }}>
                {streamedOutput}
            </pre>
        </div>
    )
}

export default SceneTab