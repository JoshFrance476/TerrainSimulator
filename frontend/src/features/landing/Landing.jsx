import './landing.css'
import Window from './Window'
function Landing({ onNavigate }) {

    return (
        <>
            <div className="landing-page">
                <div className="header-section">
                    <h1 className="main-title">Welcome to Sandbox</h1>
                    <h2 className="main-subtitle">A platform for procedural text-based open-world story games, powered by generative AI</h2>
                    <div className="main-navigation">
                        <button className="main-button" onClick={() => onNavigate({name: "browser"})}>Browse worlds</button>
                        <button className="main-button" onClick={() => onNavigate({name: "worldbuilder"})}>Open worldbuilder</button>
                    </div>
                </div>
                <Window title="What is Sandbox?">
                    <p>
                        Sandbox is a story generation platform, using generative AI to try to replicate the gameplay of open-world story games on a 2D grid-based map.
                        Choose an existing map in the browser, or build your own in the worldbuilder, and use the setup window to set up your character and
                        world lore. Once you load in, explore and interact with the world - generative AI will use your character details, world lore
                        and environment context to produce an interactive text-based story. 
                    </p>
                    <p>
                        This is an experimental project, and the story generation algorithm is rather simplistic in it's current state - it's meant more as a sandbox for
                        playing around with the flexibility of generative AI than producing engaging, intricate stories on par with those created by humans.
                        All AI prompts are editable and can be retried in order to experiment with different .
                    </p>
                </Window>
                <figure className="video-figure">
                    <video
                        className="gif-video"
                        autoPlay loop muted playsInline
                        disablePictureInPicture
                        aria-hidden="true"
                        >
                        <source src="/videos/PlayDemo.mp4" type="video/mp4" />
                    </video>
                    <figcaption className="video-caption">
                        An example of gameplay - the story generates in the top left window while you use the map to move and interact with the world.
                        The bottom left window shows details on your location and character.
                    </figcaption>
                </figure>
                <Window title="How does story generation work?">

                </Window>
                <p>Video of worldbuilder here</p>
                <Window title="The map editor">

                </Window>
                <p>Slideshow of maps here</p>
            </div>
            <footer className='landing-footer'>
                    <a href="https://github.com/JoshFrance476/TerrainSimulator">Project GitHub</a>
                    <a href="https://www.linkedin.com/in/josh-france/">LinkedIn</a>
                    <p>Email: joshfrance.476@gmail.com</p>
            </footer>
        </>
    )
}

export default Landing