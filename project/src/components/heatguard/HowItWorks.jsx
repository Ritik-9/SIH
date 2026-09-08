import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Crosshair, CloudSun, Flame, BellRing } from "lucide-react";
import { SectionHeading } from "./MetricsGrid";
const STEPS = [
    {
        number: "01",
        icon: _jsx(Crosshair, { className: "size-5" }),
        title: "Location",
        description: "User provides latitude and longitude or uses GPS to identify the area for analysis.",
    },
    {
        number: "02",
        icon: _jsx(CloudSun, { className: "size-5" }),
        title: "Weather Data",
        description: "The backend retrieves environmental data including temperature and rainfall for the target location.",
    },
    {
        number: "03",
        icon: _jsx(Flame, { className: "size-5" }),
        title: "Heat Stress Analysis",
        description: "WBGT and ML-based models assess heat stress levels and detect heatwave conditions.",
    },
    {
        number: "04",
        icon: _jsx(BellRing, { className: "size-5" }),
        title: "Early Warning",
        description: "Risk levels and heatwave alerts are delivered to the dashboard for proactive decision-making.",
    },
];
export function HowItWorks() {
    return (_jsxs("section", { children: [_jsx(SectionHeading, { title: "How the System Works", subtitle: "From location input to early warning \u2014 the four-stage heatwave risk pipeline." }), _jsx("div", { className: "mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4", children: STEPS.map((step, i) => (_jsxs("div", { className: "relative", children: [_jsxs("article", { className: "fade-rise surface-card lift-hover p-5", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "flex size-11 items-center justify-center rounded-xl deep-panel", children: step.icon }), _jsx("span", { className: "font-display text-2xl font-bold text-muted-foreground/30", children: step.number })] }), _jsx("h3", { className: "mt-4 font-display text-base font-semibold", children: step.title }), _jsx("p", { className: "mt-2 text-sm leading-relaxed text-muted-foreground", children: step.description })] }), i < STEPS.length - 1 && (_jsx("div", { className: "hidden lg:block absolute top-1/2 -right-2 z-10 text-muted-foreground/40", children: _jsx("svg", { className: "size-4", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", children: _jsx("path", { d: "M5 12h14M13 6l6 6-6 6" }) }) }))] }, step.number))) }), _jsxs("div", { className: "fade-rise mt-5 flex flex-wrap items-center justify-center gap-2 rounded-2xl border border-border bg-secondary/40 px-5 py-4 text-sm font-medium text-muted-foreground", children: [_jsx("span", { className: "rounded-lg bg-card px-3 py-1.5 shadow-sm", children: "User Location" }), _jsx(Arrow, {}), _jsx("span", { className: "rounded-lg bg-card px-3 py-1.5 shadow-sm", children: "Weather Data" }), _jsx(Arrow, {}), _jsx("span", { className: "rounded-lg bg-card px-3 py-1.5 shadow-sm", children: "WBGT + ML Analysis" }), _jsx(Arrow, {}), _jsx("span", { className: "rounded-lg bg-card px-3 py-1.5 shadow-sm text-risk-high", children: "Heatwave Risk Warning" })] })] }));
}
function Arrow() {
    return (_jsx("svg", { className: "size-4 text-muted-foreground/50", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", children: _jsx("path", { d: "M5 12h14M13 6l6 6-6 6" }) }));
}
