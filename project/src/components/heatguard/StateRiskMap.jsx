import { useEffect, useMemo, useState } from "react";
import { CircleMarker, GeoJSON, MapContainer, TileLayer, useMap } from "react-leaflet";
import { Loader2, MapPinned, LocateFixed } from "lucide-react";
import { getForecast } from "@/lib/api";
import "leaflet/dist/leaflet.css";

const INDIA_GEOJSON_URL =
  "https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@2884453/geojson/india.geojson";

export const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Puducherry",
];

const INDIA_BOUNDS = [[6.4, 68.0], [37.2, 97.6]];
const INDIA_CENTER = [22.7, 79.2];

const RISK_RANK = {
  Low: 1,
  Moderate: 2,
  High: 3,
  "Very High": 4,
  Extreme: 5,
};

const RISK_COLORS = {
  Low: "#22c55e",
  Moderate: "#eab308",
  High: "#f97316",
  "Very High": "#ef4444",
  Extreme: "#991b1b",
};

function normalize(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]/g, "");
}

function featureName(feature) {
  const p = feature?.properties ?? {};
  return p.name || p.NAME_1 || p.st_nm || p.State_Name || p.STNAME || p.state_name || p.STATE || "";
}

function findStateFeature(geojson, stateName) {
  if (!geojson?.features) return null;
  const wanted = normalize(stateName);
  return (
    geojson.features.find((feature) => normalize(featureName(feature)) === wanted) ||
    geojson.features.find((feature) => normalize(featureName(feature)).includes(wanted)) ||
    null
  );
}

function findStateForPoint(geojson, latitude, longitude) {
  if (!geojson?.features) return null;
  return geojson.features.find((feature) => pointInGeometry([latitude, longitude], feature.geometry)) || null;
}

function flattenCoordinates(geometry) {
  if (!geometry) return [];
  const walk = (value, result) => {
    if (typeof value?.[0] === "number") {
      result.push(value);
      return;
    }
    for (const child of value || []) walk(child, result);
  };
  const result = [];
  walk(geometry.coordinates, result);
  return result;
}

function geometryBounds(feature) {
  const coords = flattenCoordinates(feature?.geometry);
  if (!coords.length) return null;
  let minLat = Infinity;
  let maxLat = -Infinity;
  let minLon = Infinity;
  let maxLon = -Infinity;
  for (const [lon, lat] of coords) {
    minLat = Math.min(minLat, lat);
    maxLat = Math.max(maxLat, lat);
    minLon = Math.min(minLon, lon);
    maxLon = Math.max(maxLon, lon);
  }
  return [[minLat, minLon], [maxLat, maxLon]];
}

function pointInRing(point, ring) {
  const [lat, lon] = point;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [lonI, latI] = ring[i];
    const [lonJ, latJ] = ring[j];
    const intersects =
      latI > lat !== latJ > lat &&
      lon < ((lonJ - lonI) * (lat - latI)) / (latJ - latI || Number.EPSILON) + lonI;
    if (intersects) inside = !inside;
  }
  return inside;
}

function pointInGeometry(point, geometry) {
  if (!geometry) return false;
  if (geometry.type === "Polygon") {
    const [outer, ...holes] = geometry.coordinates;
    return pointInRing(point, outer) && !holes.some((hole) => pointInRing(point, hole));
  }
  if (geometry.type === "MultiPolygon") {
    return geometry.coordinates.some(([outer, ...holes]) =>
      pointInRing(point, outer) && !holes.some((hole) => pointInRing(point, hole)),
    );
  }
  return false;
}

function buildSamplePoints(feature, count = 12) {
  const bounds = geometryBounds(feature);
  if (!bounds) return [];
  const [[minLat, minLon], [maxLat, maxLon]] = bounds;
  const columns = 4;
  const rows = 4;
  const candidates = [];

  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < columns; c += 1) {
      const lat = minLat + ((r + 0.5) / rows) * (maxLat - minLat);
      const lon = minLon + ((c + 0.5) / columns) * (maxLon - minLon);
      if (pointInGeometry([lat, lon], feature.geometry)) {
        candidates.push({ latitude: lat, longitude: lon });
      }
    }
  }

  // Always include a geometry-derived center candidate when possible.
  const center = [(minLat + maxLat) / 2, (minLon + maxLon) / 2];
  if (pointInGeometry(center, feature.geometry)) {
    candidates.unshift({ latitude: center[0], longitude: center[1] });
  }

  const unique = [];
  const seen = new Set();
  for (const point of candidates) {
    const key = `${point.latitude.toFixed(4)},${point.longitude.toFixed(4)}`;
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(point);
    }
  }
  return unique.slice(0, count);
}

