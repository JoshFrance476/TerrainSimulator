import { useState, useEffect } from 'react'

function EngineTab({ interactionPrompt, setInteractionPrompt, onInteractionSave, sceneGuidePrompt, setSceneGuidePrompt, onSceneGuideSave }) {
    const [activeTab, setActiveTab] = useState('interaction') // 'interaction', 'scene-guide', 'model'
    return (
        <div className="engine-tab">
            <div className="tab-bar">
                <button 
                    className={activeTab === 'interaction' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('interaction')}
                >
                    Interaction
                </button>
                <button
                    className={activeTab === 'scene-guide' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('scene-guide')}
                >
                    Scene Guide
                </button>
                <button
                    className={activeTab === 'model' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('model')}
                >
                    Model
                </button>
            </div>
            {activeTab === 'interaction' ? (
                <div className="interaction-tab">
                    <textarea className="prompt-textbox"
                    value={interactionPrompt}
                    onChange={(e) => setInteractionPrompt(e.target.value)}/>
                    <button onClick={onInteractionSave}>Save</button>
                </div>
            ) : activeTab === 'scene-guide' ? (
                <div className="scene-guide-tab">
                    <textarea className="prompt-textbox" 
                    value={sceneGuidePrompt}
                    onChange={(e) => setSceneGuidePrompt(e.target.value)}/>
                    <button onClick={onSceneGuideSave}>Save</button>
                </div>
            ) : activeTab === 'model' ? (
                <div className="model-tab">
                    {/* Model tab content goes here */}
                </div>
            ) : null}
        </div>
    )
}

export default EngineTab