import React from "react";
import { Cpu, ArrowRight, CheckCircle2, SplitSquareVertical, Clock } from "lucide-react";

export default function OptimizationPage() {
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
                &ldquo;What should we do?&rdquo; — Constraint satisfaction and MIP solver for berth allocation, crane assignments, and scheduling.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
            PHASE 5 PREVIEW
          </span>
        </div>
      </div>

      {/* Comparison Blueprint: Current vs Optimized */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Unoptimized Baseline */}
        <div className="ops-panel rounded-xl p-5 border border-red-900/30 bg-red-950/10 space-y-4">
          <div className="flex items-center justify-between border-b border-red-900/30 pb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-red-400">
              Baseline (Unoptimized Scenario)
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-red-950 text-red-300 border border-red-800/40">
              FIRST-COME-FIRST-SERVE
            </span>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Average Berth Waiting Time:</span>
              <span className="text-red-400 font-bold">4.1 hours</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Total Port Demurrage Cost:</span>
              <span className="text-red-400 font-bold">$42,500</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Crane Idle Time:</span>
              <span className="text-red-400 font-bold">22.4%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Berth Schedule Conflicts:</span>
              <span className="text-red-400 font-bold">3 detected</span>
            </div>
          </div>
        </div>

        {/* Optimized Solution */}
        <div className="ops-panel rounded-xl p-5 border border-emerald-900/30 bg-emerald-950/10 space-y-4">
          <div className="flex items-center justify-between border-b border-emerald-900/30 pb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-emerald-400">
              Optimized Solution (OR-Tools CP-SAT)
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800/40">
              OPTIMAL
            </span>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Average Berth Waiting Time:</span>
              <span className="text-emerald-400 font-bold">2.4 hours (-41%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Total Port Demurrage Cost:</span>
              <span className="text-emerald-400 font-bold">$18,200 (-57%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Crane Idle Time:</span>
              <span className="text-emerald-400 font-bold">9.1% (-59%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Berth Schedule Conflicts:</span>
              <span className="text-emerald-400 font-bold">0 resolved</span>
            </div>
          </div>
        </div>
      </div>

      {/* Constraints Spec Notice */}
      <div className="ops-panel rounded-xl p-6 border border-harbor-border space-y-3">
        <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          Hard Operational Constraints Enforced
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          The solver enforces strict non-overlapping berth occupancy, vessel length and draft compatibility,
          crane capacity, and yard proximity constraints without human scheduling errors.
        </p>
      </div>
    </div>
  );
}
