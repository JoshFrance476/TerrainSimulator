import { useRef, useState } from 'react';
function WorldbuilderWindow({ 
    biomeLookup, 
    setBiomeBrush, 
    elevationEditType,  
    addRegion, 
    setElevationEditType, 
    biomeBrush, 
    generateRandomMap, 
    setBrushRadius, 
    addBiome, 
    regionLookup, 
    regionBrush, 
    setRegionBrush, 
    saveWorld, 
    saveWorldMutation, 
    loadWorld,
    detailLookup,
    setDetailBrush,
    detailBrush,
    addDetail,
    addComponent,
    setComponentBrush,
    componentBrush,
    componentLookup
}) {
    const loadWorldIdRef = useRef(); 
    
    const scaleRef = useRef(null);
    const octavesRef = useRef(null);
    const persistenceRef = useRef(null);
    const lacunarityRef = useRef(null);

    const newBiomeNameRef = useRef(null);
    const newBiomeColourRef = useRef(null);

    const newDetailNameRef = useRef(null);
    const newDetailColourRef = useRef(null);
    const newDetailHeightRef = useRef(null);

    const newComponentNameRef = useRef(null);
    const newComponentDescriptionRef = useRef(null);

    const newRegionNameRef = useRef(null);
    const newRegionVDescRef = useRef(null);
    const newRegionHDescRef = useRef(null);

    const newWorldNameRef = useRef(null);
    const newWorldDescriptionRef = useRef(null);

    const [tooltip, setTooltip] = useState(null); // { text, x, y }

    function handleAddDetail() {
        const name = newDetailNameRef.current.value;
        const colour = newDetailColourRef.current.value;
        const height = Number(newDetailHeightRef.current.value);
        newDetailNameRef.current.value = '';
        newDetailColourRef.current.value = '#000000';
        newDetailHeightRef.current.value = 0;
        addDetail({ name, colour, height });
    }

    function handleAddComponent() {
        const name = newComponentNameRef.current.value;
        const description = newComponentDescriptionRef.current.value;
        newComponentNameRef.current.value = '';
        newComponentDescriptionRef.current.value = '';
        addComponent({ name, description });
    }

    function handleAddBiome() {
        const name = newBiomeNameRef.current.value;
        const colour = newBiomeColourRef.current.value;
        newBiomeNameRef.current.value = '';
        newBiomeColourRef.current.value = '#000000';
        addBiome({ name, colour });
    }

    function handleAddRegion() {
        const title = newRegionNameRef.current.value;
        const visible_description = newRegionVDescRef.current.value;
        const hidden_description = newRegionHDescRef.current.value;
        newRegionNameRef.current.value = '';
        newRegionVDescRef.current.value = '';
        newRegionHDescRef.current.value = '';
        addRegion({ title, visible_description, hidden_description });
    }

    function handleSaveWorld() {
        const name = newWorldNameRef.current.value;
        const description = newWorldDescriptionRef.current.value;
        newWorldNameRef.current.value = '';
        newWorldDescriptionRef.current.value = '';
        saveWorld(name, description);
    }

    return (
        <div className="worldbuilder-window">
            <h2>Worldbuilder</h2>
            <h3>Active Brush</h3>
            <div className="brush-details">
                <h4>Biome: {biomeLookup[biomeBrush]?.name ?? 'None'}</h4>
                <h4>Detail: {detailBrush === 0 ? 'Erase' : detailLookup[detailBrush]?.name ?? 'None'}</h4>
                <h4>Elevation: {elevationEditType ?? 'None'} </h4>
                <h4>Region: {regionLookup[regionBrush]?.title ?? 'None'}</h4>
                <h4>Component: {componentLookup[componentBrush]?.name ?? 'None'}</h4>
                <div
                    className={`colour-preview ${biomeLookup[biomeBrush] ? '' : 'checkerboard'}`}
                    style={biomeLookup[biomeBrush] ? { backgroundColor: biomeLookup[biomeBrush].colour } : undefined}
                />
                <label>
                    Radius:
                    <input type="number" defaultValue={4} min="0" step="1" onChange={(e) => setBrushRadius(Number(e.target.value))} />
                </label>
            </div>
            <h3>Biome</h3>
            <div className="palette-display">
                <div key={"none"} className="palette-entry">
                    <button 
                        className="colour-preview-small checkerboard"
                        onMouseMove={(e) => setTooltip({ text: "None", x: e.clientX, y: e.clientY })}
                        onMouseLeave={() => setTooltip(null)}
                        onClick={() => {setBiomeBrush(null);}}
                    />
                </div>
                {Object.entries(biomeLookup).map(([biomeId, biome]) => (
                    <div key={biomeId} className="biome-entry">
                        <button 
                            className="colour-preview-small" 
                            style={{ backgroundColor: biome.colour }} 
                            onMouseMove={(e) => setTooltip({ text: biomeLookup[biomeId].name, x: e.clientX, y: e.clientY })}
                            onMouseLeave={() => setTooltip(null)}
                            onClick={() => {setBiomeBrush(biomeId);}}
                        />
                    </div>
                ))}
            </div>
            <label>
                Add biome:
                <input type="text" placeholder="Biome name" ref={newBiomeNameRef} />
                <input type="color" ref={newBiomeColourRef} />
                <button onClick={handleAddBiome}>Add</button>
            </label>
            <h3>Detail</h3>
            <div className="palette-display">
                <div key={"none"} className='palette-entry'>
                    <button
                    className="colour-preview-small checkerboard"
                    onMouseMove={(e) => setTooltip({ text: "None", x: e.clientX, y: e.clientY })}
                        onMouseLeave={() => setTooltip(null)}
                        onClick={() => {setDetailBrush(null);}}
                    />
                </div>
                <div key={"erase"} className='palette-entry'>
                    <button
                    className="colour-preview-small checkerboard erase-button"
                    onMouseMove={(e) => setTooltip({ text: "Erase", x: e.clientX, y: e.clientY })}
                        onMouseLeave={() => setTooltip(null)}
                        onClick={() => {setDetailBrush(0);}}
                    >X</button>
                </div>
                {Object.entries(detailLookup).map(([detailId, detail]) => (
                    <div key={detailId} className="palette-entry">
                        <button 
                            className="colour-preview-small" 
                            style={{ backgroundColor: detail.colour }} 
                            onMouseMove={(e) => setTooltip({ text: detailLookup[detailId].name, x: e.clientX, y: e.clientY })}
                            onMouseLeave={() => setTooltip(null)}
                            onClick={() => {setDetailBrush(detailId);}}
                        />
                    </div>
                ))}
            </div>
            <label>
                Add detail:
                <input type="text" placeholder="Detail name" ref={newDetailNameRef} />
                <input type="color" ref={newDetailColourRef} />
                <input type="number" ref={newDetailHeightRef} />
                <button onClick={handleAddDetail}>Add</button>
            </label>
            <h3>Connected Components</h3>
            <div key={"none"} className="component-entry">
                    <button onClick={() => setComponentBrush(null)}>Clear</button>
                </div>
            {Object.entries(componentLookup).map(([componentId, component]) => (
                <div key={componentId} className="component-entry">
                    <span>{component.name}</span>
                    <button onClick={() => setComponentBrush(Number(componentId))}>Select</button>
                </div>
            ))}
            <label>
                Add component:
                <input type="text" placeholder="Name" ref={newComponentNameRef} />
                <textarea placeholder="Description" ref={newComponentDescriptionRef} />
                <button onClick={handleAddComponent}>Add</button>
            </label>

            <h3>Elevation</h3>
            <div className="elevation-buttons">
                <button onClick={() => setElevationEditType(null)}>No edit</button>
                <button onClick={() => setElevationEditType('layer')}>Layer</button>
                <button onClick={() => setElevationEditType('continuous')}>Continuous</button>
                <button onClick={() => setElevationEditType('smoothing')}>Smoothing</button>
                <button onClick={() => setElevationEditType('flatten')}>Flatten</button>
            </div>

            <h3>Region</h3>
            {Object.entries(regionLookup).map(([regionId, region]) => (
                <div key={regionId} className="region-entry">
                    <span>{region.title}</span>
                    <button onClick={() => setRegionBrush(Number(regionId))}>Select</button>
                </div>
            ))}
            <label>
                Add region:
                <input type="text" placeholder="Region title" ref={newRegionNameRef} />
                <input type="text" placeholder="Region visible-description" ref={newRegionVDescRef} />
                <input type="text" placeholder="Region hidden-description" ref={newRegionHDescRef} />
                <button onClick={handleAddRegion}>Add</button>
            </label>
            <div className="map-generator-section">
                <h3>Map Generator</h3>
                <label>
                    Scale:
                    <input type="number" defaultValue={240} min="10" step="10" ref={scaleRef} />
                </label>
                <label>
                    Octaves:
                    <input type="number" defaultValue={8} min="1" step="1" ref={octavesRef} />
                </label>
                <label>
                    Persistence:
                    <input type="number" defaultValue={0.53} min="0.1" step="0.01" ref={persistenceRef} />
                </label>
                <label>
                    Lacunarity:
                    <input type="number" defaultValue={1.6} min="1" step="0.1" ref={lacunarityRef} />
                </label>
                <button onClick={() => generateRandomMap({
                    scale: Number(scaleRef.current.value), 
                    octaves: Number(octavesRef.current.value),
                    persistence: Number(persistenceRef.current.value),
                    lacunarity: Number(lacunarityRef.current.value)
                })}>
                    Generate Random Map
                </button>
            </div>
            <div className="settings-section">
                <h3>Settings</h3>
                <label>
                    Save map:
                    <input type="text" placeholder="Filename" ref={newWorldNameRef} />
                    <textarea placeholder="description" ref={newWorldDescriptionRef} />
                    <button onClick={handleSaveWorld}>Save</button>
                </label>
                {saveWorldMutation.isError && <p className="error">{saveWorldMutation.error.message}</p>}
                <label>
                    Load map:
                    <input type="text" placeholder="World ID" ref={loadWorldIdRef} />
                    <button onClick={() => loadWorld(loadWorldIdRef.current.value)}>Load</button>
                </label>
            </div>
            {tooltip && <div className="tooltip" style={{ left: tooltip.x+2, top: tooltip.y-20 }}>{tooltip.text ?? "empty"}</div>}
        </div>
    );
}

export default WorldbuilderWindow