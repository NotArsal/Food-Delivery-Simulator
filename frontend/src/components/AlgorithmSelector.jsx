import './AlgorithmSelector.css';

const algorithms = [
  { id: 'dijkstra', name: 'Dijkstra', icon: '⬡', color: '#00d4aa', desc: 'Optimal for all scenarios' },
  { id: 'astar', name: 'A*', icon: '★', color: '#f59e0b', desc: 'Heuristic best-first' },
  { id: 'bfs', name: 'BFS', icon: '◎', color: '#3b82f6', desc: 'Shortest hops' },
  { id: 'dfs', name: 'DFS', icon: '◇', color: '#8b5cf6', desc: 'Deep exploration' },
  { id: 'greedy', name: 'Greedy', icon: '◆', color: '#ec4899', desc: 'Fast local optimum' },
  { id: 'floyd_warshall', name: 'Floyd', icon: '⬢', color: '#14b8a6', desc: 'All-pairs shortest' },
  { id: 'genetic', name: 'Genetic', icon: '🧬', color: '#f97316', desc: 'Evolutionary optimization' },
];

function AlgorithmSelector({ config, onUpdateConfig }) {
  const isManual = config.routing_mode === 'manual';

  return (
    <div className="algorithm-selector">
      <h3>Algorithm</h3>
      {isManual ? (
        <div className="algorithm-grid">
          {algorithms.map(algo => (
            <button
              key={algo.id}
              className={`algo-card ${config.manual_algorithm === algo.id ? 'active' : ''}`}
              style={{ '--algo-color': algo.color }}
              onClick={() => onUpdateConfig('manual', algo.id)}
              disabled={!isManual}
            >
              <span className="algo-icon">{algo.icon}</span>
              <span className="algo-name">{algo.name}</span>
              <span className="algo-desc">{algo.desc}</span>
            </button>
          ))}
        </div>
      ) : (
        <div className="auto-mode-info">
          <span className="auto-icon">🤖</span>
          <p>Dynamic mode active</p>
          <p className="sub">System selects optimal algorithm based on traffic, order density, and urgency</p>
        </div>
      )}
    </div>
  );
}

export default AlgorithmSelector;