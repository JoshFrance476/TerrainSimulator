import { useEffect, useRef, useState } from 'react'
import { api } from '../api'

export default function PlayPanel({
  world, scene, busy, onPromptScene, onChooseAction, onCustomAction,
  onExitScene, playTool, setPlayTool, selectedCell,
}) {
  const [custom, setCustom] = useState('')
  const [character, setCharacter] = useState(null)
  const [showNotebook, setShowNotebook] = useState(false)
  const logRef = useRef(null)

  useEffect(() => {
    api.character().then(setCharacter).catch(() => {})
  }, [scene])

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [scene, busy])

  const pending = scene?.pending
  const promptCell = selectedCell || world?.player

  return (
    <div className="panel journal">
      <header className="panel-head">
        <h2>Journal</h2>
        <div className="seg">
          <button className={playTool === 'select' ? 'on' : ''} onClick={() => setPlayTool('select')}>Inspect</button>
          <button className={playTool === 'move' ? 'on' : ''} onClick={() => setPlayTool('move')}>Travel</button>
        </div>
      </header>

      <div className="journal-log" ref={logRef}>
        {!scene && (
          <div className="journal-empty">
            <p className="serif">The page is blank. Move with WASD or click the map in Travel mode, then prompt an encounter where you stand.</p>
          </div>
        )}

        {scene?.history?.map((h, i) => (
          <article className="entry" key={i}>
            <p className="serif">{h.situation}</p>
            <p className="entry-action serif">— {h.action}</p>
          </article>
        ))}

        {pending && (
          <article className="entry current">
            <p className="serif">{pending.description}</p>
          </article>
        )}

        {scene?.ended && (
          <article className="entry ended">
            <p className="serif">The scene closes.</p>
          </article>
        )}

        {busy && <div className="thinking mono">the storyteller is writing…</div>}
      </div>

      <div className="journal-actions">
        {pending && !busy && (
          <>
            {pending.actions.map((a, i) => (
              <button key={i} className={`action-card ${a.exit_flag ? 'exit' : ''}`}
                onClick={() => onChooseAction(i)}>
                {a.action}
                {a.exit_flag && <span className="mono exit-tag">ends scene</span>}
              </button>
            ))}
            <form className="custom-action" onSubmit={(e) => {
              e.preventDefault()
              if (!custom.trim()) return
              onCustomAction(custom.trim())
              setCustom('')
            }}>
              <input value={custom} onChange={(e) => setCustom(e.target.value)}
                placeholder="Do something else…" />
              <button type="submit">Act</button>
            </form>
          </>
        )}

        {!pending && !busy && (
          <button className="action-card prompt" onClick={() => onPromptScene(promptCell)}>
            Prompt an encounter here
          </button>
        )}

        {scene && !busy && (
          <button className="ghost" onClick={onExitScene}>Abandon scene</button>
        )}
      </div>

      <footer className="journal-foot">
        <button className="ghost" onClick={() => setShowNotebook(!showNotebook)}>
          Notebook {character?.notebook?.length ? `(${character.notebook.length})` : ''}
        </button>
        {showNotebook && (
          <div className="notebook">
            {character?.notebook?.length
              ? character.notebook.map((n, i) => <p key={i} className="serif">{typeof n === 'string' ? n : JSON.stringify(n)}</p>)
              : <p className="dim">Empty. Generate a character on the World page.</p>}
            {character?.history?.length > 0 && (
              <>
                <h4 className="mono">Past scenes</h4>
                {character.history.map((h, i) => <p key={i} className="serif dim">{h}</p>)}
              </>
            )}
          </div>
        )}
      </footer>
    </div>
  )
}
