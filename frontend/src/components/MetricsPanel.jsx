function MetricsPanel({ metrics, isRunning }) {
  const {
    active_drivers = 0,
    total_drivers = 0,
    orders_pending = 0,
    orders_delivered = 0,
    orders_in_transit = 0,
    total_orders = 0,
    total_orders_released = 0,
    avg_delivery_time_min = 0,
    total_distance_km = 0,
    tick = 0,
    utilization_pct = 0,
  } = metrics;

  return (
    <div className="metric-grid">
      <div className="metric-card wide">
        <div className="metric-label">Delivery Completion</div>
        <div className="progress-wrapper">
          <div className="progress-header">
            <span className="progress-title">{orders_delivered} of {total_orders_released}</span>
            <span className="progress-stats">{Math.round((orders_delivered / (total_orders_released || 1)) * 100)}%</span>
          </div>
          <div className="progress-track">
            <div 
              className="progress-fill green" 
              style={{ width: `${(orders_delivered / (total_orders_released || 1)) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Avg Time</div>
        <div className="metric-value gradient">
          {avg_delivery_time_min}
          <span className="metric-unit">min</span>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Utilization</div>
        <div className="metric-value success">
          {Math.round(utilization_pct)}
          <span className="metric-unit">%</span>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-label">In Transit</div>
        <div className="metric-value">{orders_in_transit}</div>
      </div>

      <div className="metric-card">
        <div className="metric-label">Pending</div>
        <div className="metric-value" style={{ color: 'var(--status-picking)' }}>{orders_pending}</div>
      </div>

      <div className="metric-card wide">
        <div className="metric-label">Distance Covered</div>
        <div className="metric-value">
          {total_distance_km.toFixed(1)}
          <span className="metric-unit">km</span>
        </div>
      </div>

      <div className="info-text">
        System Tick: {tick} | Data Source: Live Simulation
      </div>
    </div>
  );
}

export default MetricsPanel;