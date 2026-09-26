import './window.css'
function Window({ title , children }) {

    return (
        <div className="landing-window">
            <h2>{title}</h2>
            <div className='window-content'>{children}</div>
        </div>
        
    )
}

export default Window