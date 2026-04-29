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

// Status colors
const STATUS_COLORS = {
  idle: '#22c55e',
  picking: '#eab308',
  delivering: '#ef4444',
  returning: '#3b82f6',
}

// Custom driver icon creator
function createDriverIcon(status) {
  const color = STATUS_COLORS[status] || '#94a3b8'
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
      <circle cx="16" cy="16" r="14" fill="${color}" stroke="white" stroke-width="2.5" opacity="0.95"/>
      <circle cx="16" cy="16" r="5" fill="white" opacity="0.9"/>
      ${status !== 'idle' ? '<circle cx="16" cy="16" r="18" fill="none" stroke="' + color + '" stroke-width="1.5" opacity="0.3"><animate attributeName="r" from="14" to="22" dur="1.5s" repeatCount="indefinite"/><animate attributeName="opacity" from="0.4" to="0" dur="1.5s" repeatCount="indefinite"/></circle>' : ''}
    </svg>
  `
  return L.divIcon({
    html: svg,
    className: 'driver-marker-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
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
      >
        {/* Dark tile layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <MapUpdater city={city} />
        <HeatmapLayer points={heatmapPoints} visible={showHeatmap} />

        {/* Delivery routes */}
        {routes.map(route => (
          <Polyline
            key={`route-${route.id}`}
            positions={route.coords}
            pathOptions={{
              color: STATUS_COLORS[route.status] || '#3b82f6',
              weight: 3,
              opacity: 0.6,
              dashArray: '8 6',
            }}
          />
        ))}

        {/* Debug Routing Exploration Overlay (Dijkstra) */}
        {debugRouteData?.dijkstra?.explored_coords && (
          <Polyline 
            positions={debugRouteData.dijkstra.explored_coords.map(c => [c[0], c[1]])} 
            pathOptions={{ color: '#22c55e', weight: 5, opacity: 0.15 }} 
          />
        )}

        {/* Debug Routing Exploration Overlay (A*) */}
        {debugRouteData?.astar?.explored_coords && (
          <Polyline 
            positions={debugRouteData.astar.explored_coords.map(c => [c[0], c[1]])} 
            pathOptions={{ color: '#ef4444', weight: 4, opacity: 0.35 }} 
          />
        )}

        {/* Restaurant markers (Red) */}
        {orders.slice(0, 80).map(order => (
          <CircleMarker
            key={`rest-${order.order_id}`}
            center={[order.restaurant_lat, order.restaurant_lng]}
            radius={5}
            pathOptions={{
              fillColor: '#ef4444',
              fillOpacity: 0.8,
              color: '#f87171',
              weight: 1.5,
            }}
          >
            <Popup>
              <div className="driver-popup">
                <h4>🍕 {order.restaurant_name || "Restaurant"}</h4>
                {order.restaurant_zone && <p>Zone: {order.restaurant_zone}</p>}
                <p>Order: {order.order_id}</p>
                <p>Status: {order.status}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Customer markers (Blue) */}
        {orders.slice(0, 80).map(order => (
          <CircleMarker
            key={`cust-${order.order_id}`}
            center={[order.customer_lat, order.customer_lng]}
            radius={4}
            pathOptions={{
              fillColor: '#3b82f6',
              fillOpacity: 0.7,
              color: '#60a5fa',
              weight: 1,
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

      {/* Map overlay legend */}
      {!showHeatmap && (
        <div className="map-legend">
          <div className="map-legend-title">Markers</div>
          <div className="map-legend-items">
            <div className="map-legend-item">
              <span style={{ color: '#ef4444', fontSize: 16 }}>●</span> Restaurant
            </div>
            <div className="map-legend-item">
              <span style={{ color: '#3b82f6', fontSize: 16 }}>●</span> Customer
            </div>
            <div className="map-legend-item">
              <span style={{ color: '#22c55e', fontSize: 16 }}>●</span> Idle
            </div>
            <div className="map-legend-item">
              <span style={{ color: '#eab308', fontSize: 16 }}>●</span> Picking
            </div>
            <div className="map-legend-item">
              <span style={{ color: '#ef4444', fontSize: 16 }}>●</span> Delivering
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MapView

