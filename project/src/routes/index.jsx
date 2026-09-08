import { useCallback, useEffect, useMemo, useState } from "react";
import { Navbar } from "@/components/heatguard/Navbar";
import { Hero } from "@/components/heatguard/Hero";
import { LoadingState } from "@/components/heatguard/LoadingState";
import { ErrorState } from "@/components/heatguard/ErrorState";
import { LocationCard } from "@/components/heatguard/LocationCard";
import { RiskOverview } from "@/components/heatguard/RiskOverview";
import { HeatwaveAlert } from "@/components/heatguard/HeatwaveAlert";
import { MetricsGrid } from "@/components/heatguard/MetricsGrid";
import { WbgtSection } from "@/components/heatguard/WbgtSection";
import { ForecastList } from "@/components/heatguard/ForecastList";
import { Charts } from "@/components/heatguard/Charts";
import { SafetySection } from "@/components/heatguard/SafetySection";
import { HowItWorks } from "@/components/heatguard/HowItWorks";
import { SystemArchitecture } from "@/components/heatguard/SystemArchitecture";
import { Footer } from "@/components/heatguard/Footer";
import { checkBackendHealth, getForecast, ApiError } from "@/lib/api";

function Index() {
  const [selectedState, setSelectedState] = useState("");
  const [forecastData, setForecastData] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationMessage, setValidationMessage] = useState(null);
  const [status, setStatus] = useState("checking");
  const [lastCoords, setLastCoords] = useState(null);

  useEffect(() => {
    let active = true;
    checkBackendHealth().then((ok) => {
      if (active) setStatus(ok ? "online" : "offline");
    });
    return () => { active = false; };
  }, []);

  const handleScanComplete = useCallback((forecast, representative) => {
    const forecastArray = Array.isArray(forecast) ? forecast : forecast?.forecast;
    if (!Array.isArray(forecastArray) || forecastArray.length === 0) {
      setError("The prediction service returned an invalid forecast for the selected state.");
      return;
    }
    setError(null);
    setValidationMessage(null);
    setForecastData({
      location: {
        latitude: representative.latitude,
        longitude: representative.longitude,
      },
      forecast: forecastArray,
    });
    setLastCoords({ lat: representative.latitude, lon: representative.longitude });
    setSelectedIndex(0);

    if ("Notification" in window && Notification.permission === "granted") {
      const extreme = forecast.some((day) => String(day.risk ?? "").trim().toLowerCase() === "extreme");
      if (extreme) {
        new Notification("🚨 HeatGuard: Extreme Heat Risk", {
          body: `${selectedState} contains sampled locations with Extreme heat risk in the backend forecast.`,
          icon: "/favicon.ico",
        });
      }
    }
  }, [selectedState]);

  const handleStateChange = useCallback((state) => {
    setSelectedState(state);
    setForecastData(null);
    setError(null);
    setValidationMessage(null);
    setSelectedIndex(0);
  }, []);

  const handleRetry = useCallback(() => {
    if (!lastCoords) return;
    setLoading(true);
    setError(null);
    getForecast(lastCoords.lat, lastCoords.lon)
      .then((data) => {
        setForecastData(data);
        setSelectedIndex(0);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Could not refresh the prediction.");
      })
      .finally(() => setLoading(false));
  }, [lastCoords]);

  const selectedDay = useMemo(() => {
    if (!forecastData) return null;
    return forecastData.forecast[selectedIndex] ?? forecastData.forecast[0] ?? null;
  }, [forecastData, selectedIndex]);

  const showResults = Boolean(forecastData && selectedDay && !loading && !error);

  return (
    <div className="min-h-screen bg-background">
      <Navbar status={status} />
      <Hero
        selectedState={selectedState}
        onStateChange={handleStateChange}
        loading={loading}
        validationMessage={validationMessage}
        onScanComplete={handleScanComplete}
        setLoading={setLoading}
      />
      <main className="mx-auto w-full max-w-7xl space-y-12 px-4 py-12 sm:px-6 sm:py-16">
        {loading && <LoadingState />}
        {!loading && error && <ErrorState message={error} onRetry={handleRetry} />}
        {!loading && !error && !showResults && !selectedState && (
          <section className="fade-rise rounded-2xl border border-border bg-secondary/20 px-6 py-10 text-center">
            <p className="font-display text-xl font-semibold">Select a state to begin</p>
            <p className="mt-2 text-sm text-muted-foreground">Choose a state above to run backend heat-risk predictions across multiple sampled locations.</p>
          </section>
        )}
        {showResults && (
          <div className="space-y-12">
            <LocationCard stateName={selectedState} />
            <HeatwaveAlert forecast={forecastData.forecast} />
            {selectedDay && <RiskOverview day={selectedDay} />}
            {selectedDay && <MetricsGrid day={selectedDay} />}
            {selectedDay && <WbgtSection day={selectedDay} />}
            <ForecastList forecast={forecastData.forecast} selectedIndex={selectedIndex} onSelect={setSelectedIndex} />
            <Charts forecast={forecastData.forecast} />
            <SafetySection />
            <HowItWorks />
            <SystemArchitecture />
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

export default Index;
