import { useMemo } from 'react'

function MetricsPanel({ metrics, isRunning, debugRouteData, debugLoading, onDebugClick, config, onUpdateConfig, simSetupConfig, setSimSetupConfig }) {
  const {
    active_drivers = 0,
    total_drivers = 50,
    orders_pending = 0,
    orders_delivered = 0,
    orders_in_transit = 0,
    total_orders = 1000,
    total_orders_released = 0,
    avg_delivery_time_min = 0,
    total_distance_km = 0,
    tick = 0,
    driver_statuses = {},
  } = metrics

  const deliveredPct = total_orders > 0 ? (orders_delivered / total_orders * 100) : 0
  const releasedPct = total_orders > 0 ? (total_orders_released / total_orders * 100) : 0

  return (
    <div className="metrics-panel">
      {/* Simulation Status */}
      <div className="panel-title">
        {isRunning ? '🟢 Simulation Active' : '⏸️ Simulation Idle'}
      </div>

      {/* Key Metrics Grid */}
      <div className="metric-grid">
        <div className="metric-card">
          <div className="metric-label">Active Fleet</div>
          <div className="metric-value success">{active_drivers}<span className="metric-unit">/ {total_drivers}</span></div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Pending Orders</div>
          <div className="metric-value">{orders_pending}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">In Transit</div>
          <div className="metric-value" style={{ fontSize: '22px' }}>{orders_in_transit}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Delivered</div>
          <div className="metric-value success" style={{ fontSize: '22px' }}>
            {orders_delivered}
          </div>
        </div>
        <div className="metric-card wide">
          <div className="metric-label">Avg Delivery Time</div>
          <div className="metric-value gradient">{avg_delivery_time_min}<span className="metric-unit">min</span></div>
        </div>
        <div className="metric-card wide">
          <div className="metric-label">Total Distance Routed</div>
          <div className="metric-value">{total_distance_km.toFixed(1)}<span className="metric-unit">km</span></div>
        </div>
      </div>

      {/* Progress Bars */}
      <div className="glass-panel">
        <div className="panel-title" style={{ border: 'none', margin: 0 }}>Fulfillment Progress</div>

        <div className="progress-wrapper">
          <div className="progress-header">
            <span className="progress-title">Released Orders</span>
            <span className="progress-stats">{total_orders_released} / {total_orders}</span>
          </div>
          <div className="progress-track">
            <div className="progress-fill blue" style={{ width: `${releasedPct}%` }}></div>
          </div>
        </div>

        <div className="progress-wrapper">
          <div className="progress-header">
            <span className="progress-title">Delivered Orders</span>
            <span className="progress-stats">{orders_delivered} / {total_orders}</span>
          </div>
          <div className="progress-track">
            <div className="progress-fill green" style={{ width: `${deliveredPct}%` }}></div>
          </div>
        </div>
      </div>

      {/* Simulation Setup (Only editable when stopped) */}
      <div className="glass-panel">
        <div className="panel-title" style={{ border: 'none', margin: 0 }}>Infrastructure Setup</div>
        
        <div className="input-group">
          <span className="input-label">City</span>
          <select 
            className="glass-select" 
            value={simSetupConfig?.city}
            onChange={(e) => setSimSetupConfig({ ...simSetupConfig, city: e.target.value })}
            disabled={isRunning}
          >
            <option value="Pune, India">Pune, India</option>
            <option value="Mumbai, India">Mumbai, India</option>
            <option value="Delhi, India">Delhi, India</option>
            <option value="Bangalore, India">Bangalore, India</option>
          </select>
        </div>

        <div className="input-group">
          <span className="input-label">Drivers</span>
          <input 
            type="number" 
            className="glass-input" 
            value={simSetupConfig?.num_drivers}
            onChange={(e) => setSimSetupConfig({ ...simSetupConfig, num_drivers: parseInt(e.target.value) || 1 })}
            disabled={isRunning}
            min="1" max="500"
          />
        </div>

        <div className="input-group">
          <span className="input-label">Orders</span>
          <input 
            type="number" 
            className="glass-input" 
            value={simSetupConfig?.num_orders}
            onChange={(e) => setSimSetupConfig({ ...simSetupConfig, num_orders: parseInt(e.target.value) || 1 })}
            disabled={isRunning}
            min="1" max="10000"
          />
        </div>
      </div>

      {/* Algorithm Configuration */}
      <div className="glass-panel">
        <div className="panel-title" style={{ border: 'none', margin: 0 }}>Routing Strategy</div>
        
        <div className="segmented-control">
          <button 
            className={`segment-btn ${config.routing_mode === 'dynamic' ? 'active' : ''}`}
            onClick={() => onUpdateConfig('dynamic', config.manual_algorithm)}
          >
            ✨ Dynamic
          </button>
          <button 
            className={`segment-btn ${config.routing_mode === 'manual' ? 'active' : ''}`}
            onClick={() => onUpdateConfig('manual', config.manual_algorithm)}
          >
            ⚙️ Manual
          </button>
        </div>

        {config.routing_mode === 'manual' && (
          <div className="input-group">
            <select 
              className="glass-select"
              style={{ textAlign: 'left', paddingLeft: '12px' }}
              value={config.manual_algorithm}
              onChange={(e) => onUpdateConfig('manual', e.target.value)}
            >
              <option value="dijkstra">Dijkstra's (Balanced)</option>
              <option value="astar">A* Search (Fast)</option>
              <option value="bfs">Breadth-First Search</option>
              <option value="dfs">Depth-First Search</option>
              <option value="greedy">Greedy Best-First</option>
              <option value="bellman_ford">Bellman-Ford</option>
            </select>
          </div>
        )}
        
        <div className="info-text">
          {config.routing_mode === 'dynamic' 
            ? "Dynamic mode auto-selects the optimal algorithm based on live heuristic variables like distance, urgency, and congestion." 
            : "Manual mode forces the engine to use a single fixed algorithm for all pathfinding operations."}
        </div>
      </div>

      {/* Driver Status Breakdown */}
      <div className="glass-panel">
        <div className="panel-title" style={{ border: 'none', margin: 0 }}>Driver Diagnostics</div>
        <div className="status-list">
          {['idle', 'picking', 'delivering', 'returning'].map(status => (
            <div className="status-item" key={status}>
              <div className="status-left">
                <span className={`status-dot ${status}`}></span>
                <span className="status-name">{status}</span>
              </div>
              <span className="status-count">{driver_statuses[status] || 0}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Algorithm Benchmark */}
      <div className="glass-panel">
        <div className="panel-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: 'none', margin: 0 }}>
          <span>Algorithm Profiler</span>
          <button 
            className="btn btn-secondary" 
            style={{ padding: '6px 12px', fontSize: '12px', height: 'auto', borderRadius: '6px' }}
            onClick={onDebugClick} 
            disabled={debugLoading || total_orders === 0}
          >
            {debugLoading ? 'Profiling...' : 'Run Profile'}
          </button>
        </div>
        
        {debugRouteData ? (
          <div style={{ marginTop: '10px' }}>
            <table className="benchmark-table">
              <thead>
                <tr>
                  <th>Algorithm</th>
                  <th>Time (ms)</th>
                  <th>Nodes</th>
                  <th>Dist</th>
                </tr>
              </thead>
              <tbody>
                {['dijkstra', 'astar', 'bfs', 'dfs', 'greedy', 'bellman_ford'].map(algo => {
                  const d = debugRouteData[algo];
                  if (!d || d.error) return null;
                  const isFast = d.calc_time_ms < 50;
                  return (
                    <tr key={algo}>
                      <td style={{ textTransform: 'capitalize' }}>{algo.replace('_', ' ')}</td>
                      <td className={`benchmark-time ${isFast ? 'fast' : 'slow'}`}>{d.calc_time_ms}</td>
                      <td>{d.nodes_explored}</td>
                      <td>{d.total_distance_m}m</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="info-text">
            Click 'Run Profile' to benchmark all search algorithms on a single live route.
          </div>
        )}
      </div>

    </div>
  )
}

export default MetricsPanel
