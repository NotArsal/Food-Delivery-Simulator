# 🚀 Food Delivery Route Optimizer & Logistics Simulation Platform

A full-stack logistics optimization system that simulates a real-world food delivery platform operating in **Pune, India**, using real road data, advanced routing algorithms, ML-based ETA prediction, and a live real-time dashboard.

![Tech Stack](https://img.shields.io/badge/Python-FastAPI-009688?style=flat-square) ![React](https://img.shields.io/badge/React-Leaflet-61DAFB?style=flat-square) ![ML](https://img.shields.io/badge/ML-Random_Forest-orange?style=flat-square) ![Map](https://img.shields.io/badge/Map-OpenStreetMap-green?style=flat-square)

---

## ✨ Features

| Module | Description |
|--------|-------------|
| **Road Network Engine** | Dynamically downloads road network via OSMnx based on chosen City (Pune, Mumbai, etc.) |
| **6 Routing Algorithms** | Dijkstra, A*, BFS, DFS, Greedy Best-First, Bellman-Ford, Floyd-Warshall |
| **Traffic Simulation** | Dynamic traffic multipliers (low ×1.0, medium ×1.3, high ×1.8) |
| **Order Generation** | User-configurable order count using real restaurant OSM data |
| **Order Batching** | K-Means clustering with max 3 orders/batch, 2 km radius |
| **Smart Dispatch** | Priority-queue assignment evaluating distance, driver load, and VIP orders |
| **Route Optimization** | Greedy TSP for multi-stop delivery sequence |
| **ML ETA Prediction** | Random Forest Regressor trained on synthetic delivery data |
| **Real-time Simulation** | Tick-based driver movement with WebSocket streaming |
| **Live Dashboard** | UI with config panel for Drivers, Orders, City, and Routing Strategies |

---

## 🏗️ Architecture

```
food-delivery-optimizer/
├── backend/                  # FastAPI + simulation engine
│   ├── main.py              # API server + WebSocket
│   ├── road_network.py      # OSMnx graph loader
│   ├── routing.py           # 4 routing algorithms
│   ├── traffic.py           # Dynamic traffic simulation
│   ├── orders.py            # Order generation
│   ├── batching.py          # K-Means clustering
│   ├── drivers.py           # Driver allocation
│   ├── route_optimizer.py   # Greedy TSP
│   ├── simulation.py        # Simulation engine
│   └── requirements.txt
├── ml/                       # Machine learning
│   ├── generate_training_data.py
│   ├── train_model.py
│   └── predict.py
├── frontend/                 # React + Leaflet dashboard
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── components/
│           ├── MapView.jsx
│           └── MetricsPanel.jsx
├── simulation/               # Standalone runner
│   └── run_simulation.py
├── data/                     # Cached graphs & models
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **npm**

### 1. Backend Setup

```bash
cd backend

# Create virtual env (optional but recommended)
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the API server (loads road network on first run)
python main.py
```

The backend starts at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 2. Train ML Model (Optional)

```bash
cd ml
python generate_training_data.py
python train_model.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 4. Run Simulation

- Click **"Start Simulation"** on the dashboard
- Watch 1000 orders get batched, assigned, and delivered across Pune
- Drivers move in real time on the map
- Metrics update live

---

## 🗺️ Dashboard

The dashboard features:

- **Simulation Setup**: Select Target City (e.g., Pune, Mumbai), Fleet Size (1 to 500+ drivers), and Order Volume.
- **Dark CartoDB Map**: Auto-centers on the configured city.
- **Routing Strategy Panel**: Toggle between **✨ Dynamic Mode** (auto-selects algorithm based on distance/traffic) and **⚙️ Manual Mode**
- **Color-coded driver markers**: 🟢 Idle | 🟡 Picking | 🔴 Delivering
- **Route polylines** showing delivery paths
- **Restaurant (red)** and **Customer (blue)** markers
- **Real-time metrics panel** with Driver Utilization % and live stats
- **Progress bars** for order release and delivery
- **Interactive Routing Benchmark Table**: Compares distance, nodes explored, and time elapsed across algorithms.

---

## 🧠 Algorithms

### Routing Operations
- **Dynamic Mode**: Analyzes traffic levels, node density, and distance to intelligently swap algorithms on the fly (e.g., A* for long distance, Dijkstra for chaotic traffic, BFS for short rapid tasks).
- **Manual Mode**: Global toggle over all simulated agents.

### Algorithms
- **Dijkstra**: Optimal shortest path using travel-time weights. Best for varying traffic.
- **A***: Heuristic search with haversine distance estimate. Extremely fast for long routes.
- **BFS (Breadth-First Search)**: Fast unweighted pathfinding.
- **DFS (Depth-First Search)**: Deep unweighted exploration.
- **Greedy Best-First**: Rapid heuristic-only expansion.
- **Bellman-Ford**: Supports negative weights (traffic recalculation fallback).
- **Floyd-Warshall**: All-pairs shortest paths (200-node subgraph demo).

### Optimization
- **K-Means Clustering**: Groups nearby orders into delivery batches
- **Greedy TSP**: Nearest-neighbor heuristic for stop sequencing
- **Priority Queue**: Min-heap for driver-batch assignment

### Machine Learning
- **Random Forest Regressor**: 100 estimators, features = [distance, traffic, stops, hour]
- Trained on 10,000 synthetic samples

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server status |
| GET | `/api/network/stats` | Road network statistics |
| GET | `/api/orders` | Current orders |
| GET | `/api/drivers` | Driver states |
| GET | `/api/metrics` | Simulation metrics |
| POST | `/api/simulation/start` | Start simulation |
| POST | `/api/simulation/stop` | Stop simulation |
| POST | `/api/simulation/reset` | Reset simulation |
| POST | `/api/simulation/config` | **NEW**: Update simulation routing configuration |
| POST | `/api/predict-eta` | ML ETA prediction |
| GET | `/api/route?from_lat=...&to_lat=...` | Compute route |
| GET | `/api/algorithms/compare?...` | Compare all algorithms |
| WS | `/ws` | Real-time WebSocket stream |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Graph | NetworkX, OSMnx |
| Data | Pandas, NumPy |
| ML | Scikit-learn, Joblib |
| Frontend | React 19, Vite |
| Map | Leaflet.js, react-leaflet, CartoDB tiles |
| Real-time | WebSockets |
| Map Source | OpenStreetMap |

---

## 📝 Notes

- **First run** downloads Pune's road network (~50-100 MB) if OSMnx is installed. Falls back to a synthetic grid otherwise.
- **Floyd-Warshall** runs on a 200-node subgraph only (O(V³) is infeasible on full graph).
- **Simulation** uses accelerated time: 2-second ticks with 10 orders released per tick.

---

## 📄 License

MIT License
