import { useState, useEffect, useRef, useCallback } from 'react';
import Dashboard from './components/Dashboard';
import AlgorithmChart from './components/AlgorithmChart';
import './App.css';

const WS_URL = 'ws://localhost:8000/ws';
const API_URL = 'http://localhost:8000';

function App() {
  const [simState, setSimState] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [simSetupConfig, setSimSetupConfig] = useState({
    num_drivers: 50,
    num_orders: 1000,
    city: "Pune, India",
    routing_mode: "dynamic",
    manual_algorithm: "dijkstra"
  });
  const [debugRouteData, setDebugRouteData] = useState(null);
  const [debugLoading, setDebugLoading] = useState(false);

  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('[WS] Connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== 'pong') {
            setSimState(data);
            setIsRunning(data.is_running);
          }
        } catch (e) {
          console.error('[WS] Parse error:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('[WS] Disconnected');
        reconnectTimer.current = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (e) => {
        console.error('[WS] Error:', e);
        setError('WebSocket connection failed. Is the backend running?');
      };

      wsRef.current = ws;
    } catch (e) {
      setError('Cannot connect to backend server');
    }
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connectWebSocket]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const startSimulation = async () => {
    try {
      setIsRunning(true);
      const res = await fetch(`${API_URL}/api/simulation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(simSetupConfig)
      });
      const data = await res.json();
      if (data.status !== 'started' && data.status !== 'already_running') {
        setIsRunning(false);
      }
    } catch (e) {
      setError('Failed to start simulation. Check backend connection.');
      setIsRunning(false);
    }
  };

  const resetSimulation = async () => {
    try {
      await fetch(`${API_URL}/api/simulation/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(simSetupConfig)
      });
      setIsRunning(false);
    } catch (e) {
      setError('Failed to reset simulation.');
    }
  };

  const stopSimulation = async () => {
    try {
      await fetch(`${API_URL}/api/simulation/stop`, { method: 'POST' });
      setIsRunning(false);
    } catch (e) {
      setError('Failed to stop simulation.');
    }
  };

  const updateConfig = async (routing_mode, manual_algorithm) => {
    try {
      setSimSetupConfig(prev => ({ ...prev, routing_mode, manual_algorithm }));
      await fetch(`${API_URL}/api/simulation/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ routing_mode, manual_algorithm })
      });
      if (simState) {
        setSimState({ ...simState, config: { routing_mode, manual_algorithm } });
      }
    } catch (e) {
      console.error('Failed to update config', e);
    }
  };

  const fetchDebugRoute = async () => {
    if (!simState || !simState.orders || simState.orders.length === 0) return;
    setDebugLoading(true);
    try {
      const order = simState.orders.find(o => o.status === 'pending') || simState.orders[0];
      const res = await fetch(`${API_URL}/api/algorithms/compare?from_lat=${order.restaurant_lat}&from_lng=${order.restaurant_lng}&to_lat=${order.customer_lat}&to_lng=${order.customer_lng}`);
      const data = await res.json();
      setDebugRouteData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setDebugLoading(false);
    }
  };

  return (
    <>
      {error && (
        <div className="error-banner">
          <span>⚠️</span> {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
      <Dashboard
        simState={simState}
        isConnected={isConnected}
        isRunning={isRunning}
        config={simState?.config || { routing_mode: simSetupConfig.routing_mode, manual_algorithm: simSetupConfig.manual_algorithm }}
        onUpdateConfig={updateConfig}
        simSetupConfig={simSetupConfig}
        setSimSetupConfig={setSimSetupConfig}
        onStart={startSimulation}
        onStop={stopSimulation}
        onReset={resetSimulation}
      >
        <AlgorithmChart comparisonData={debugRouteData} isLoading={debugLoading} />
      </Dashboard>
    </>
  );
}

export default App;