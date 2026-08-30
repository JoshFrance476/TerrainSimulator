export async function streamRequest(url, payload, handlers) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)

    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
    let buffer = ''
    while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += value

        const frames = buffer.split(/\r?\n\r?\n/)
        buffer = frames.pop()                  // trailing partial frame
        for (const frame of frames) {
            let event = 'message'
            const dataLines = []
            for (const line of frame.split(/\r?\n/)) {
                if (line.startsWith('event: ')) event = line.slice(7)
                else if (line.startsWith('data: ')) dataLines.push(line.slice(6))
            }
            handlers[event]?.(dataLines.join('\n'))
        }
    }
}