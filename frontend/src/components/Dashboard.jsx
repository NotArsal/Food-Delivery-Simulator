import { useState } from 'react';
import MapView from './MapView';
import MetricsPanel from './MetricsPanel';
import AlgorithmSelector from './AlgorithmSelector';
import SimControls from './SimControls';
import './Dashboard.css';

function Dashboard({
  simState,
  isConnected,
  isRunning,
  config = { routing_mode: 'dynamic', manual_algorithm: 'dijkstra' },
  onUpdateConfig,
  simSetupConfig,
  setSimSetupConfig,
  onStart,
  onStop,
  onReset,
  onCompare,
  children,
}) {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🚴</span>
            <h1>DeliveryOS</h1>
          </div>
          <span className="subtitle">{simSetupConfig.city.split(',')[0]} Operations</span>
        </div>

        <div className="header-right">
          <div className="segmented-control">
            <button
              className={`segment-btn ${config.routing_mode === 'dynamic' ? 'active' : ''}`}
              onClick={() => onUpdateConfig('dynamic', config.manual_algorithm)}
            >
              🤖 Auto
            </button>
            <button
              className={`segment-btn ${config.routing_mode === 'manual' ? 'active' : ''}`}
              onClick={() => onUpdateConfig('manual', config.manual_algorithm)}
            >
              🎯 Manual
            </button>
          </div>

          <label className="heatmap-toggle">
            <input
              type="checkbox"
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
              style={{ display: 'none' }}
            />
            <span className={`btn btn-secondary ${showHeatmap ? 'active' : ''}`} style={{ borderColor: showHeatmap ? 'var(--accent-primary)' : '' }}>
              {showHeatmap ? '🔥 Heatmap On' : '🔥 Heatmap'}
            </span>
          </label>

          <div className={`connection-badge ${isConnected ? 'connected' : ''}`}>
            <span className="connection-dot"></span>
            {isConnected ? 'Live' : 'Offline'}
          </div>

          <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '20px' }}>
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <main className="app-main">
        <section className="map-container">
          <MapView
            drivers={simState?.drivers || []}
            orders={simState?.orders || []}
            isRunning={isRunning}
            showHeatmap={showHeatmap}
            city={simSetupConfig.city}
          />
        </section>

        <aside className="metrics-panel">
          <div className="panel-section">
            <h3 className="panel-title">🕹️ Simulation Control</h3>
            <SimControls
              isRunning={isRunning}
              onStart={onStart}
              onStop={onStop}
              onReset={onReset}
              config={simSetupConfig}
              onConfigChange={setSimSetupConfig}
            />
          </div>

          <div className="panel-section">
            <h3 className="panel-title">🧠 Routing Strategy</h3>
            <AlgorithmSelector
              config={config}
              onUpdateConfig={onUpdateConfig}
            />
          </div>

          <div className="panel-section">
            <h3 className="panel-title">📊 Live Telemetry</h3>
            <MetricsPanel
              metrics={simState?.metrics || {}}
              isRunning={isRunning}
            />
          </div>

          {onCompare && (
            <button
              className="btn btn-start"
              id="btn-compare-algorithms"
              onClick={onCompare}
              disabled={!simState?.orders?.length}
              style={{ width: '100%', marginTop: 'auto' }}
            >
              🚀 Run Algorithm Benchmark
            </button>
          )}
          {children}
        </aside>
      </main>
    </div>
  );
}

export default Dashboard;