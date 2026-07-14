import { useState } from 'react'

function ChatStream() {
  const [message, setMessage] = useState('')
  const [output, setOutput] = useState('')

  async function handleSend() {
    setOutput('')

    const res = await fetch('/api/scene/prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: message[0], y: message[1] })
    })

    if (!res.ok) {
      console.error('POST failed:', await res.text())
      return
    }

    const { stream_id } = await res.json()

    const source = new EventSource(`/api/stream?id=${stream_id}`)
    source.addEventListener('data', (e) => {
      setOutput((prev) => prev + e.data)
    })
    source.addEventListener('done', () => source.close())
    source.onerror = () => source.close()
  }

  return (
    <div>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Enter message"
      />
      <button onClick={handleSend}>Send</button>
      <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', width: '100%', boxSizing: 'border-box' }}>
        {output}
      </pre>
    </div>
  )
}

export default ChatStream