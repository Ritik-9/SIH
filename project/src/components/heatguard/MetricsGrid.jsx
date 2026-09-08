import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Activity, CloudRain, Droplets, Gauge, Thermometer, ThermometerSun } from "lucide-react";
import { formatDate } from "@/lib/risk";
export function MetricsGrid({ day }) {
    const metrics = [
        {
            icon: _jsx(ThermometerSun, { className: "size-5 text-risk-high" }),
            label: "Maximum Temperature",
            value: `${day.temperature.max.toFixed(1)}`,
            unit: "°C",
        },
        {
            icon: _jsx(Thermometer, { className: "size-5 text-accent" }),
            label: "Mean Temperature",
            value: `${day.temperature.mean.toFixed(1)}`,
            unit: "°C",
        },
        {
            icon: _jsx(Activity, { className: "size-5 text-risk-veryhigh" }),
            label: "Maximum WBGT",
            value: `${day.wbgt.max.toFixed(1)}`,
            unit: "°C",
        },
        {
            icon: _jsx(Gauge, { className: "size-5 text-primary" }),
            label: "Mean WBGT",
            value: `${day.wbgt.mean.toFixed(1)}`,
            unit: "°C",
        },
        {
            icon: _jsx(Droplets, { className: "size-5 text-accent" }),
            label: "Rainfall",
            value: `${day.rain.total.toFixed(1)}`,
            unit: "mm",
        },
        {
            icon: _jsx(CloudRain, { className: "size-5 text-primary" }),
            label: "Rain Status",
            value: day.rain.status,
            unit: "",
        },
    ];
    return (_jsxs("section", { children: [_jsx(SectionHeading, { title: "Weather Metrics", subtitle: `Values reported for ${formatDate(day.date, { weekday: "long", day: "numeric", month: "long" })}` }), _jsx("div", { className: "mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3", children: metrics.map((m) => (_jsxs("article", { className: "fade-rise surface-card lift-hover p-5", children: [_jsxs("div", { className: "flex items-center justify-between gap-3", children: [_jsx("p", { className: "text-xs font-semibold uppercase tracking-wide text-muted-foreground", children: m.label }), _jsx("span", { className: "flex size-9 items-center justify-center rounded-lg bg-secondary", children: m.icon })] }), _jsxs("p", { className: "mt-4 font-display text-3xl font-semibold", children: [m.value, m.unit && _jsx("span", { className: "ml-1 text-base font-medium text-muted-foreground", children: m.unit })] })] }, m.label))) })] }));
}
export function SectionHeading({ title, subtitle }) {
    return (_jsxs("div", { children: [_jsx("h2", { className: "font-display text-2xl font-semibold sm:text-3xl", children: title }), subtitle && _jsx("p", { className: "mt-1.5 text-sm text-muted-foreground", children: subtitle })] }));
}
