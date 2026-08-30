function MapToolbar({ interactionMode, onInteractionModeChange }) {
    return (
        <div className="map-toolbar">
            <button
                className={interactionMode === 'view' ? 'mode-btn active' : 'mode-btn inactive'}
                onClick={() => onInteractionModeChange('view')}
            >
                View
            </button>
            <button
                className={interactionMode === 'move' ? 'mode-btn active' : 'mode-btn inactive'}
                onClick={() => onInteractionModeChange('move')}
            >
                Move
            </button>
        </div>
    )
}

export default MapToolbar