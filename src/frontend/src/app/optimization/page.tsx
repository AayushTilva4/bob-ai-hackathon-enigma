"use client";

import React, { useState } from "react";
import {
  Cpu,
  CheckCircle2,
  Play,
  Loader2,
  ArrowRight,
  ArrowDown,
  AlertTriangle,
  Zap,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Assignment {
  vessel_id: string;
  vessel_name: string;
  berth_id: string | null;
  berth_name: string | null;
  planned_start_h: number | null;
  planned_end_h: number | null;
  waiting_time_h: number | null;
  handling_duration_h: number | null;
  reason: string | null;
}

interface OptResult {
  solver_status: string;
  solve_time_ms: number;
  objective_value: number;
  assignments: Assignment[];
  total_waiting_time_h: number;
  average_waiting_time_h: number;
  max_delay_h: number;
  explanation: string[];
}

interface Comparison {
  baseline: Record<string, number>;
  optimized: Record<string, number>;
  improvements: Record<string, number>;
  explanation: string[];
}

function pctBadge(value: number) {
  if (value < 0)
    return (
      <span className="text-emerald-400 font-bold">{value.toFixed(1)}%</span>
    );
  if (value > 0)
    return (
      <span className="text-red-400 font-bold">+{value.toFixed(1)}%</span>
    );
  return <span className="text-slate-400">0%</span>;
}

export default function OptimizationPage() {
  const [result, setResult] = useState<OptResult | null>(null);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runOptimization = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/optimization/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ time_limit_seconds: 10 }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: OptResult = await res.json();
      setResult(data);

      // Auto-run comparison
      const cmpRes = await fetch(`${API}/api/optimization/compare`, {
        method: "POST",
      });
      if (cmpRes.ok) {
        const cmpData: Comparison = await cmpRes.json();
        setComparison(cmpData);
      }
    } catch (e: any) {
      setError(e.message || "Optimization failed");
    }
    setRunning(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/40">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                OR-Tools Mathematical Optimization Engine
              </h2>
              <p className="text-xs text-slate-400">
                Constraint satisfaction solver for berth allocation, crane assignments, and scheduling.
              </p>
            </div>
          </div>
          <button
            onClick={runOptimization}
            disabled={running}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-2 disabled:opacity-50 transition-colors"
          >
            {running ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Solving...</>
            ) : (
              <><Zap className="w-4 h-4" /> Run Optimization</>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="ops-panel rounded-xl p-4 border border-red-900/40 bg-red-950/20 flex items-center gap-3 text-red-400 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Solver Result */}
      {result && (
        <div className="ops-panel rounded-xl p-5 border border-harbor-border space-y-4">
          <div className="flex items-center justify-between border-b border-harbor-border pb-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 className={`w-4 h-4 ${result.solver_status === "OPTIMAL" ? "text-emerald-400" : "text-amber-400"}`} />
              <span className="text-sm font-semibold text-white">
                Solver: {result.solver_status}
              </span>
            </div>
            <span className="text-xs font-mono text-slate-500">
              {result.solve_time_ms.toFixed(1)}ms
            </span>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center font-mono text-xs">
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="text-slate-400 mb-1">Total Wait</div>
              <div className="text-lg font-bold text-white">{result.total_waiting_time_h.toFixed(1)}h</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="text-slate-400 mb-1">Avg Wait</div>
              <div className="text-lg font-bold text-white">{result.average_waiting_time_h.toFixed(1)}h</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="text-slate-400 mb-1">Max Delay</div>
              <div className="text-lg font-bold text-white">{result.max_delay_h.toFixed(1)}h</div>
            </div>
          </div>

          {result.explanation.map((e, i) => (
            <div key={i} className="text-xs text-slate-400 font-mono">{e}</div>
          ))}
        </div>
      )}

      {/* Comparison */}
      {comparison && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="ops-panel rounded-xl p-5 border border-red-900/30 bg-red-950/10 space-y-4">
            <div className="flex items-center justify-between border-b border-red-900/30 pb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-red-400">
                Baseline (Current Schedule)
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950 text-red-300 border border-red-800/40">
                FCFS
              </span>
            </div>
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between"><span className="text-slate-400">Total Waiting Time:</span><span className="text-red-400 font-bold">{comparison.baseline.total_waiting_time_h?.toFixed(1)}h</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Average Wait:</span><span className="text-red-400 font-bold">{comparison.baseline.average_waiting_time_h?.toFixed(1)}h</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Max Delay:</span><span className="text-red-400 font-bold">{comparison.baseline.max_delay_h?.toFixed(1)}h</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Schedule Conflicts:</span><span className="text-red-400 font-bold">{comparison.baseline.conflicts || 0}</span></div>
            </div>
          </div>

          <div className="ops-panel rounded-xl p-5 border border-emerald-900/30 bg-emerald-950/10 space-y-4">
            <div className="flex items-center justify-between border-b border-emerald-900/30 pb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-emerald-400">
                Optimized (OR-Tools CP-SAT)
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800/40">
                {result?.solver_status || "OPTIMAL"}
              </span>
            </div>
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between"><span className="text-slate-400">Total Waiting Time:</span><span className="text-emerald-400 font-bold">{comparison.optimized.total_waiting_time_h?.toFixed(1)}h ({pctBadge(comparison.improvements.waiting_time_reduction_pct)})</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Average Wait:</span><span className="text-emerald-400 font-bold">{comparison.optimized.average_waiting_time_h?.toFixed(1)}h ({pctBadge(comparison.improvements.avg_waiting_reduction_pct)})</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Max Delay:</span><span className="text-emerald-400 font-bold">{comparison.optimized.max_delay_h?.toFixed(1)}h</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Conflicts Resolved:</span><span className="text-emerald-400 font-bold">{comparison.improvements.conflicts_resolved || 0}</span></div>
            </div>
          </div>
        </div>
      )}

      {/* Assignments Table */}
      {result && result.assignments.length > 0 && (
        <div className="ops-panel rounded-xl p-5 border border-harbor-border">
          <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 mb-4 border-b border-harbor-border pb-3">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            Optimized Assignments
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-800 font-mono text-[11px]">
                  <th className="pb-2">VESSEL</th>
                  <th className="pb-2">BERTH</th>
                  <th className="pb-2">START</th>
                  <th className="pb-2">END</th>
                  <th className="pb-2">WAIT</th>
                  <th className="pb-2">REASON</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                {result.assignments.map((a, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="py-2 font-semibold text-white">{a.vessel_name}</td>
                    <td className="py-2 text-cyan-400">{a.berth_name || "—"}</td>
                    <td className="py-2">T+{a.planned_start_h?.toFixed(0) || "—"}h</td>
                    <td className="py-2">T+{a.planned_end_h?.toFixed(0) || "—"}h</td>
                    <td className="py-2">{a.waiting_time_h != null ? `${a.waiting_time_h.toFixed(1)}h` : "—"}</td>
                    <td className="py-2 text-slate-500 text-[10px] max-w-[200px] truncate" title={a.reason || ""}>{a.reason || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Call to action if not run yet */}
      {!result && !running && (
        <div className="ops-panel rounded-xl p-8 border border-harbor-border flex flex-col items-center justify-center space-y-4 text-center">
          <div className="p-4 rounded-xl bg-cyan-950/50 text-cyan-400 border border-cyan-800/40">
            <Cpu className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-white">Run Optimization to See Results</h3>
          <p className="text-xs text-slate-400 max-w-md">
            Click &quot;Run Optimization&quot; to execute the OR-Tools CP-SAT solver. It will compute optimal berth assignments,
            minimize waiting times, and produce a side-by-side comparison against the current FCFS schedule.
          </p>
        </div>
      )}
    </div>
  );
}
