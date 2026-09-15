"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  Anchor,
  Clock,
  Layers,
  Ship,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  RefreshCw,
  Play,
  RotateCcw,
  FastForward,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface KPIs {
  total_vessels: number;
  active_vessels: number;
  waiting_vessels: number;
  vessels_at_berth: number;
  completed_vessels: number;
  queue_length: number;
  occupied_berths: number;
  available_berths: number;
  berth_utilization: number;
  total_cranes: number;
  active_cranes: number;
  available_cranes: number;
  crane_utilization: number;
  total_yard_capacity: number;
  total_yard_occupancy: number;
  yard_utilization: number;
  throughput_teu: number;
  average_waiting_time_h: number;
  average_handling_time_h: number;
  congestion_score: number;
  congestion_risk: string;
}

interface VesselItem {
  id: string;
  name: string;
  status: string;
  assigned_berth_id: string | null;
  length_m: number;
  draft_m: number;
  containers_to_handle: number | null;
  expected_handling_duration_h: number | null;
  waiting_hours: number;
}

interface SimState {
  simulation_time: string;
  is_running: boolean;
  elapsed_hours: number;
  total_steps: number;
  vessels: VesselItem[];
  kpis: KPIs;
}

function riskColor(risk: string) {
  switch (risk?.toLowerCase()) {
    case "critical": return "text-red-400";
    case "high": return "text-orange-400";
    case "medium": return "text-amber-400";
    default: return "text-emerald-400";
  }
}

function riskBg(risk: string) {
  switch (risk?.toLowerCase()) {
    case "critical": return "bg-red-950 text-red-400 border-red-800/40";
    case "high": return "bg-orange-950 text-orange-400 border-orange-800/40";
    case "medium": return "bg-amber-950 text-amber-400 border-amber-800/40";
    default: return "bg-emerald-950 text-emerald-400 border-emerald-800/40";
  }
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    at_sea: "bg-slate-800 text-slate-400",
    approaching: "bg-blue-950 text-blue-400 border-blue-800/40",
    waiting: "bg-amber-950 text-amber-400 border-amber-800/40",
    berth_assigned: "bg-cyan-950 text-cyan-400 border-cyan-800/40",
    entering_berth: "bg-cyan-950 text-cyan-400 border-cyan-800/40",
    at_berth: "bg-emerald-950 text-emerald-400 border-emerald-800/40",
    crane_operations: "bg-emerald-950 text-emerald-400 border-emerald-800/40",
    departing: "bg-purple-950 text-purple-400 border-purple-800/40",
    left_port: "bg-slate-800 text-slate-500",
  };
  return map[status] || "bg-slate-800 text-slate-400";
}

