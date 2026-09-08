import { Globe2, MapPin } from "lucide-react";

export function LocationCard({ stateName }) {
  return (
    <section className="fade-rise surface-card overflow-hidden">
      <div className="grid gap-0 md:grid-cols-[1fr_1fr]">
        <div className="p-6 sm:p-8">
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            <MapPin className="size-3.5 text-primary" /> Analyzed State
          </p>
          <h2 className="mt-4 font-display text-2xl font-semibold">{stateName || "Selected state"}</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            HeatGuard analysed multiple sampled locations inside this state using the live backend prediction service.
          </p>
          <div className="mt-6 rounded-xl border border-border bg-secondary/60 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Representative forecast</p>
            <p className="mt-1 text-sm font-semibold">The highest-risk sampled location is used for the detailed forecast below.</p>
          </div>
        </div>
        <div className="relative min-h-56 deep-panel p-6 sm:p-8">
          <div className="absolute inset-0 opacity-25">
            <div className="size-full" style={{ backgroundImage: "linear-gradient(oklch(1 0 0 / 0.25) 1px, transparent 1px), linear-gradient(90deg, oklch(1 0 0 / 0.25) 1px, transparent 1px)", backgroundSize: "8.333% 11.11%" }} />
          </div>
          <div className="relative flex h-full min-h-44 items-center justify-center">
            <div className="text-center">
              <Globe2 className="mx-auto size-10 opacity-80" />
              <p className="mt-3 text-sm font-semibold">State-wide risk scan complete</p>
              <p className="mt-1 text-xs opacity-75">Detailed results below are based on the backend's sampled locations.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
