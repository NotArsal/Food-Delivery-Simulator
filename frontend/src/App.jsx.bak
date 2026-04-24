import { useState, useEffect, useRef, useCallback } from 'react'
import MapView from './components/MapView'
import MetricsPanel from './components/MetricsPanel'
import './App.css'

const WS_URL = 'ws://localhost:8000/ws'
const API_URL = 'http://localhost:8000'

function App() {
  const [simState, setSimState] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState(null)
  const [simSetupConfig, setSimSetupConfig] = useState({
    num_drivers: 50,
    num_orders: 1000,
    city: "Pune, India",
    routing_mode: "dynamic",
    manual_algorithm: "dijkstra"
  })
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      const ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        setIsConnected(true)
        setError(null)
        console.log('[WS] Connected')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type !== 'pong') {
            setSimState(data)
            setIsRunning(data.is_running)
          }
        } catch (e) {
          console.error('[WS] Parse error:', e)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        console.log('[WS] Disconnected')
        reconnectTimer.current = setTimeout(connectWebSocket, 3000)
      }

      ws.onerror = (e) => {
        console.error('[WS] Error:', e)
        setError('WebSocket connection failed. Is the backend running?')
      }

      wsRef.current = ws
    } catch (e) {
      setError('Cannot connect to backend server')
    }
  }, [])

  useEffect(() => {
    connectWebSocket()
    return () => {
      if (wsRef.current) wsRef.current.close()
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }
  }, [connectWebSocket])

  // Keepalive ping
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  const startSimulation = async () => {
    try {
      setIsRunning(true)
      const res = await fetch(`${API_URL}/api/simulation/start`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(simSetupConfig)
      })
      const data = await res.json()
      if (data.status !== 'started' && data.status !== 'already_running') {
        setIsRunning(false)
      }
    } catch (e) {
      setError('Failed to start simulation. Check backend connection.')
      setIsRunning(false)
    }
  }

  const resetSimulation = async () => {
    try {
      await fetch(`${API_URL}/api/simulation/reset`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(simSetupConfig)
      })
      setIsRunning(false)
      setMetrics(null)
    } catch (e) {
      setError('Failed to reset simulation.')
    }
  }

  const stopSimulation = async () => {
    try {
      await fetch(`${API_URL}/api/simulation/stop`, { method: 'POST' })
      setIsRunning(false)
    } catch (e) {
      setError('Failed to stop simulation.')
    }
  }

  const updateConfig = async (routing_mode, manual_algorithm) => {
    try {
      // Always update local setup config so UI reflects it immediately
      setSimSetupConfig(prev => ({ ...prev, routing_mode, manual_algorithm }))
      
      // If backend is running, notify it
      await fetch(`${API_URL}/api/simulation/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ routing_mode, manual_algorithm })
      })
      
      if (simState) {
        setSimState({
          ...simState,
          config: { routing_mode, manual_algorithm }
        })
      }
    } catch (e) {
      console.error('Failed to update config', e)
    }
  }

  const [debugRouteData, setDebugRouteData] = useState(null)
  const [debugLoading, setDebugLoading] = useState(false)

  const fetchDebugRoute = async () => {
    if (!simState || !simState.orders || simState.orders.length === 0) return
    setDebugLoading(true)
    try {
      // Pick random pending order to debug
      const order = simState.orders.find(o => o.status === 'pending') || simState.orders[0]
      const res = await fetch(`${API_URL}/api/algorithms/compare?from_lat=${order.restaurant_lat}&from_lng=${order.restaurant_lng}&to_lat=${order.customer_lat}&to_lng=${order.customer_lng}`)
      const data = await res.json()
      setDebugRouteData(data)
    } catch (e) {
      console.error(e)
    } finally {
      setDebugLoading(false)
    }
  }

  const metrics = simState?.metrics || {
    active_drivers: 0,
    total_drivers: simSetupConfig.num_drivers,
    orders_pending: 0,
    orders_delivered: 0,
    orders_in_transit: 0,
    total_orders: simSetupConfig.num_orders,
    total_orders_released: 0,
    avg_delivery_time_min: 0,
    total_distance_km: 0,
    tick: 0,
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🚀</span>
            <h1>Delivery OS</h1>
          </div>
          <div className="subtitle">Simulation Engine</div>
        </div>
        <div className="header-right">
          <div className={`connection-badge ${isConnected ? 'connected' : 'disconnected'}`}>
            <span className="connection-dot"></span>
            {isConnected ? 'Live' : 'Offline'}
          </div>
          {!isRunning ? (
            <button className="btn btn-start" onClick={startSimulation}>
              <span>▶</span> Start Simulation
            </button>
          ) : (
            <button className="btn btn-stop" onClick={stopSimulation}>
              <span>⏹</span> Stop
            </button>
          )}
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <span>⚠️</span> {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Main content */}
      <main className="app-main">
          <MapView 
            key={simSetupConfig.city}
            drivers={simState?.drivers || []} 
            orders={simState?.orders || []}
            isRunning={isRunning}
            debugRouteData={debugRouteData}
            city={simSetupConfig.city}
          />
        <MetricsPanel 
          metrics={metrics} 
          isRunning={isRunning} 
          debugRouteData={debugRouteData}
          debugLoading={debugLoading}
          onDebugClick={fetchDebugRoute}
          config={simState?.config || { routing_mode: simSetupConfig.routing_mode, manual_algorithm: simSetupConfig.manual_algorithm }}
          onUpdateConfig={updateConfig}
          simSetupConfig={simSetupConfig}
          setSimSetupConfig={setSimSetupConfig}
        />
      </main>
    </div>
  )
}

export default App
