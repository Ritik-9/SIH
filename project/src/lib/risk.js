const MAP = {
    low: {
        key: "low",
        label: "Low",
        text: "text-risk-low",
        bg: "bg-risk-low-soft",
        border: "border-risk-low/40",
        dot: "bg-risk-low",
        chart: "var(--risk-low)",
        scale: 0.15,
    },
    moderate: {
        key: "moderate",
        label: "Moderate",
        text: "text-risk-moderate",
        bg: "bg-risk-moderate-soft",
        border: "border-risk-moderate/45",
        dot: "bg-risk-moderate",
        chart: "var(--risk-moderate)",
        scale: 0.4,
    },
    high: {
        key: "high",
        label: "High",
        text: "text-risk-high",
        bg: "bg-risk-high-soft",
        border: "border-risk-high/45",
        dot: "bg-risk-high",
        chart: "var(--risk-high)",
        scale: 0.65,
    },
    "very high": {
        key: "veryhigh",
        label: "Very High",
        text: "text-risk-veryhigh",
        bg: "bg-risk-veryhigh-soft",
        border: "border-risk-veryhigh/45",
        dot: "bg-risk-veryhigh",
        chart: "var(--risk-veryhigh)",
        scale: 0.85,
    },
    extreme: {
        key: "extreme",
        label: "Extreme",
        text: "text-risk-extreme",
        bg: "bg-risk-extreme-soft",
        border: "border-risk-extreme/50",
        dot: "bg-risk-extreme",
        chart: "var(--risk-extreme)",
        scale: 1,
    },
};
/** Presentation-only mapping of the backend risk string. No risk is computed here. */
export function riskStyle(risk) {
    const key = (risk ?? "").trim().toLowerCase();
    const found = MAP[key];
    if (found)
        return found;
    return {
        key: "unknown",
        label: risk && risk.trim() !== "" ? titleCase(risk) : "Unknown",
        text: "text-muted-foreground",
        bg: "bg-muted",
        border: "border-border",
        dot: "bg-muted-foreground",
        chart: "var(--muted-foreground)",
        scale: 0.1,
    };
}
export function titleCase(value) {
    return value
        .toLowerCase()
        .split(/\s+/)
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");
}
export function formatDate(iso, opts) {
    const d = new Date(`${iso}T00:00:00`);
    if (Number.isNaN(d.getTime()))
        return iso;
    return d.toLocaleDateString(undefined, opts ?? { weekday: "short", day: "numeric", month: "short" });
}
export const WBGT_THRESHOLD = 30;