export default function DashboardPage() {
  const [state, setState] = useState<SimState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [advancing, setAdvancing] = useState(false);

  const fetchState = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/simulation/state`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setState(data);
      setError(null);
    } catch (e: any) {
      setError(e.message || "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 5000);
    return () => clearInterval(interval);
  }, [fetchState]);

  const handleAdvance = async (hours: number) => {
    setAdvancing(true);
    try {
      await fetch(`${API}/api/simulation/advance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hours }),
      });
      await fetchState();
    } catch {}
    setAdvancing(false);
  };

  const handleReset = async () => {
    try {
      await fetch(`${API}/api/simulation/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seed: 42 }),
      });
      await fetchState();
    } catch {}
  };

  const kpis = state?.kpis;
  const vessels = state?.vessels || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="ops-panel rounded-xl p-6 border border-red-900/40 bg-red-950/20">
        <div className="flex items-center gap-3 text-red-400">
          <AlertTriangle className="w-5 h-5" />
          <div>
            <h3 className="font-semibold">Backend Connection Error</h3>
            <p className="text-xs mt-1 text-slate-400">Cannot reach {API}. Ensure the backend is running.</p>
            <p className="text-xs text-red-300 mt-1">{error}</p>
          </div>
        </div>
        <button onClick={fetchState} className="mt-3 px-3 py-1.5 rounded bg-slate-800 text-xs text-slate-300 hover:bg-slate-700">
          <RefreshCw className="w-3 h-3 inline mr-1" /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="ops-panel rounded-xl p-4 border border-cyan-900/40 bg-gradient-to-r from-cyan-950/30 via-slate-900/40 to-slate-900/40 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start md:items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/50 shrink-0">
            <Anchor className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white tracking-wide">
              Harbor Operations Console — Live Monitoring
            </h2>
            <p className="text-xs text-slate-400">
              Simulation Time: <span className="text-cyan-400 font-mono">{state?.simulation_time ? new Date(state.simulation_time).toLocaleString() : "—"}</span>
              {" | "}Elapsed: <span className="text-cyan-400 font-mono">{state?.elapsed_hours?.toFixed(1) || 0}h</span>
              {" | "}Steps: <span className="text-cyan-400 font-mono">{state?.total_steps || 0}</span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleReset} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Reset Simulation">
            <RotateCcw className="w-4 h-4" />
          </button>
          <button onClick={() => handleAdvance(1)} disabled={advancing} className="px-3 py-1.5 rounded bg-cyan-700 hover:bg-cyan-600 text-white font-mono text-xs flex items-center gap-1.5 disabled:opacity-50" title="Advance 1h">
            <Play className="w-3 h-3 fill-current" /> +1h
          </button>
          <button onClick={() => handleAdvance(6)} disabled={advancing} className="px-3 py-1.5 rounded bg-cyan-800 hover:bg-cyan-700 text-white font-mono text-xs flex items-center gap-1.5 disabled:opacity-50" title="Advance 6h">
            <FastForward className="w-3 h-3" /> +6h
          </button>
          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${riskBg(kpis?.congestion_risk || "low")}`}>
            {(kpis?.congestion_risk || "LOW").toUpperCase()}
          </span>
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-amber-950/60 text-amber-300 border border-amber-700/50">
            SYNTHETIC
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Berth Utilization */}
        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">BERTH UTILIZATION</span>
            <span className="p-1.5 rounded-md bg-emerald-950/50 text-emerald-400 border border-emerald-800/40">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{((kpis?.berth_utilization || 0) * 100).toFixed(0)}%</span>
            <span className={`text-xs font-mono ${riskColor(kpis?.berth_utilization && kpis.berth_utilization > 0.8 ? "high" : "low")}`}>
              {kpis?.berth_utilization && kpis.berth_utilization > 0.8 ? "HIGH" : "NORMAL"}
            </span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${(kpis?.berth_utilization || 0) * 100}%` }} />
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">
            {kpis?.occupied_berths || 0} of {(kpis?.occupied_berths || 0) + (kpis?.available_berths || 0)} Berths Occupied
          </div>
        </div>

        {/* Active Vessels */}
        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">ACTIVE VESSELS</span>
            <span className="p-1.5 rounded-md bg-cyan-950/50 text-cyan-400 border border-cyan-800/40">
              <Ship className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{kpis?.active_vessels || 0}</span>
            <span className="text-xs font-mono text-cyan-400">/ {kpis?.total_vessels || 0} TOTAL</span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-cyan-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${kpis?.total_vessels ? ((kpis?.active_vessels || 0) / kpis.total_vessels * 100) : 0}%` }} />
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">
            {kpis?.waiting_vessels || 0} waiting | {kpis?.vessels_at_berth || 0} at berth
          </div>
        </div>

        {/* Yard Utilization */}
        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">YARD UTILIZATION</span>
            <span className="p-1.5 rounded-md bg-amber-950/50 text-amber-400 border border-amber-800/40">
              <Layers className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{((kpis?.yard_utilization || 0) * 100).toFixed(1)}%</span>
            <span className={`text-xs font-mono ${kpis?.yard_utilization && kpis.yard_utilization > 0.8 ? "text-amber-400" : "text-emerald-400"}`}>
              {kpis?.yard_utilization && kpis.yard_utilization > 0.8 ? "ELEVATED" : "NORMAL"}
            </span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-amber-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${(kpis?.yard_utilization || 0) * 100}%` }} />
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">
            {kpis?.total_yard_occupancy?.toLocaleString() || 0} / {kpis?.total_yard_capacity?.toLocaleString() || 0} TEU
          </div>
        </div>

        {/* Congestion Score */}
        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">CONGESTION SCORE</span>
            <span className="p-1.5 rounded-md bg-blue-950/50 text-blue-400 border border-blue-800/40">
              <Cpu className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{((kpis?.congestion_score || 0) * 100).toFixed(0)}</span>
            <span className={`text-xs font-mono ${riskColor(kpis?.congestion_risk || "low")}`}>
              {(kpis?.congestion_risk || "LOW").toUpperCase()}
            </span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className={`h-1.5 rounded-full transition-all duration-500 ${kpis?.congestion_score && kpis.congestion_score > 0.6 ? "bg-orange-500" : "bg-blue-500"}`} style={{ width: `${(kpis?.congestion_score || 0) * 100}%` }} />
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">
            Cranes: {((kpis?.crane_utilization || 0) * 100).toFixed(0)}% util | Queue: {kpis?.queue_length || 0}
          </div>
        </div>
      </div>

      {/* Vessel Table */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between mb-4 border-b border-harbor-border pb-3">
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <Ship className="w-4 h-4 text-cyan-400" />
              Vessel Fleet Status
            </h3>
            <p className="text-xs text-slate-400">Live vessel tracking from simulation engine</p>
          </div>
          <button onClick={fetchState} className="text-xs font-mono text-slate-500 hover:text-cyan-400 flex items-center gap-1">
            <RefreshCw className="w-3 h-3" /> REFRESH
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800 font-mono text-[11px]">
                <th className="pb-2">VESSEL NAME</th>
                <th className="pb-2">DRAFT / LEN</th>
                <th className="pb-2">CONTAINERS</th>
                <th className="pb-2">WAIT (H)</th>
                <th className="pb-2">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {vessels.map((v) => (
                <tr key={v.id} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-semibold text-white">{v.name}</td>
                  <td className="py-2.5">{v.draft_m}m / {v.length_m}m</td>
                  <td className="py-2.5">{v.containers_to_handle?.toLocaleString() || "—"}</td>
                  <td className="py-2.5">{v.waiting_hours > 0 ? v.waiting_hours.toFixed(1) : "—"}</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 rounded border text-[10px] ${statusBadge(v.status)}`}>
                      {v.status.toUpperCase().replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
