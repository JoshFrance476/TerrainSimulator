import './landing.css'

function Landing({ onNavigate }) {

    return (
        <div className="landing-page">
            <div className="main-section">
                <h1 className="main-title">Welcome to Sandbox</h1>
                <h2 className="main-subtitle">A platform for procedural text-based open-world story games, powered by generative AI</h2>
                <div className="main-navigation">
                    <button className="main-button" onClick={() => onNavigate({name: "browser"})}>Browse worlds</button>
                    <button className="main-button" onClick={() => onNavigate({name: "worldbuilder"})}>Open worldbuilder</button>
                </div>
            </div>
        </div>
        
    )
}

export default Landing