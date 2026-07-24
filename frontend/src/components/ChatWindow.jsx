import { useState } from 'react'
import SceneDisplay from './SceneDisplay'


function ChatWindow({ selectedCell }) {

    return (
        <div className="chat-window">
            <SceneDisplay selectedCell={selectedCell} />
        </div>
    )
}

export default ChatWindow