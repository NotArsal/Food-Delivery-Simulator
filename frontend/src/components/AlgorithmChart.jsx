import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './AlgorithmChart.css';

function AlgorithmChart({ comparisonData, isLoading }) {
  if (isLoading) {
    return <div className="algo-chart loading">Loading comparison...</div>;
  }

  if (!comparisonData || Object.keys(comparisonData).length === 0) {
    return <div className="algo-chart empty">Run comparison to see metrics</div>;
  }

  const chartData = Object.entries(comparisonData).map(([algo, data]) => ({
    name: algo,
    time: data.time_ms || 0,
    distance: data.distance_m || 0,
  }));

  return (
    <div className="algo-chart">
      <h3>Algorithm Comparison</h3>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={chartData} layout="vertical">
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" width={70} tick={{fontSize: 10}} />
            <Tooltip
              contentStyle={{
                background: '#1a1a25',
                border: 'none',
                borderRadius: 8
              }}
            />
            <Bar dataKey="time" fill="#00d4aa" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend">
        <span>⏱ Execution time (ms)</span>
      </div>
    </div>
  );
}

export default AlgorithmChart;