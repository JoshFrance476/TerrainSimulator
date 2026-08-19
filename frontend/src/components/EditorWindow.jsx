import '../pages/editor.css'

function EditorWindow({ interactionType, brushColour, brushBiome, brushRegion, colourPresets, setBrushColour, setInteractionType }) {
    return (
        <div className="editor-window">
            <h2>Worldbuilder</h2>
            <h4>Current Brush</h4>
            <div className="brush-overview">
                <div 
                    className={`colour-preview ${brushColour === null ? 'checkerboard' : ''}`}
                    style={{ backgroundColor: brushColour }}

                />
                <div className="brush-details">
                    <h4>Biome: {brushBiome ?? 'None'} </h4>
                    <h4>Region: {brushRegion ?? 'None'}</h4>
                </div>
            </div>
            <div className="colour-section">
                <h4>Colour</h4>
                <div className="colour-presets">
                    <button 
                        key="no-colour"
                        className={`colour-preview-small checkerboard ${brushColour === null ? 'selected' : ''}`}
                        onClick={() => setBrushColour(null)}
                    />
                    {colourPresets.map((colour, index) => (
                        <button 
                            key={colour}
                            className={`colour-preview-small ${brushColour === colour ? 'selected' : ''}`}
                            style={{ backgroundColor: colour }}
                            onClick={() => setBrushColour(colour)}
                        />
                    ))}
                </div>
                <button onClick={() => setInteractionType('eyedropper')}>Eyedropper</button>
            </div>
            <div className="texture-section">
                <h4>Texture</h4>
                <button onClick={() => setBrushBiome('grass')}>Grass</button>
            </div>
            <div className="biome-section">
                <h4>Biome</h4>
                <button onClick={() => setBrushBiome(null)}>No Biome</button>
            </div>
            <div className="region-section">
                <h4>Region</h4>
                <button onClick={() => setBrushRegion(null)}>No Region</button>
            </div>
        </div>
    )
}

export default EditorWindow