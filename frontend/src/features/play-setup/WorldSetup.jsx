function WorldSetup({regionLookup, componentLookup}) {
    return (
        <div className="modal-container-vertical">
            <div>
                <h3>Regions</h3>
                <div className="modal-list">
                    {Object.entries(regionLookup).map(([key, region]) => (
                        <div key={key}>{region.title} - {region.visible_description}</div>
                    ))}
                </div>
            </div>
            <div>
                <h3>Components</h3>
                <div className="modal-list">
                    {Object.entries(componentLookup).map(([key, component]) => (
                        <div key={key}>{component.name} - {component.description}</div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default WorldSetup