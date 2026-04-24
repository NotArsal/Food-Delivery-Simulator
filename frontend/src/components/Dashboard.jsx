import { useState, useEffect } from 'react';
import MapView from './MapView';
import MetricsPanel from './MetricsPanel';
import AlgorithmSelector from './AlgorithmSelector';
import SimControls from './SimControls';
import './Dashboard.css';

function Dashboard({
  simState,
  isConnected,
  isRunning,
  config,
  onUpdateConfig,
  simSetupConfig,
  setSimSetupConfig,
  onStart,
  onStop,
  onReset
}) {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`dashboard ${darkMode ? 'dark' : 'light'}`}>
      <header className="dashboard-header">
        <div className="logo-section">
          <span className="logo-icon">🚴</span>
          <h1>DeliveryOS</h1>
          <span className="tag">Pune</span>
        </div>

        <div className="controls-section">
          <div className="mode-toggle">
            <button
              className={config.routing_mode === 'dynamic' ? 'active' : ''}
              onClick={() => onUpdateConfig('dynamic', config.manual_algorithm)}
            >
              🤖 Auto
            </button>
            <button
              className={config.routing_mode === 'manual' ? 'active' : ''}
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
            />
            <span>🔥 Heatmap</span>
          </label>

          <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>

        <div className="stats-badge">
          <span className={`connection ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● Live' : '○ Offline'}
          </span>
        </div>
      </header>

      <main className="dashboard-main">
        <section className="map-section">
          <MapView
            drivers={simState?.drivers || []}
            orders={simState?.orders || []}
            isRunning={isRunning}
            showHeatmap={showHeatmap}
            city={simSetupConfig.city}
          />
        </section>

        <aside className="sidebar">
          <SimControls
            isRunning={isRunning}
            onStart={onStart}
            onStop={onStop}
            onReset={onReset}
            config={simSetupConfig}
            onConfigChange={setSimSetupConfig}
          />
          <AlgorithmSelector
            config={config}
            onUpdateConfig={onUpdateConfig}
          />
          <MetricsPanel
            metrics={simState?.metrics || {}}
            isRunning={isRunning}
          />
        </aside>
      </main>
    </div>
  );
}

export default Dashboard;