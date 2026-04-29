import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

// City Centers
const CITY_COORDS = {
  "Pune, India": [18.5204, 73.8567],
  "Mumbai, India": [19.0760, 72.8777],
  "Delhi, India": [28.6139, 77.2090],
  "Bangalore, India": [12.9716, 77.5946]
}

// Premium Status Colors (Accessible Palette)
const STATUS_COLORS = {
  idle: '#34c759',      // Apple Green
  picking: '#ffcc00',   // Apple Yellow
  delivering: '#ff3b30', // Apple Red
  returning: '#007aff',  // Apple Blue
  restaurant: '#ff9500', // Apple Orange
  customer: '#af52de',   // Apple Purple
}

// Custom driver icon creator
function createDriverIcon(status) {
  const color = STATUS_COLORS[status] || '#94a3b8'
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
      <defs>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <circle cx="18" cy="18" r="12" fill="${color}" stroke="white" stroke-width="2.5" filter="url(#glow)"/>
      <circle cx="18" cy="18" r="4" fill="white"/>
      ${status !== 'idle' ? `
        <circle cx="18" cy="18" r="15" fill="none" stroke="${color}" stroke-width="2" opacity="0.5">
          <animate attributeName="r" from="12" to="22" dur="1.2s" repeatCount="indefinite" />
          <animate attributeName="opacity" from="0.6" to="0" dur="1.2s" repeatCount="indefinite" />
        </circle>
      ` : ''}
    </svg>
  `
  return L.divIcon({
    html: svg,
    className: 'driver-marker-icon',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  })
}

// Heatmap layer component
function HeatmapLayer({ points, visible }) {
  const map = useMap()
  const heatLayerRef = useRef(null)

  useEffect(() => {
    if (visible && points.length > 0) {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current)
      }
      heatLayerRef.current = L.heatLayer(points, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        gradient: { 0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1: 'red' }
      }).addTo(map)
    } else if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current)
      heatLayerRef.current = null
    }

    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current)
      }
    }
  }, [map, points, visible])

  return null
}

// Animated map view controller
function MapUpdater({ city }) {
  const map = useMap()
  useEffect(() => {
    const coords = CITY_COORDS[city]
    if (coords) {
      map.setView(coords, 12, { animate: true })
    }
  }, [city, map])
  return null
}

function MapView({ drivers, orders, isRunning, showHeatmap, debugRouteData, city }) {
  const mapCenter = CITY_COORDS[city] || CITY_COORDS["Pune, India"]
  
  // Create driver icons memo
  const driverIcons = useMemo(() => {
    const icons = {}
    Object.keys(STATUS_COLORS).forEach(status => {
      icons[status] = createDriverIcon(status)
    })
    return icons
  }, [])

  // Route polylines from active drivers
  const routes = useMemo(() => {
    return drivers
      .filter(d => d.route_coords && d.route_coords.length > 1)
      .map(d => ({
        id: d.driver_id,
        coords: d.route_coords.map(c => [c[0], c[1]]),
        status: d.status,
      }))
  }, [drivers])

  // Heatmap data: all restaurant and customer locations
  const heatmapPoints = useMemo(() => {
    const points = []
    orders.forEach(o => {
      if (o.status !== 'delivered') {
        points.push([o.restaurant_lat, o.restaurant_lng, 0.5])
        points.push([o.customer_lat, o.customer_lng, 0.3])
      }
    })
    return points
  }, [orders])

  return (
    <div className="map-container">
      <MapContainer
        center={mapCenter}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        preferCanvas={true}
      >
        {/* Dark tile layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <MapUpdater city={city} />
        <HeatmapLayer points={heatmapPoints} visible={showHeatmap} />

        {/* Delivery routes (Layered for Glow) */}
        {routes.map(route => {
          const color = STATUS_COLORS[route.status] || '#0a84ff';
          return (
            <div key={`route-group-${route.id}`}>
              {/* Outer Glow */}
              <Polyline
                positions={route.coords}
                pathOptions={{
                  color: color,
                  weight: 8,
                  opacity: 0.15,
                  lineCap: 'round',
                }}
              />
              {/* Mid Glow */}
              <Polyline
                positions={route.coords}
                pathOptions={{
                  color: color,
                  weight: 4,
                  opacity: 0.3,
                  lineCap: 'round',
                }}
              />
              {/* Main Path */}
              <Polyline
                positions={route.coords}
                pathOptions={{
                  color: color,
                  weight: 2,
                  opacity: 0.8,
                  lineCap: 'round',
                  dashArray: route.status === 'delivering' ? '1, 6' : '10, 5',
                }}
              />
            </div>
          )
        })}

        {/* Debug Routing Exploration Overlay (Dijkstra) */}
        {debugRouteData?.dijkstra?.explored_coords && (
          <Polyline 
            positions={debugRouteData.dijkstra.explored_coords.map(c => [c[0], c[1]])} 
            pathOptions={{ color: '#32d74b', weight: 4, opacity: 0.1 }} 
          />
        )}

        {/* Debug Routing Exploration Overlay (A*) */}
        {debugRouteData?.astar?.explored_coords && (
          <Polyline 
            positions={debugRouteData.astar.explored_coords.map(c => [c[0], c[1]])} 
            pathOptions={{ color: '#ff453a', weight: 3, opacity: 0.2 }} 
          />
        )}

        {/* Restaurant markers (Pulse) */}
        {orders.map(order => (
          <CircleMarker
            key={`rest-${order.order_id}`}
            center={[order.restaurant_lat, order.restaurant_lng]}
            radius={7}
            pathOptions={{
              fillColor: STATUS_COLORS.restaurant,
              fillOpacity: 0.9,
              color: 'white',
              weight: 2,
            }}
          >
            <Popup>
              <div className="driver-popup">
                <h4>🍕 {order.restaurant_name || "Restaurant"}</h4>
                <p>Zone: {order.restaurant_zone}</p>
                <p>Status: {order.status}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Customer markers */}
        {orders.map(order => (
          <CircleMarker
            key={`cust-${order.order_id}`}
            center={[order.customer_lat, order.customer_lng]}
            radius={5}
            pathOptions={{
              fillColor: STATUS_COLORS.customer,
              fillOpacity: 0.8,
              color: 'white',
              weight: 1.5,
            }}
          >
            <Popup>
              <div className="driver-popup">
                <h4>📍 Customer</h4>
                <p>Order: {order.order_id}</p>
                <p>Status: {order.status}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Driver markers */}
        {drivers.map(driver => (
          <Marker
            key={driver.driver_id}
            position={[driver.lat, driver.lng]}
            icon={driverIcons[driver.status] || driverIcons.idle}
          >
            <Popup>
              <div className="driver-popup">
                <h4>🏍️ {driver.driver_id}</h4>
                <span className={`status-tag ${driver.status}`}>{driver.status.toUpperCase()}</span>
                <p>Deliveries: {driver.deliveries || 0}</p>
                {driver.active_batch && <p>Batch: {driver.active_batch}</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Map overlay legend (Premium) */}
      {!showHeatmap && (
        <div className="map-legend">
          <div className="map-legend-title">System Status</div>
          <div className="legend-grid">
            <div className="legend-item">
              <span className="status-dot" style={{ background: STATUS_COLORS.restaurant }}></span> Restaurant
            </div>
            <div className="legend-item">
              <span className="status-dot" style={{ background: STATUS_COLORS.customer }}></span> Customer
            </div>
            <div className="legend-item">
              <span className="status-dot" style={{ background: STATUS_COLORS.idle, boxShadow: `0 0 10px ${STATUS_COLORS.idle}` }}></span> Idle
            </div>
            <div className="legend-item">
              <span className="status-dot" style={{ background: STATUS_COLORS.picking, boxShadow: `0 0 10px ${STATUS_COLORS.picking}` }}></span> Picking
            </div>
            <div className="legend-item">
              <span className="status-dot" style={{ background: STATUS_COLORS.delivering, boxShadow: `0 0 10px ${STATUS_COLORS.delivering}` }}></span> Delivering
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MapView


