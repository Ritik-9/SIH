import { jsxs, jsx } from "react/jsx-runtime";
import { MapPin, Sparkles, TriangleAlert } from "lucide-react";
import { StateRiskMap } from "./StateRiskMap";

export function Hero({ selectedState, onStateChange, loading, validationMessage, onScanComplete, setLoading }) {
  return jsxs("section", {
    id: "dashboard",
    className: "relative overflow-hidden deep-panel",
    children: [
      jsx("div", { "aria-hidden": true, className: "pointer-events-none absolute -right-24 -top-32 size-[28rem] rounded-full opacity-30 blur-3xl", style: { background: "radial-gradient(circle, var(--risk-high), transparent 65%)" } }),
      jsx("div", { "aria-hidden": true, className: "pointer-events-none absolute -bottom-40 -left-20 size-[26rem] rounded-full opacity-25 blur-3xl", style: { background: "radial-gradient(circle, var(--color-accent), transparent 65%)" } }),
      jsxs("div", {
        className: "relative mx-auto grid w-full max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[0.85fr_1.15fr] lg:py-20",
        children: [
          jsxs("div", {
            className: "fade-rise lg:pt-8",
            children: [
              jsxs("span", { className: "inline-flex items-center gap-2 rounded-full glass-chip px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em]", children: [jsx(Sparkles, { className: "size-3.5" }), "AI-Powered Heatwave Early Warning & Risk Assessment"] }),
              jsx("h1", { className: "mt-6 max-w-2xl text-4xl font-semibold leading-[1.08] sm:text-5xl lg:text-6xl", children: "Know the Heat. Understand the Risk. Stay Safe." }),
              jsx("p", { className: "mt-5 max-w-xl text-base leading-relaxed opacity-85 sm:text-lg", children: "Select a state to explore heatwave risk across multiple locations. HeatGuard sends those locations to the AI prediction backend and visualizes the returned risk levels on the map.", }),
              jsxs("dl", { className: "mt-8 grid max-w-lg grid-cols-2 gap-3 sm:grid-cols-3", children: [
                { k: "WBGT-based", v: "Heat stress detection" },
                { k: "7-day", v: "Daily risk outlook" },
                { k: "Live", v: "Prediction service" },
              ].map((item) => jsxs("div", { className: "rounded-xl glass-chip px-3 py-3", children: [jsx("dt", { className: "font-display text-sm font-semibold", children: item.k }), jsx("dd", { className: "mt-0.5 text-xs opacity-80", children: item.v })] }, item.k)), }),
              selectedState && jsxs("div", { className: "mt-8 inline-flex items-center gap-2 rounded-xl bg-white/10 px-4 py-3 text-sm font-semibold", children: [jsx(MapPin, { className: "size-4" }), selectedState, " selected"] }),
            ],
          }),
          jsxs("div", {
            className: "fade-rise rounded-2xl border border-white/20 bg-white/95 p-5 text-foreground shadow-2xl backdrop-blur sm:p-6",
            children: [
              jsxs("div", { className: "flex items-center gap-2", children: [jsx(MapPin, { className: "size-4 text-primary" }), jsx("h2", { className: "font-display text-lg font-semibold", children: "State Heat Risk Map" })] }),
              jsx("p", { className: "mt-1.5 text-sm text-muted-foreground", children: "The map starts with the whole of India. Selecting a state automatically zooms into it and runs backend predictions for multiple locations.", }),
              jsx(StateRiskMap, { selectedState, onStateChange, onScanComplete, loading, setLoading }),
              validationMessage && jsxs("p", { className: "mt-4 flex items-start gap-2 rounded-xl border border-risk-moderate/45 bg-risk-moderate-soft px-3 py-2.5 text-sm font-medium text-foreground", children: [jsx(TriangleAlert, { className: "mt-0.5 size-4 shrink-0 text-risk-high" }), validationMessage] }),
            ],
          }),
        ],
      }),
    ],
  });
}
