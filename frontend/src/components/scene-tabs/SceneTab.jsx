import { useEffect, useState } from 'react'

function SceneTab( { playerLocation , scene , streamedOutput , onStartNewScene , onSubmitAction} ) {
    const [expandedGuides, setExpandedGuides] = useState(new Set())


    function toggleGuide(index) {
    setExpandedGuides((prev) => {
        const next = new Set(prev)
        if (next.has(index)) {
            next.delete(index)
        } else {
            next.add(index)
        }
        return next
    })
}


    return (
        <div className="scene-window">
            <p className="position">Position: ({playerLocation ? playerLocation.x : 'N/A'}, {playerLocation ? playerLocation.y : 'N/A'})</p>
            <div>
                <button onClick={onStartNewScene}>Send</button>
            </div>

            {!scene && <p>No active scene.</p>}

            {scene && (
                <>
                    {scene.interactions.map((interaction, index) => (
                        <div key={index}>
                            <button className="link-button" onClick={() => toggleGuide(index)}>
                                {expandedGuides.has(index) ? 'Hide Guide' : 'Show Guide'}
                            </button>
                            
                            {expandedGuides.has(index) && (
                                <div className="interaction-guide">
                                    <p><b>Environment description:</b> {interaction.guide.environment_description}</p>
                                    <p><b>Precise location:</b> {interaction.guide.precise_location}</p>
                                    <p><b>Story suggestion:</b> {interaction.guide.story_suggestion}</p>
                                    <ul>
                                        {interaction.guide.outcome_suggestions.map((outcome, outcomeIndex) => (
                                            <li key={outcomeIndex}>{outcome}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
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
                                </>
                            )}
                        </div>
                    ))}
                </>
            )}
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', width: '100%', boxSizing: 'border-box' }}>
                {streamedOutput}
            </pre>
        </div>
    )
}

export default SceneTab