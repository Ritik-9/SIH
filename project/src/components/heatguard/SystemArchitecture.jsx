import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { SectionHeading } from "./MetricsGrid";
const LAYERS = [
    { label: "USER", sub: "Browser / Mobile" },
    { label: "REACT FRONTEND", sub: "HeatGuard Dashboard" },
    { label: "FASTAPI REST API", sub: "Prediction Service" },
    { label: "WEATHER DATA + WBGT + ML MODEL", sub: "Heat Stress Analysis" },
    { label: "PREDICTION RESPONSE", sub: "JSON Forecast" },
    { label: "HEATGUARD DASHBOARD", sub: "Risk Visualization" },
];
export function SystemArchitecture() {
    return (_jsxs("section", { children: [_jsx(SectionHeading, { title: "System Architecture", subtitle: "End-to-end data flow from user input through the ML backend to the dashboard." }), _jsx("div", { className: "fade-rise mt-5 rounded-2xl border border-border bg-secondary/30 p-6 sm:p-8", children: _jsx("div", { className: "mx-auto flex max-w-md flex-col items-center gap-1", children: LAYERS.map((layer, i) => (_jsxs("div", { className: "flex w-full flex-col items-center", children: [_jsxs("div", { className: `w-full rounded-xl border px-5 py-4 text-center ${i === 0 || i === LAYERS.length - 1
                                    ? "border-primary/30 bg-card"
                                    : i === 3
                                        ? "border-risk-high/40 bg-risk-high-soft"
                                        : "border-border bg-card"}`, children: [_jsx("p", { className: "font-display text-sm font-bold tracking-wide", children: layer.label }), _jsx("p", { className: "mt-0.5 text-xs text-muted-foreground", children: layer.sub })] }), i < LAYERS.length - 1 && (_jsx("svg", { className: "size-5 py-0.5 text-muted-foreground/50", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", children: _jsx("path", { d: "M12 5v14M6 13l6 6 6-6" }) }))] }, layer.label))) }) })] }));
}
