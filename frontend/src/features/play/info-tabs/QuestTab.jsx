import { useStory } from "../../../hooks/useStory";
import { useNewQuestMutation } from "../../../queries/queries";

function QuestTab() {
    const { questsList, isLoading, isError } = useStory()
    
    const newQuestMutation = useNewQuestMutation()

    if (isLoading) {
        return <p>Loading quests...</p>;
    }
    if (isError) {
        return <p>Error loading quests.</p>;
    }
    return (
        <div>
            {questsList.length === 0 ? (
                <p>No quests available.</p> 
            ) : (    
                questsList.map((quest, index) => (
                    <div key={index} className="info-window-box">
                        <h3 className="capitalise box-title">{quest.quest_description}</h3>
                        <p className="quest-visible-desc">{quest.component_id}</p>
                    </div>
                ))
            )}
            <button onClick={() => newQuestMutation.mutate()}>Generate New Quest</button>
        </div>  
    );
}

export default QuestTab;
