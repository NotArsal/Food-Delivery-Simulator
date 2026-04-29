function SimControls({ isRunning, isInitializing, onStart, onStop, onReset, config, onConfigChange }) {
  return (
    <div className="glass-panel">
      <div className="control-buttons" style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
        {!isRunning ? (
          <button className="btn btn-start" style={{ flex: 1 }} onClick={onStart} disabled={isInitializing}>
            {isInitializing ? '⏳ Initializing...' : '▶ Start'}
          </button>
        ) : (
          <button className="btn btn-stop" style={{ flex: 1 }} onClick={onStop}>
            ⏹ Stop
          </button>
        )}
        <button className="btn btn-secondary" onClick={onReset}>
          ↺ Reset
        </button>
      </div>

      <div className="input-group" style={{ marginBottom: '10px' }}>
        <span className="input-label">Drivers</span>
        <input
          className="glass-input"
          type="number"
          min="1"
          max="200"
          value={config.num_drivers}
          onChange={(e) => onConfigChange({...config, num_drivers: parseInt(e.target.value) || 1})}
        />
      </div>

      <div className="input-group" style={{ marginBottom: '10px' }}>
        <span className="input-label">Orders</span>
        <input
          className="glass-input"
          type="number"
          min="10"
          max="5000"
          value={config.num_orders}
          onChange={(e) => onConfigChange({...config, num_orders: parseInt(e.target.value) || 10})}
        />
      </div>

      <div className="input-group" style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '4px' }}>
          <span className="input-label">Speed</span>
          <span className="input-label" style={{ opacity: 0.8 }}>{config.speed || 1}x</span>
        </div>
        <input
          type="range"
          min="0.5"
          max="5"
          step="0.5"
          value={config.speed || 1}
          onChange={(e) => onConfigChange({...config, speed: parseFloat(e.target.value)})}
          style={{ width: '100%', accentColor: '#0a84ff' }}
        />
      </div>
      
      <div className="info-text">
        {isRunning ? "Adjusting speed updates in real-time." : "Adjust parameters before starting a new simulation run."}
      </div>
    </div>
  );
}

export default SimControls;