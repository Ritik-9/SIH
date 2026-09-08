import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { CloudRain, Flame, ShieldCheck } from "lucide-react";
import { formatDate, riskStyle } from "@/lib/risk";
import { SectionHeading } from "./MetricsGrid";
export function ForecastList({ forecast, selectedIndex, onSelect }) {
    return (_jsxs("section", { id: "forecast", children: [_jsx(SectionHeading, { title: `${forecast.length}-Day Heat Risk Forecast`, subtitle: "Select a day to update the metrics, WBGT analysis and charts above." }), _jsx("div", { className: "mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4", children: forecast.map((day, index) => {
                    const style = riskStyle(day.risk);
                    const selected = index === selectedIndex;
                    return (_jsxs("button", { type: "button", onClick: () => onSelect(index), "aria-pressed": selected, className: `fade-rise surface-card lift-hover text-left p-5 transition ${selected ? "ring-2 ring-primary ring-offset-2 ring-offset-background" : ""}`, children: [_jsxs("div", { className: "flex items-center justify-between gap-2", children: [_jsx("p", { className: "font-display text-sm font-semibold", children: formatDate(day.date) }), _jsx("span", { className: `rounded-full border px-2.5 py-1 text-[11px] font-semibold ${style.border} ${style.bg} ${style.text}`, children: style.label })] }), _jsxs("p", { className: `mt-3 flex items-center gap-1.5 text-xs font-semibold ${day.heatwave ? "text-risk-veryhigh" : "text-risk-low"}`, children: [day.heatwave ? _jsx(Flame, { className: "size-3.5" }) : _jsx(ShieldCheck, { className: "size-3.5" }), day.heatwave ? "Heatwave" : "No heatwave"] }), _jsxs("dl", { className: "mt-4 space-y-1.5 text-xs", children: [_jsx(Row, { label: "Temp max / mean", value: `${day.temperature.max.toFixed(1)} / ${day.temperature.mean.toFixed(1)} °C` }), _jsx(Row, { label: "WBGT max / mean", value: `${day.wbgt.max.toFixed(1)} / ${day.wbgt.mean.toFixed(1)} °C` }), _jsx(Row, { label: "Rainfall", value: `${day.rain.total.toFixed(1)} mm` })] }), _jsxs("p", { className: "mt-4 flex items-center gap-1.5 border-t border-border/70 pt-3 text-xs font-medium text-muted-foreground", children: [_jsx(CloudRain, { className: "size-3.5" }), day.rain.status] })] }, `${day.date}-${index}`));
                }) })] }));
}
function Row({ label, value }) {
    return (_jsxs("div", { className: "flex items-center justify-between gap-2", children: [_jsx("dt", { className: "text-muted-foreground", children: label }), _jsx("dd", { className: "font-semibold", children: value })] }));
}
