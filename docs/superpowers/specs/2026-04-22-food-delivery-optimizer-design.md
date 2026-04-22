# Food Delivery Optimizer - Full System Redesign

## 1. Project Overview

**Project Name:** Food Delivery Route Optimizer  
**Type:** Real-time logistics simulation platform  
**Core Functionality:** Intelligent food delivery routing system with dynamic algorithm selection, live simulation, and algorithm comparison  
**Target Users:** Academic judges, recruiters, portfolio reviewers

## 2. Goals

- Portfolio-grade demonstration of algorithm intelligence
- Demo-ready polished UI/UX with smooth animations
- Real-time visualization of drivers, orders, routes on Pune map
- Algorithm comparison dashboard
- Heatmaps for demand zones

## 3. Architecture

### 3.1 Backend (FastAPI)

**Modules:**
- `routing/` - All pathfinding algorithms
- `simulation.py` - Core simulation engine  
- `road_network.py` - Pune graph data
- `traffic.py` - Traffic simulation
- `orders.py` - Order generation
- `drivers.py` - Driver management
- `batching.py` - Multi-order batching

### 3.2 Frontend (React + Vite)

**Stack:** React 18, Vite, Leaflet, Recharts  
**UI:** Custom dark theme, smooth animations, premium feel

### 3.3 Communication

- REST API for configuration
- WebSocket for real-time simulation updates

## 4. Algorithm Router

### 4.1 Dynamic Selection Logic

When `routing_mode == 'dynamic'`:

| Scenario | Algorithm |
|----------|-----------|
| High traffic + many orders | A* (heuristic) |
| Rush hour + urgency | Greedy Best-First |
| Small graph / debug | BFS |
| Full all-pairs shortest path | Floyd-Warshall |
| Optimization mode | Genetic Algorithm |
| Default | Dijkstra |

### 4.2 Manual Mode

User selects algorithm via UI buttons:
- Dijkstra
- A*
- BFS
- DFS
- Greedy Best-First
- Floyd-Warshall
- Genetic Algorithm

## 5. Pune Data

### 5.1 Restaurant Zones

| Zone | Coordinates (lat, lng) | Restaurants |
|------|----------------------|-------------|
| Kothrud | 18.5113, 73.7797 | 15-20 |
| Baner | 18.5647, 73.7719 | 12-15 |
| Hinjewadi | 18.5907, 73.7383 | 20-25 |
| Viman Nagar | 18.5679, 73.9100 | 10-15 |
| Koregaon Park | 18.5362, 73.8951 | 15-18 |
| Wakad | 18.5986, 73.7677 | 12-15 |
| Hadapsar | 18.5089, 73.9267 | 10-12 |

### 5.2 Traffic Simulation by Time of Day

| Time Period | Traffic Level | Congestion Zones |
|-------------|---------------|------------------|
| 8:00-10:00  | High          | Hinjewadi, Viman Nagar |
| 12:00-14:00 | High          | Koregaon Park, Kothrud |
| 18:00-21:00 | Very High     | All zones |
| 22:00-24:00 | Low           | All zones |
| Other times | Medium        | Random hotspots |

Traffic affects algorithm selection in dynamic mode.

### 5.3 Restaurant Data

For each restaurant:
- Name (realistic Indian restaurant names)
- Cuisine type (Indian, Chinese, Pizza, Biryani, etc.)
- Rating (3.5-4.8)
- Zone location
- Icon/category for map markers

### 5.4 Road Network

- Generate synthetic but realistic Pune road graph
- Major roads connecting zones
- Estimated 200-500 nodes
- Include major roads: Mumbai-Bangalore Highway, Pune-Solapur Road, Nagar Road

## 6. User Controls

### 6.1 Simulation Parameters
- Number of drivers (10-100)
- Number of orders (100-2000)
- Vehicle speed type (bike/car)
- Traffic level (low/medium/high)
- Routing mode (dynamic/manual)

### 6.2 Algorithm Selection
- Visual cards for each algorithm
- Active selection highlighted
- Real-time performance metrics per algorithm

## 7. Frontend UI

### 7.1 Layout

```
┌─────────────────────────────────────────────────┐
│  Header: Logo | Mode Toggle | Stats | Controls │
├─────────────────────────────────────────────────┤
│                                                 │
│              Interactive Map                    │
│           (Drivers, Routes, Heatmap)            │
│                                                 │
├─────────────────────────────────────────────────┤
│  Metrics Panel  │  Algorithm Cards │ Comparison │
└─────────────────────────────────────────────────┘
```

### 7.2 Visual Features
- Dark theme with accent colors
- Smooth driver movement animations
- Color-coded route lines by algorithm
- Heatmap overlay for demand zones
- Real-time counter animations
- Responsive layout
- Restaurant icons/markers by cuisine type

## 8. Simulation Features

### 8.1 Live Dispatch
- Drivers moving on map in real-time
- Orders assigned dynamically
- Pickup → delivery flow visualization
- Route recalculation on traffic changes

### 8.2 Metrics
- Delivery time comparison
- Total distance traveled
- Fuel cost estimation
- Driver utilization
- Orders completed
- CPU/runtime efficiency

### 8.3 Advanced Features
- Multi-order batching
- Nearest-driver matching
- Traffic-aware rerouting
- Priority order handling
- Heatmaps for demand zones

## 9. Acceptance Criteria

### 9.1 Functional
- [ ] All 6 algorithms work correctly
- [ ] Dynamic mode selects appropriate algorithm
- [ ] Real-time simulation runs smoothly
- [ ] WebSocket updates at 1-2 second intervals
- [ ] Heatmap displays demand zones
- [ ] Algorithm comparison shows metrics

### 9.2 Visual
- [ ] Premium dashboard appearance
- [ ] Smooth driver animations
- [ ] Dark theme with good contrast
- [ ] Responsive on different screen sizes
- [ ] Professional color scheme

### 9.3 Performance
- [ ] Frontend loads in < 3 seconds
- [ ] Simulation runs at acceptable speed
- [ ] No memory leaks during extended runs

## 10. Implementation Phases

### Phase 1: Backend Core (Days 1-3)
1. Fix existing bugs in routing algorithms
2. Implement algorithm router with dynamic selection
3. Add genetic algorithm
4. Enhance Pune data module with time-based traffic
5. Improve traffic simulation
6. Add real restaurant data with zones

### Phase 2: Frontend Polish (Days 3-6)
1. Rebuild UI with premium design
2. Add algorithm selection cards
3. Implement heatmap layer
4. Add live metrics animations
5. Create comparison dashboard
6. Add restaurant icons on map

### Phase 3: Integration & Polish (Days 6-10)
1. WebSocket optimization
2. Route visualization
3. Performance tuning
4. Bug fixes
5. Demo preparation

### Phase 4: Portfolio Documentation (Days 10-14)
1. Create comprehensive README.md with:
   - Architecture diagram (ASCII or Mermaid)
   - Algorithm explanations with time complexity
   - Screenshots/GIFs of key features
   - Setup instructions
   - Feature highlights
2. Add inline code documentation
3. Create demo video script
4. Add performance benchmarks

## 11. Success Metrics

- Judges/recruiters impressed by:
  - Algorithm depth and correctness
  - Real-time visualization quality
  - UI polish and professionalism
  - Code organization
  - Feature completeness