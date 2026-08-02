import { useState, useEffect } from 'react'
import PromptEditor from './PromptEditor'

function EngineTab() {
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
                    className={activeTab === 'scene-summary' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('scene-summary')}
                >
                    Scene Summary
                </button>
                <button
                    className={activeTab === 'model' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('model')}
                >
                    Model
                </button>
            </div>
            {activeTab === 'interaction' && <PromptEditor name="interaction" />}
            {activeTab === 'scene-guide' && <PromptEditor name="scene-guide" />}
            {activeTab === 'scene-summary' && <PromptEditor name="scene-summary" />}
            {activeTab === 'model' && (
                <div className="model-tab">
                    {/* Model tab content goes here */}
                </div>
            )}
        </div>
    )
}

export default EngineTab