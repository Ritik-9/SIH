import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis, } from "recharts";
import { CloudRain } from "lucide-react";
import { formatDate, WBGT_THRESHOLD } from "@/lib/risk";
import { SectionHeading } from "./MetricsGrid";
const axis = { fontSize: 12, fill: "var(--muted-foreground)" };
function tooltipStyle() {
    return {
        contentStyle: {
            borderRadius: 12,
            border: "1px solid var(--color-border)",
            background: "var(--color-card)",
            fontSize: 12,
            boxShadow: "var(--shadow-card)",
        },
    };
}
export function Charts({ forecast }) {
    const data = forecast.map((d) => ({
        date: formatDate(d.date),
        tempMax: d.temperature.max,
        tempMean: d.temperature.mean,
        wbgtMax: d.wbgt.max,
        wbgtMean: d.wbgt.mean,
        rain: d.rain.total,
        overThreshold: d.wbgt.max >= WBGT_THRESHOLD,
    }));
    return (_jsxs("section", { className: "space-y-5", children: [_jsx(SectionHeading, { title: "Interactive Charts", subtitle: "All series are rendered from the prediction response." }), _jsxs("div", { className: "grid gap-5 xl:grid-cols-2", children: [_jsx(ChartCard, { title: "Temperature Forecast", note: "Daily maximum and mean air temperature (\u00B0C)", children: _jsx(ResponsiveContainer, { width: "100%", height: 280, children: _jsxs(LineChart, { data: data, margin: { top: 8, right: 12, left: 0, bottom: 4 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border)", vertical: false }), _jsx(XAxis, { dataKey: "date", tick: axis, tickLine: false, axisLine: false }), _jsx(YAxis, { tick: axis, tickLine: false, axisLine: false, width: 48, label: { value: "°C", angle: -90, position: "insideLeft", style: axis } }), _jsx(Tooltip, { formatter: (v) => `${Number(v).toFixed(1)} °C`, ...tooltipStyle() }), _jsx(Legend, { wrapperStyle: { fontSize: 12 } }), _jsx(Line, { type: "monotone", dataKey: "tempMax", name: "Max temperature", stroke: "var(--risk-high)", strokeWidth: 2.5, dot: { r: 3 }, activeDot: { r: 5 } }), _jsx(Line, { type: "monotone", dataKey: "tempMean", name: "Mean temperature", stroke: "var(--color-accent)", strokeWidth: 2.5, dot: { r: 3 }, activeDot: { r: 5 } })] }) }) }), _jsx(ChartCard, { title: "WBGT Heat Stress Forecast", note: `Reference line at the ${WBGT_THRESHOLD}°C heatwave threshold`, children: _jsx(ResponsiveContainer, { width: "100%", height: 280, children: _jsxs(LineChart, { data: data, margin: { top: 8, right: 12, left: 0, bottom: 4 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border)", vertical: false }), _jsx(XAxis, { dataKey: "date", tick: axis, tickLine: false, axisLine: false }), _jsx(YAxis, { tick: axis, tickLine: false, axisLine: false, width: 48, label: { value: "°C", angle: -90, position: "insideLeft", style: axis } }), _jsx(Tooltip, { formatter: (v) => `${Number(v).toFixed(1)} °C`, ...tooltipStyle() }), _jsx(Legend, { wrapperStyle: { fontSize: 12 } }), _jsx(ReferenceLine, { y: WBGT_THRESHOLD, stroke: "var(--risk-extreme)", strokeDasharray: "6 4", label: {
                                            value: "Heatwave Threshold",
                                            position: "insideTopRight",
                                            fill: "var(--risk-extreme)",
                                            fontSize: 11,
                                        } }), _jsx(Line, { type: "monotone", dataKey: "wbgtMax", name: "Max WBGT", stroke: "var(--risk-veryhigh)", strokeWidth: 2.5, dot: (props) => {
                                            const { cx, cy, payload, index } = props;
                                            return (_jsx("circle", { cx: cx, cy: cy, r: payload.overThreshold ? 5.5 : 3, fill: payload.overThreshold ? "var(--risk-extreme)" : "var(--risk-veryhigh)", stroke: "var(--color-card)", strokeWidth: payload.overThreshold ? 2 : 0 }, index));
                                        } }), _jsx(Line, { type: "monotone", dataKey: "wbgtMean", name: "Mean WBGT", stroke: "var(--color-primary)", strokeWidth: 2.5, dot: { r: 3 } })] }) }) })] }), _jsx(ChartCard, { title: "Rainfall Forecast", note: "Total daily rainfall (mm)", icon: _jsx(CloudRain, { className: "size-4 text-accent" }), children: _jsx(ResponsiveContainer, { width: "100%", height: 260, children: _jsxs(BarChart, { data: data, margin: { top: 8, right: 12, left: 0, bottom: 4 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border)", vertical: false }), _jsx(XAxis, { dataKey: "date", tick: axis, tickLine: false, axisLine: false }), _jsx(YAxis, { tick: axis, tickLine: false, axisLine: false, width: 48, label: { value: "mm", angle: -90, position: "insideLeft", style: axis } }), _jsx(Tooltip, { formatter: (v) => `${Number(v).toFixed(1)} mm`, ...tooltipStyle() }), _jsx(Legend, { wrapperStyle: { fontSize: 12 } }), _jsx(Bar, { dataKey: "rain", name: "Rainfall", radius: [8, 8, 0, 0], maxBarSize: 54, children: data.map((entry, i) => (_jsx(Cell, { fill: entry.rain > 0 ? "var(--color-accent)" : "var(--color-border)" }, i))) })] }) }) })] }));
}
function ChartCard({ title, note, icon, children, }) {
    return (_jsxs("article", { className: "fade-rise surface-card p-5 sm:p-6", children: [_jsxs("div", { className: "mb-4 flex items-start justify-between gap-3", children: [_jsxs("div", { children: [_jsx("h3", { className: "font-display text-lg font-semibold", children: title }), _jsx("p", { className: "mt-1 text-xs text-muted-foreground", children: note })] }), icon] }), _jsx("div", { className: "w-full overflow-hidden", children: children })] }));
}
