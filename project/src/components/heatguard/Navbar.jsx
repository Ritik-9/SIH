import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Flame, Menu, X } from "lucide-react";
import { useState } from "react";
const LINKS = [
    { label: "Dashboard", href: "#dashboard" },
    { label: "Forecast", href: "#forecast" },
    { label: "Risk Analysis", href: "#risk-analysis" },
    { label: "Safety", href: "#safety" },
];
export function Navbar({ status }) {
    const [open, setOpen] = useState(false);
    const statusLabel = status === "online" ? "System Online" : status === "offline" ? "System Offline" : "Checking system…";
    const statusColor = status === "online" ? "bg-risk-low" : status === "offline" ? "bg-destructive" : "bg-risk-moderate";
    return (_jsxs("header", { className: "sticky top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur-xl", children: [_jsxs("div", { className: "mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6", children: [_jsxs("a", { href: "#dashboard", className: "flex items-center gap-3", children: [_jsx("span", { className: "flex size-10 items-center justify-center rounded-xl deep-panel shadow-sm", children: _jsx(Flame, { className: "size-5" }) }), _jsxs("span", { className: "leading-tight", children: [_jsx("span", { className: "block font-display text-lg font-semibold tracking-tight", children: "HeatGuard" }), _jsx("span", { className: "block text-[11px] font-medium uppercase tracking-[0.16em] text-muted-foreground", children: "Heatwave Intelligence" })] })] }), _jsx("nav", { className: "hidden items-center gap-1 md:flex", children: LINKS.map((l) => (_jsx("a", { href: l.href, className: "rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground", children: l.label }, l.href))) }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsxs("span", { className: "flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 text-xs font-semibold text-foreground shadow-sm", children: [_jsx("span", { className: `size-2 rounded-full ${statusColor} ${status === "checking" ? "pulse-dot" : ""}` }), _jsx("span", { className: "hidden sm:inline", children: statusLabel })] }), _jsx("button", { type: "button", "aria-label": "Toggle navigation", onClick: () => setOpen((v) => !v), className: "flex size-10 items-center justify-center rounded-lg border border-border bg-card md:hidden", children: open ? _jsx(X, { className: "size-4" }) : _jsx(Menu, { className: "size-4" }) })] })] }), open && (_jsx("nav", { className: "border-t border-border bg-card px-4 py-2 md:hidden", children: LINKS.map((l) => (_jsx("a", { href: l.href, onClick: () => setOpen(false), className: "block rounded-lg px-3 py-3 text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground", children: l.label }, l.href))) }))] }));
}
