import { useState } from 'react'

function LocationTab({ selectedCell }) {
    return (
        <div>
            {selectedCell && (
                <div>
                    <p className="position">Position: ({selectedCell.x}, {selectedCell.y})</p>
                    <h2 className="capitalise biome-name">{selectedCell.biomeData.name}</h2>
                    {selectedCell.regionData.map((region, index) => (
                        <div key={index} className="info-window-box">
                            <h3 className="capitalise box-title">{region.title}</h3>
                            <p className="region-visible-desc">{region.visible_description}</p>
                            <p className="region-hidden-desc"><i>{region.hidden_description}</i></p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default LocationTab