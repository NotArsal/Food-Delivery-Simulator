import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function AlgorithmChart({ comparisonData, isLoading }) {
  if (isLoading) {
    return (
      <div className="metric-card wide" style={{ textAlign: 'center', padding: '40px' }}>
        <div className="logo-icon" style={{ fontSize: '24px', marginBottom: '10px' }}>⚡</div>
        <div className="metric-label">Analyzing Performance...</div>
      </div>
    );
  }

  if (!comparisonData || Object.keys(comparisonData).length === 0) {
    return null; // Don't show anything if no data
  }

  const chartData = Object.entries(comparisonData).map(([algo, data]) => ({
    name: algo.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    time: data.time_ms || 0,
    distance: data.distance_m || 0,
    color: algo === 'dijkstra' ? '#32d74b' : algo === 'astar' ? '#ffd60a' : '#0a84ff'
  })).sort((a, b) => a.time - b.time);

  return (
    <div className="glass-panel" style={{ marginTop: '16px' }}>
      <h3 className="panel-title">⚡ Algorithm Benchmark</h3>
      
      <div style={{ height: '180px', width: '100%', marginTop: '12px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: -10, right: 20 }}>
            <XAxis type="number" hide />
            <YAxis 
              type="category" 
              dataKey="name" 
              width={80} 
              tick={{ fontSize: 9, fill: 'var(--text-secondary)', fontWeight: 600 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{
                background: 'rgba(10, 10, 12, 0.95)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                fontSize: '11px',
                backdropFilter: 'blur(10px)'
              }}
              itemStyle={{ color: 'var(--text-primary)' }}
            />
            <Bar dataKey="time" radius={[0, 4, 4, 0]} barSize={12}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="info-text" style={{ textAlign: 'center', fontSize: '10px' }}>
        Lower execution time (ms) indicates better computational efficiency.
      </div>
    </div>
  );
}

export default AlgorithmChart;