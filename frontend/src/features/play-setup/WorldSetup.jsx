function WorldSetup({regionLookup, componentLookup}) {
    return (
        <div className="world-setup-container">
            <div>
                <h3>Regions</h3>
                <div className="location-list">
                    {Object.entries(regionLookup).map(([key, region]) => (
                        <div className="location-item" key={key}>
                            <div className="location-title">{region.title}</div>
                            <div className="location-visible-context">{region.visible_description}</div>
                            {region.context && 
                                <div className="location-hidden-context">{region.context}</div>
                            }
                        </div>
                    ))}
                </div>
            </div>
            <div>
                <h3>Components</h3>
                <div className="location-list">
                    {Object.entries(componentLookup).map(([key, component]) => (
                        <div className="location-item" key={key}>
                            <div className="location-title">{component.name}</div>
                            <div className="location-visible-context">{component.description}</div>
                            {component.context && 
                                <div className="location-hidden-context">{component.context}</div>
                            }
                            
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default WorldSetup