import { useTokenUsageQuery } from '../queries/queries'

function Header() {
    const { data } = useTokenUsageQuery()

    return (
        <header className="header">
            <div className="header-brand">Sandbox</div>

            <nav className="header-nav">
                <button className="nav-btn nav-btn-active" type="button">Play</button>
                <button className="nav-btn" type="button">Editor</button>
                <button className="nav-btn" type="button">Browse</button>
            </nav>

            <div className="token-counter">
                <span>I : {data?.input_tokens ?? 0}</span>
                <span>O : {data?.output_tokens ?? 0}</span>
            </div>

            <button className="account-btn" type="button" aria-label="Account">
                <span className="account-avatar">JF</span>
            </button>
        </header>
    )
}

export default Header