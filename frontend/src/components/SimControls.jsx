import './SimControls.css';

function SimControls({ isRunning, onStart, onStop, onReset, config, onConfigChange }) {
  return (
    <div className="sim-controls">
      <h3>Simulation</h3>

      <div className="control-buttons">
        {!isRunning ? (
          <button className="btn-start" onClick={onStart}>
            ▶ Start
          </button>
        ) : (
          <button className="btn-stop" onClick={onStop}>
            ⏹ Stop
          </button>
        )}
        <button className="btn-reset" onClick={onReset}>
          ↺ Reset
        </button>
      </div>

      <div className="control-sliders">
        <label>
          <span>Drivers</span>
          <input
            type="range"
            min="10"
            max="100"
            value={config.num_drivers}
            onChange={(e) => onConfigChange({...config, num_drivers: parseInt(e.target.value)})}
          />
          <span className="value">{config.num_drivers}</span>
        </label>

        <label>
          <span>Orders</span>
          <input
            type="range"
            min="100"
            max="2000"
            step="100"
            value={config.num_orders}
            onChange={(e) => onConfigChange({...config, num_orders: parseInt(e.target.value)})}
          />
          <span className="value">{config.num_orders}</span>
        </label>
      </div>
    </div>
  );
}

export default SimControls;