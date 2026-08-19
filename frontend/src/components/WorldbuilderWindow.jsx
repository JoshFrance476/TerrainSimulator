function WorldbuilderWindow({ biomeLookup, setBiomeBrush, setBrushType, brushType, biomeBrush, generateRandomMap }) {
    return (
        <div className="worldbuilder-window">
            <h2>Worldbuilder</h2>
            <h3>Biome</h3>
            {Object.entries(biomeLookup).map(([biomeId, biome]) => (
                <div key={biomeId} className="biome-entry">
                    <div className="colour-preview-small" style={{ backgroundColor: biome.colour }} />
                    <span>{biome.name}</span>
                    <button onClick={() => {setBiomeBrush(biomeId); setBrushType('paint');}}>Select</button>
                </div>
            ))}

            <h3>Elevation</h3>
            <button onClick={() => setBrushType('elevation')}>Elevation</button>
            <button onClick={generateRandomMap}>Generate Random Map</button>
        </div>
    );
}

export default WorldbuilderWindow