# HeatGuard - State Risk Map Frontend

Stack: React + JavaScript/JSX + Tailwind CSS + Vite + Leaflet.

## New state-based workflow

1. The map opens on a whole-India view.
2. The user selects a state/UT instead of entering latitude/longitude.
3. The map loads the published India state boundary GeoJSON and zooms to the selected state.
4. The frontend samples multiple points inside that state boundary.
5. Each point is sent to the existing FastAPI endpoint:
   `GET /api/predict?latitude=...&longitude=...`
6. The worst 7-day risk returned by the backend is shown as a colored map point.
7. Extreme = dark red, Very High = red, High = orange, Moderate = yellow, Low = green.
8. The highest-risk sampled point becomes the representative forecast for the existing dashboard cards.

The map uses OpenStreetMap tiles and the India state GeoJSON from udit-001/india-maps-data via jsDelivr.

## Run

```bash
npm install
npm run dev
```

The frontend expects the FastAPI backend at `http://127.0.0.1:8000` unless `VITE_API_BASE_URL` is configured.

## Important limitation

The current backend is a coordinate-level prediction service, not a district-level/state-wide raster service. Therefore the colored areas on the state map are **backend prediction sample points**, not official district boundaries or a continuous heat-risk surface. Increasing the sampling density or adding a dedicated backend grid endpoint can make the map more detailed later.
