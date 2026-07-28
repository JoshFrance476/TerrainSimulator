import { useState } from "react";

function QuestTab() {
    const [quests, setQuests] = useState([
        {
            title: "The Lost Artifact",
            description: "You learned of a mysterious artifact hidden in the nearby cave. Find it and bring it back to the village elder.",
            objectives: [
                "Find the cave entrance.",
                "Find out more information on the artifact. (optional)",
                "Get better equipped. (optional)"
            ]
        },
        {
            title: "Rescue the Villagers",
            description: "Save the villagers captured by the bandits in the Dark Forest.",
            objectives: [
                "Find the bandits' hideout.",
            ]   
        }
    ]); 
    return (
        <div>
            {quests.length === 0 ? (
                <p>No quests available.</p> 
            ) : (    
                quests.map((quest, index) => (
                    <div key={index} className="info-window-box">
                        <h3 className="capitalise box-title">{quest.title}</h3>
                        <p className="quest-description">{quest.description}</p>
                        <div className="quest-objectives">
                            <ul>
                                {quest.objectives && quest.objectives.map((objective, objIndex) => (
                                    <li key={objIndex}><i>{objective}</i></li>
                                ))}
                            </ul>
                        </div>
                    </div>
                ))
            )}
        </div>  
    );
}

export default QuestTab;
