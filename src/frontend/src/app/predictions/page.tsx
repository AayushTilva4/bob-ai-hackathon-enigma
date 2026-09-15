"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  TrendingUp,
  Clock,
  AlertTriangle,
  Activity,
  BarChart3,
  RefreshCw,
  Loader2,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PlanWindow {
  label: string;
  start_h: number;
  end_h: number;
  vessel_arrivals: number;
  vessel_names: string[];
  expected_containers: number;
  berth_utilization: number;
  crane_utilization: number;
  yard_utilization: number;
  congestion_risk: string;
  congestion_probability: number;
  expected_waiting_h: number;
  recommendations: string[];
}

interface Plan72H {
  generated_at: string;
  simulation_time: string;
  windows: PlanWindow[];
  summary: string;
  total_arrivals: number;
  peak_window: string;
}

function riskColor(risk: string) {
  switch (risk?.toUpperCase()) {
    case "CRITICAL": return "text-red-400";
    case "HIGH": return "text-orange-400";
    case "MEDIUM": return "text-amber-400";
    default: return "text-emerald-400";
  }
}

function riskBg(risk: string) {
  switch (risk?.toUpperCase()) {
    case "CRITICAL": return "bg-red-950 border-red-800/40";
    case "HIGH": return "bg-orange-950 border-orange-800/40";
    case "MEDIUM": return "bg-amber-950 border-amber-800/40";
    default: return "bg-emerald-950 border-emerald-800/40";
  }
}

function barHeight(value: number) {
  return Math.max(4, Math.round(value * 120));
}

export default function PredictionsPage() {
  const [plan, setPlan] = useState<Plan72H | null>(null);
  const [kpis, setKpis] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [planRes, kpiRes] = await Promise.all([
        fetch(`${API}/api/optimization/plan72h`),
        fetch(`${API}/api/simulation/kpis`),
      ]);

      if (planRes.ok) setPlan(await planRes.json());
      if (kpiRes.ok) setKpis(await kpiRes.json());
      setError(null);
    } catch (e: any) {
      setError(e.message || "Failed to fetch predictions");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/40">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                Congestion Predictions &amp; 72-Hour Operational Plan
              </h2>
              <p className="text-xs text-slate-400">
                Time-windowed demand forecasts, congestion projections, and operational recommendations.
              </p>
            </div>
          </div>
          <button onClick={fetchData} className="p-2 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-400">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="ops-panel rounded-xl p-4 border border-red-900/40 bg-red-950/20 text-red-400 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Current KPIs */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="ops-panel rounded-xl p-4 border border-harbor-border text-center">
            <div className="text-xs font-mono text-slate-400 mb-1">CONGESTION SCORE</div>
            <div className={`text-2xl font-bold font-mono ${riskColor(kpis.congestion_risk)}`}>
              {(kpis.congestion_score * 100).toFixed(0)}
            </div>
            <div className={`text-[10px] font-mono ${riskColor(kpis.congestion_risk)}`}>
              {(kpis.congestion_risk || "LOW").toUpperCase()}
            </div>
          </div>
          <div className="ops-panel rounded-xl p-4 border border-harbor-border text-center">
            <div className="text-xs font-mono text-slate-400 mb-1">WAITING VESSELS</div>
            <div className="text-2xl font-bold font-mono text-white">{kpis.waiting_vessels}</div>
            <div className="text-[10px] font-mono text-slate-500">Queue: {kpis.queue_length}</div>
          </div>
          <div className="ops-panel rounded-xl p-4 border border-harbor-border text-center">
            <div className="text-xs font-mono text-slate-400 mb-1">AVG WAIT TIME</div>
            <div className="text-2xl font-bold font-mono text-white">{kpis.average_waiting_time_h?.toFixed(1) || "0.0"}h</div>
            <div className="text-[10px] font-mono text-slate-500">Handling: {kpis.average_handling_time_h?.toFixed(1) || "0"}h</div>
          </div>
          <div className="ops-panel rounded-xl p-4 border border-harbor-border text-center">
            <div className="text-xs font-mono text-slate-400 mb-1">THROUGHPUT</div>
            <div className="text-2xl font-bold font-mono text-white">{kpis.throughput_teu?.toLocaleString() || 0}</div>
            <div className="text-[10px] font-mono text-slate-500">TEU processed</div>
          </div>
        </div>
      )}

      {/* 72h Plan Summary */}
      {plan && (
        <>
          <div className="ops-panel rounded-xl p-5 border border-harbor-border">
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              72-Hour Demand Forecast
            </h3>
            <p className="text-xs text-slate-400 font-mono mb-4">{plan.summary}</p>

            {/* Bar Chart */}
            <div className="flex items-end gap-3 h-[140px] border-b border-slate-800 pb-2 mb-3">
              {plan.windows.map((w, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  {/* Berth util bar */}
                  <div className="w-full flex gap-[2px] items-end" style={{ height: "120px" }}>
                    <div
                      className="flex-1 rounded-t bg-cyan-600/80 transition-all duration-500"
                      style={{ height: `${barHeight(w.berth_utilization)}px` }}
                      title={`Berth: ${(w.berth_utilization * 100).toFixed(0)}%`}
                    />
                    <div
                      className="flex-1 rounded-t bg-emerald-600/80 transition-all duration-500"
                      style={{ height: `${barHeight(w.crane_utilization)}px` }}
                      title={`Crane: ${(w.crane_utilization * 100).toFixed(0)}%`}
                    />
                    <div
                      className="flex-1 rounded-t bg-amber-600/80 transition-all duration-500"
                      style={{ height: `${barHeight(w.yard_utilization)}px` }}
                      title={`Yard: ${(w.yard_utilization * 100).toFixed(0)}%`}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Window Labels */}
            <div className="flex gap-3">
              {plan.windows.map((w, i) => (
                <div key={i} className="flex-1 text-center">
                  <div className="text-[10px] font-mono text-slate-400">{w.label}</div>
                  <div className={`text-[10px] font-mono font-bold ${riskColor(w.congestion_risk)}`}>
                    {w.congestion_risk}
                  </div>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="flex items-center gap-4 mt-3 text-[10px] font-mono text-slate-500">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-cyan-600" /> Berth</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-emerald-600" /> Crane</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-amber-600" /> Yard</span>
            </div>
          </div>

          {/* Time Windows Detail */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plan.windows.map((w, i) => (
              <div key={i} className={`ops-panel rounded-xl p-4 border ${riskBg(w.congestion_risk)} space-y-3`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-semibold text-white">{w.label}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${riskColor(w.congestion_risk)}`}>
                    {w.congestion_risk}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div>
                    <div className="text-slate-500">Arrivals</div>
                    <div className="text-white font-bold">{w.vessel_arrivals}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Containers</div>
                    <div className="text-white font-bold">{w.expected_containers.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Berth Util</div>
                    <div className="text-white font-bold">{(w.berth_utilization * 100).toFixed(0)}%</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Est. Wait</div>
                    <div className="text-white font-bold">{w.expected_waiting_h.toFixed(1)}h</div>
                  </div>
                </div>

                {w.vessel_names.length > 0 && (
                  <div className="text-[10px] font-mono text-slate-500">
                    Vessels: {w.vessel_names.join(", ")}
                  </div>
                )}

                <div className="space-y-1">
                  {w.recommendations.map((r, ri) => (
                    <div key={ri} className="text-[10px] font-mono text-slate-400 flex items-start gap-1">
                      <Activity className="w-3 h-3 text-cyan-500 shrink-0 mt-0.5" />
                      {r}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
