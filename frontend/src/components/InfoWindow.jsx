function InfoWindow({ selectedCell }) {
    return (
        <div className="info-window">
            {selectedCell && (
                <div>
                    <p className="region-position">Position: ({selectedCell.x}, {selectedCell.y})</p>
                    <h2 className="capitalise biome-name">{selectedCell.biomeData.name}</h2>
                    {selectedCell.regionData.map((region, index) => (
                        <div key={index} className="region-info"> 
                            <h3 className="capitalise region-title">{region.title}</h3>
                            <p className="region-visible-desc">{region.visible_desc}</p>
                            <p className="region-hidden-desc"><i>{region.hidden_desc}</i></p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default InfoWindow