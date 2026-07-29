import { useState } from "react";
import { useStoryDataContext } from "../../contexts/StoryDataContext";

function QuestTab() {
    const { questsList } = useStoryDataContext()
    if (!questsList) {
        return <p>No quests</p>;
    }
    return (
        <div>
            {questsList && questsList.length === 0 ? (
                <p>No quests available.</p> 
            ) : (    
                questsList.map((quest, index) => (
                    <div key={index} className="info-window-box">
                        <h3 className="capitalise box-title">{quest.title}</h3>
                        <p className="quest-visible-desc">{quest.visible_context}</p>
                        <div className="quest-hidden-desc">{quest.hidden_context}</div>
                    </div>
                ))
            )}
        </div>  
    );
}

export default QuestTab;
