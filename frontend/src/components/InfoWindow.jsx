function InfoWindow({ selectedCell }) {
    return (
        <div className="info-window">
            {selectedCell && (
                <div>
                    <h3 className="capitalise">{selectedCell.biomeData.name}</h3>
                    <p>Position: ({selectedCell.x}, {selectedCell.y})</p>
                </div>
            )}
        </div>
    )
}

export default InfoWindow