import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Info, Waves } from "lucide-react";
import { WBGT_THRESHOLD } from "@/lib/risk";
function pct(value) {
    return Math.max(0, Math.min(100, (value / 40) * 100));
}
export function WbgtSection({ day }) {
    const over = day.wbgt.max >= WBGT_THRESHOLD;
    return (_jsx("section", { className: "fade-rise overflow-hidden rounded-2xl deep-panel p-6 sm:p-8", children: _jsxs("div", { className: "grid gap-8 lg:grid-cols-[0.95fr_1.05fr]", children: [_jsxs("div", { children: [_jsxs("span", { className: "inline-flex items-center gap-2 rounded-full glass-chip px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em]", children: [_jsx(Waves, { className: "size-3.5" }), "Heat stress index"] }), _jsx("h2", { className: "mt-5 text-2xl font-semibold sm:text-3xl", children: "Wet Bulb Globe Temperature (WBGT)" }), _jsx("p", { className: "mt-3 max-w-lg text-sm leading-relaxed opacity-85", children: "WBGT is a heat-stress indicator that accounts for environmental conditions affecting how the human body experiences heat." }), _jsxs("p", { className: "mt-5 flex items-start gap-2 rounded-xl glass-chip px-3.5 py-3 text-xs leading-relaxed", children: [_jsx(Info, { className: "mt-0.5 size-4 shrink-0" }), "Heatwave detection, including the ", WBGT_THRESHOLD, "\u00B0C threshold and duration condition, is performed entirely by the prediction service."] })] }), _jsxs("div", { className: "rounded-2xl glass-chip p-5 sm:p-6", children: [_jsx(Gauge, { label: "Maximum WBGT", value: day.wbgt.max, highlight: over }), _jsx("div", { className: "mt-6", children: _jsx(Gauge, { label: "Mean WBGT", value: day.wbgt.mean, highlight: day.wbgt.mean >= WBGT_THRESHOLD }) }), _jsxs("div", { className: "mt-6 flex items-center justify-between border-t border-white/20 pt-4 text-sm", children: [_jsx("span", { className: "opacity-80", children: "Heatwave threshold" }), _jsxs("span", { className: "font-display text-lg font-semibold", children: [WBGT_THRESHOLD, " \u00B0C"] })] })] })] }) }));
}
function Gauge({ label, value, highlight }) {
    return (_jsxs("div", { children: [_jsxs("div", { className: "flex items-end justify-between", children: [_jsx("span", { className: "text-xs font-semibold uppercase tracking-wide opacity-80", children: label }), _jsxs("span", { className: "font-display text-2xl font-semibold", children: [value.toFixed(1), " \u00B0C"] })] }), _jsxs("div", { className: "relative mt-3 h-3 w-full overflow-hidden rounded-full bg-white/20", children: [_jsx("div", { className: "h-full rounded-full transition-all duration-700", style: {
                            width: `${pct(value)}%`,
                            background: highlight
                                ? "linear-gradient(90deg, var(--risk-high), var(--risk-extreme))"
                                : "linear-gradient(90deg, var(--risk-low), var(--risk-moderate))",
                        } }), _jsx("span", { className: "absolute top-0 h-full w-0.5 bg-white/85", style: { left: `${pct(WBGT_THRESHOLD)}%` }, "aria-hidden": true })] }), _jsx("p", { className: "mt-2 text-xs opacity-75", children: highlight
                    ? `At or above the ${WBGT_THRESHOLD}°C heat-stress threshold`
                    : `Below the ${WBGT_THRESHOLD}°C heat-stress threshold` })] }));
}
