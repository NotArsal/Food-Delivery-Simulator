const algorithms = [
  { id: 'dijkstra', name: 'Dijkstra', icon: '⬡', color: '#32d74b', desc: 'Optimal & Stable' },
  { id: 'astar', name: 'A*', icon: '★', color: '#ffd60a', desc: 'Heuristic Guided' },
  { id: 'bfs', name: 'BFS', icon: '◎', color: '#0a84ff', desc: 'Shortest Hop' },
  { id: 'dfs', name: 'DFS', icon: '◇', color: '#bf5af2', desc: 'Deep Search' },
  { id: 'greedy', name: 'Greedy', icon: '◆', color: '#ff453a', desc: 'Fastest Compute' },
  { id: 'floyd_warshall', name: 'Floyd', icon: '⬢', color: '#007aff', desc: 'All-Pairs' },
];

function AlgorithmSelector({ config, onUpdateConfig }) {
  const isManual = config.routing_mode === 'manual';

  return (
    <div className="glass-panel">
      {isManual ? (
        <div className="metric-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          {algorithms.map(algo => (
            <button
              key={algo.id}
              className={`metric-card ${config.manual_algorithm === algo.id ? 'active' : ''}`}
              style={{ 
                cursor: 'pointer',
                textAlign: 'left',
                border: config.manual_algorithm === algo.id ? `1px solid ${algo.color}` : '1px solid var(--border-color)',
                boxShadow: config.manual_algorithm === algo.id ? `0 0 10px ${algo.color}44` : 'none',
                background: config.manual_algorithm === algo.id ? `${algo.color}11` : 'var(--bg-glass)'
              }}
              onClick={() => onUpdateConfig({ manual_algorithm: algo.id })}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{ color: algo.color, fontSize: '16px' }}>{algo.icon}</span>
                <span className="metric-label" style={{ margin: 0, fontSize: '10px' }}>{algo.name}</span>
              </div>
              <div style={{ fontSize: '9px', color: 'var(--text-muted)', fontWeight: 500 }}>{algo.desc}</div>
            </button>
          ))}
        </div>
      ) : (
        <div className="metric-card wide" style={{ textAlign: 'center', padding: '20px 10px' }}>
          <div className="logo-icon" style={{ fontSize: '32px', marginBottom: '12px' }}>🤖</div>
          <div className="metric-label" style={{ color: 'var(--accent-primary)' }}>Dynamic Intelligence Active</div>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px', lineHeight: 1.4 }}>
            System is autonomously selecting optimal routing strategies based on real-time traffic and delivery urgency.
          </p>
        </div>
      )}
    </div>
  );
}

export default AlgorithmSelector;