import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Droplets, Sun, Snowflake, Users } from "lucide-react";
import { SectionHeading } from "./MetricsGrid";
const RECOMMENDATIONS = [
    {
        icon: _jsx(Droplets, { className: "size-5 text-accent" }),
        title: "Stay Hydrated",
        description: "Drink water frequently throughout the day, even before you feel thirsty. Avoid alcohol and sugary drinks during extreme heat.",
    },
    {
        icon: _jsx(Sun, { className: "size-5 text-risk-high" }),
        title: "Avoid Peak Heat",
        description: "Limit outdoor activity between 11 AM and 4 PM when temperatures and WBGT values are typically at their highest.",
    },
    {
        icon: _jsx(Snowflake, { className: "size-5 text-primary" }),
        title: "Stay Cool",
        description: "Use fans, air conditioning, or cool showers. Wear lightweight, light-colored clothing and stay in shaded areas.",
    },
    {
        icon: _jsx(Users, { className: "size-5 text-risk-veryhigh" }),
        title: "Protect Vulnerable People",
        description: "Check on elderly, children, and those with health conditions. They are more susceptible to heat-related illness.",
    },
];
export function SafetySection() {
    return (_jsxs("section", { id: "safety", children: [_jsx(SectionHeading, { title: "Heat Safety Recommendations", subtitle: "General public-safety guidelines to follow during periods of elevated heat stress." }), _jsx("div", { className: "mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4", children: RECOMMENDATIONS.map((rec) => (_jsxs("article", { className: "fade-rise surface-card lift-hover p-5", children: [_jsx("span", { className: "flex size-11 items-center justify-center rounded-xl bg-secondary", children: rec.icon }), _jsx("h3", { className: "mt-4 font-display text-base font-semibold", children: rec.title }), _jsx("p", { className: "mt-2 text-sm leading-relaxed text-muted-foreground", children: rec.description })] }, rec.title))) })] }));
}
