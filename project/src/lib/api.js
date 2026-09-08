/**
 * Central API service for the HeatGuard frontend.
 * Talks to the existing FastAPI backend. No prediction logic lives here.
 */
const BASE_URL = import.meta.env["VITE_API_BASE_URL"]?.replace(/\/$/, "") ??
    "http://127.0.0.1:8000";
export const API_BASE_URL = BASE_URL;
/** Error carrying a message that is always safe to show to a user. */
export class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}
function friendlyStatusMessage(status) {
    if (status === 400)
        return "Those coordinates were rejected by the prediction service.";
    if (status === 404)
        return "The prediction service could not find that endpoint.";
    if (status === 422)
        return "Please check the coordinates and try again.";
    if (status === 500)
        return "The prediction service ran into a problem while analysing this location.";
    if (status === 502 || status === 503 || status === 504)
        return "The prediction service is unreachable right now. Please try again shortly.";
    return "The prediction service returned an unexpected response.";
}
async function fetchWithTimeout(url, timeoutMs = 20000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        return await fetch(url, { signal: controller.signal, headers: { Accept: "application/json" } });
    }
    finally {
        clearTimeout(timer);
    }
}
/** Returns true when GET /api/health responds with an ok status. */
export async function checkBackendHealth() {
    try {
        const res = await fetchWithTimeout(`${BASE_URL}/api/health`, 8000);
        if (!res.ok)
            return false;
        const data = (await res.json());
        return typeof data?.status === "string" && data.status.toLowerCase() === "ok";
    }
    catch {
        return false;
    }
}
function isValidDay(day) {
    const d = day;
    return (!!d &&
        typeof d.date === "string" &&
        typeof d.heatwave === "boolean" &&
        typeof d.risk === "string" &&
        d.risk.trim().length > 0 &&
        typeof d.temperature?.max === "number" &&
        typeof d.temperature?.mean === "number" &&
        typeof d.wbgt?.max === "number" &&
        typeof d.wbgt?.mean === "number" &&
        typeof d.rain?.total === "number" &&
        typeof d.rain?.status === "string");
}
/** GET /api/predict?latitude=..&longitude=.. */
export async function getForecast(latitude, longitude) {
    const url = `${BASE_URL}/api/predict?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`;
    let res;
    try {
        res = await fetchWithTimeout(url);
    }
    catch {
        throw new ApiError("Could not reach the prediction server. Please check your connection and make sure the server is running.");
    }
    if (!res.ok)
        throw new ApiError(friendlyStatusMessage(res.status), res.status);
    let data;
    try {
        data = await res.json();
    }
    catch {
        throw new ApiError("The prediction service returned data we could not read.");
    }
    const payload = data;
    if (!payload ||
        typeof payload.location?.latitude !== "number" ||
        typeof payload.location?.longitude !== "number" ||
        !Array.isArray(payload.forecast)) {
        throw new ApiError("The prediction service returned data in an unexpected format.");
    }
    const forecast = payload.forecast.filter(isValidDay);
    if (forecast.length === 0) {
        throw new ApiError("No forecast data is available for this location right now.");
    }
    return { location: payload.location, forecast };
}
/** Client-side guard mirroring the backend's coordinate rules. */
export function validateCoordinates(latitudeInput, longitudeInput) {
    const lat = Number(latitudeInput);
    const lon = Number(longitudeInput);
    if (latitudeInput.trim() === "" || Number.isNaN(lat))
        return { ok: false, message: "Please enter a latitude, for example 28.67." };
    if (longitudeInput.trim() === "" || Number.isNaN(lon))
        return { ok: false, message: "Please enter a longitude, for example 77.43." };
    if (lat < -90 || lat > 90)
        return { ok: false, message: "Latitude must be between -90 and 90." };
    if (lon < -180 || lon > 180)
        return { ok: false, message: "Longitude must be between -180 and 180." };
    return { ok: true, latitude: lat, longitude: lon };
}
