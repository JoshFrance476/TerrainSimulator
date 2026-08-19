import { useTokenUsageQuery } from '../queries/queries'
import { useState } from 'react'

function Header({ user , setShowAccountWindow, onNavigate }) {
    const { data } = useTokenUsageQuery()


    return (
        <header className="header">
            <button className="header-brand" type="button" onClick={() => onNavigate({ name: "landing" })}>Sandbox</button>

            <nav className="header-nav">
                <button className="nav-btn nav-btn-active" type="button">Play</button>
                <button className="nav-btn" type="button">Worldbuilder</button>
                <button className="nav-btn" type="button">Browse</button>
            </nav>

            <div className="token-counter">
                <span>I : {data?.input_tokens ?? 0}</span>
                <span>O : {data?.output_tokens ?? 0}</span>
            </div>

            <button className="account-btn" type="button" aria-label="Account" onClick={() => setShowAccountWindow((prev) => !prev)}>
                {user ? (
                    <span className="account-avatar">{user.name?.slice(0, 2) ?? '?'}</span>
                ) : (
                    <span className="account-avatar">?</span>
                )}
            </button>
        </header>
    )
}

export default Header