function FitToBounds({ bounds, india }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) map.fitBounds(bounds, { padding: [24, 24], maxZoom: 7 });
    else if (india) map.fitBounds(INDIA_BOUNDS, { padding: [20, 20] });
  }, [bounds, india, map]);
  return null;
}

function RiskLegend() {
  return (
    <div className="absolute bottom-3 left-3 z-[1000] rounded-xl border border-white/50 bg-white/95 p-3 text-xs shadow-lg backdrop-blur">
      <p className="mb-2 font-semibold text-foreground">Backend risk level</p>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
        {Object.entries(RISK_COLORS).map(([risk, color]) => (
          <div key={risk} className="flex items-center gap-1.5">
            <span className="size-3 rounded-full" style={{ backgroundColor: color }} />
            <span>{risk}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function StateRiskMap({ selectedState, onStateChange, onScanComplete, loading, setLoading }) {
  const [geojson, setGeojson] = useState(null);
  const [geoError, setGeoError] = useState(null);
  const [riskPoints, setRiskPoints] = useState([]);
  const [scanMessage, setScanMessage] = useState("");
  const [locating, setLocating] = useState(false);
  const [userLocation, setUserLocation] = useState(null);

  useEffect(() => {
    let active = true;
    fetch(INDIA_GEOJSON_URL)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load India's state boundaries.");
        return response.json();
      })
      .then((data) => {
        if (active) setGeojson(data);
      })
      .catch((error) => {
        if (active) setGeoError(error.message);
      });
    return () => { active = false; };
  }, []);

  const selectedFeature = useMemo(
    () => findStateFeature(geojson, selectedState),
    [geojson, selectedState],
  );

  useEffect(() => {
    if (!selectedState || !selectedFeature) {
      setRiskPoints([]);
      setScanMessage("");
      return;
    }

    let active = true;
    const scan = async () => {
      setLoading(true);
      setRiskPoints([]);
      setScanMessage("Sampling locations and asking the FastAPI prediction service for risk…");
      const points = buildSamplePoints(selectedFeature, 12);

      if (!points.length) {
        setLoading(false);
        setScanMessage("No safe sample points could be generated inside this state boundary.");
        return;
      }

      const results = [];
      for (let i = 0; i < points.length; i += 4) {
        const batch = points.slice(i, i + 4);
        const batchResults = await Promise.allSettled(
          batch.map(async (point) => {
            const forecast = await getForecast(point.latitude, point.longitude);
            const normalizedDays = forecast.forecast.map((day) => ({
              ...day,
              riskKey: String(day.risk ?? "").trim().toLowerCase(),
            }));
            const worstDay = normalizedDays.reduce(
              (best, day) => {
                const currentRank = RISK_RANK[
                  day.riskKey === "very high" ? "Very High" :
                  day.riskKey === "extreme" ? "Extreme" :
                  day.riskKey === "high" ? "High" :
                  day.riskKey === "moderate" ? "Moderate" : "Low"
                ] ?? 0;
                const bestRank = RISK_RANK[best] ?? 0;
                return currentRank > bestRank ? (
                  day.riskKey === "very high" ? "Very High" :
                  day.riskKey === "extreme" ? "Extreme" :
                  day.riskKey === "high" ? "High" :
                  day.riskKey === "moderate" ? "Moderate" : "Low"
                ) : best;
              },
              "Low",
            );
            const extremeDays = normalizedDays.filter((day) => day.riskKey === "extreme").length;
            return { ...point, risk: worstDay, extremeDays, forecast };
          }),
        );
        for (const result of batchResults) {
          if (result.status === "fulfilled") results.push(result.value);
        }
        if (active) setRiskPoints([...results]);
      }

      if (!active) return;
      if (!results.length) {
        setScanMessage("The prediction service did not return usable results for this state.");
        setLoading(false);
        return;
      }

      // IMPORTANT: Do not choose the "worst" sampled location as the dashboard
      // forecast. Doing that makes a normal 7-day backend forecast appear to be
      // Extreme for every day whenever any sampled location has an Extreme day.
      //
      // The first point is the geometry-derived center when available, so use the
      // first successful backend response as the representative daily forecast.
      // The map still keeps the sampled-location risk markers separately.
      const representative = results[0];
      const extremeCount = results.filter((point) => point.risk === "Extreme").length;
      setScanMessage(
        `${results.length} locations analysed. ${extremeCount} sampled area${extremeCount === 1 ? "" : "s"} reached Extreme risk. Dashboard forecast uses the representative location's daily backend response.`,
      );
      setLoading(false);
      onScanComplete?.(representative.forecast.forecast, representative);
    };

    void scan();
    return () => { active = false; };
  }, [onScanComplete, selectedFeature, selectedState, setLoading]);

  const handleUseMyLocation = () => {
    if (!("geolocation" in navigator)) {
      setScanMessage("Location access is not supported by this browser.");
      return;
    }

    setLocating(true);
    setScanMessage("Finding your location…");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        setUserLocation([latitude, longitude]);

        const feature = findStateForPoint(geojson, latitude, longitude);
        if (!feature) {
          setScanMessage("Your location could not be matched to an Indian state boundary.");
          setLocating(false);
          return;
        }

        const stateName = featureName(feature);
        if (!stateName) {
          setScanMessage("Your location was found, but the state name could not be identified.");
          setLocating(false);
          return;
        }

        onStateChange(stateName);
        setScanMessage(`${stateName} detected from your location. Running backend risk analysis…`);
        setLocating(false);
      },
      (error) => {
        const message = error.code === 1
          ? "Location permission was denied. Allow location access and try again."
          : "Could not determine your location. Please select a state manually.";
        setScanMessage(message);
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 },
    );
  };

  const stateStyle = {
    color: "#0f766e",
    weight: 2,
    fillColor: "#14b8a6",
    fillOpacity: 0.12,
  };

  return (
    <div className="mt-5 overflow-hidden rounded-2xl border border-input bg-card">
      <div className="border-b border-input p-4">
        <label className="block text-xs font-semibold uppercase tracking-wide text-muted-foreground" htmlFor="state-select">
          Select State / Union Territory
        </label>
        <select
          id="state-select"
          value={selectedState}
          onChange={(event) => onStateChange(event.target.value)}
          className="mt-1.5 w-full rounded-xl border border-input bg-background px-3.5 py-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-ring/25"
        >
          <option value="">Choose a state to analyse…</option>
          {INDIAN_STATES.map((state) => <option key={state} value={state}>{state}</option>)}
        </select>
        <button
          type="button"
          onClick={handleUseMyLocation}
          disabled={locating || !geojson}
          className="mt-3 inline-flex items-center gap-2 rounded-xl border border-primary/25 bg-primary/5 px-3.5 py-2.5 text-sm font-semibold text-primary transition hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {locating ? <Loader2 className="size-4 animate-spin" /> : <LocateFixed className="size-4" />}
          {locating ? "Finding location…" : "Use My Location"}
        </button>
        <p className="mt-2 text-xs text-muted-foreground">
          The map starts with India. Selecting a state zooms into it and samples multiple locations using your backend's prediction API.
        </p>
      </div>

      <div className="relative h-[430px] w-full">
        <MapContainer center={INDIA_CENTER} zoom={5} minZoom={4} maxZoom={12} className="h-full w-full" scrollWheelZoom>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FitToBounds bounds={selectedFeature ? geometryBounds(selectedFeature) : null} india={!selectedState} />
          {selectedFeature && <GeoJSON key={selectedState} data={selectedFeature} style={stateStyle} />}
          {userLocation && (
            <CircleMarker
              center={userLocation}
              radius={7}
              pathOptions={{ color: "#ffffff", weight: 2, fillColor: "#0f766e", fillOpacity: 1 }}
            />
          )}
          {riskPoints.map((point) => (
            <CircleMarker
              key={`${point.latitude}-${point.longitude}`}
              center={[point.latitude, point.longitude]}
              radius={point.risk === "Extreme" ? 13 : 9}
              pathOptions={{
                color: "#ffffff",
                weight: 2,
                fillColor: RISK_COLORS[point.risk] || RISK_COLORS.Low,
                fillOpacity: 0.85,
              }}
            >
              <div />
            </CircleMarker>
          ))}
        </MapContainer>
        <RiskLegend />
        {!selectedState && (
          <div className="pointer-events-none absolute left-1/2 top-4 z-[1000] -translate-x-1/2 rounded-full bg-white/95 px-4 py-2 text-xs font-semibold text-foreground shadow-lg">
            <MapPinned className="mr-1 inline size-3.5 text-primary" /> India overview
          </div>
        )}
        {loading && (
          <div className="absolute inset-0 z-[1001] flex items-center justify-center bg-white/35 backdrop-blur-[1px]">
            <div className="flex items-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-semibold shadow-xl">
              <Loader2 className="size-4 animate-spin text-primary" /> Analysing selected state…
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-input px-4 py-3 text-xs text-muted-foreground">
        {geoError ? `Map boundary error: ${geoError}` : scanMessage || "Select a state to start backend risk sampling."}
      </div>
    </div>
  );
}
