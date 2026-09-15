import React from "react";
import {
  Anchor,
  Clock,
  Layers,
  Ship,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  ArrowUpRight,
} from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Top Banner / System Advisory */}
      <div className="ops-panel rounded-xl p-4 border border-cyan-900/40 bg-gradient-to-r from-cyan-950/30 via-slate-900/40 to-slate-900/40 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start md:items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/50 shrink-0">
            <Anchor className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white tracking-wide">
              Harbor Operations Console — Active Monitoring Window
            </h2>
            <p className="text-xs text-slate-400">
              Real-time synthesized status of berths, quay cranes, and scheduled arrivals.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-cyan-950/80 text-cyan-400 border border-cyan-700/50">
            PHASE 0 FOUNDATION
          </span>
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-amber-950/60 text-amber-300 border border-amber-700/50">
            SYNTHETIC DATASET
          </span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">BERTH UTILIZATION</span>
            <span className="p-1.5 rounded-md bg-emerald-950/50 text-emerald-400 border border-emerald-800/40">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">68.4%</span>
            <span className="text-xs font-mono text-emerald-400">NORMAL</span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: "68%" }}></div>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">5 of 7 Berths Occupied</div>
        </div>

        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">ACTIVE VESSEL QUEUE</span>
            <span className="p-1.5 rounded-md bg-cyan-950/50 text-cyan-400 border border-cyan-800/40">
              <Ship className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">12</span>
            <span className="text-xs font-mono text-cyan-400">INBOUND</span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: "45%" }}></div>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">4 approaching anchorage</div>
        </div>

        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">YARD STORAGE OCCUPANCY</span>
            <span className="p-1.5 rounded-md bg-amber-950/50 text-amber-400 border border-amber-800/40">
              <Layers className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">74.2%</span>
            <span className="text-xs font-mono text-amber-400">ELEVATED</span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: "74%" }}></div>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">Zone B near threshold</div>
        </div>

        <div className="ops-panel ops-panel-hover rounded-xl p-5 border border-harbor-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">AVG WAITING TIME</span>
            <span className="p-1.5 rounded-md bg-blue-950/50 text-blue-400 border border-blue-800/40">
              <Clock className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">2.4h</span>
            <span className="text-xs font-mono text-cyan-400">-18% OPT</span>
          </div>
          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: "55%" }}></div>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">Benchmark vs unoptimized: 4.1h</div>
        </div>
      </div>

      {/* Main Operations Matrix Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Vessel Tracking & Berth Overview */}
        <div className="lg:col-span-2 space-y-6">
          <div className="ops-panel rounded-xl p-5 border border-harbor-border">
            <div className="flex items-center justify-between mb-4 border-b border-harbor-border pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                  <Ship className="w-4 h-4 text-cyan-400" />
                  Scheduled Vessel Movements (72-Hour Horizon)
                </h3>
                <p className="text-xs text-slate-400">
                  Priority sequencing and arrival forecasts.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-500">SYNTHETIC QUEUE</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-800 font-mono text-[11px]">
                    <th className="pb-2">VESSEL NAME</th>
                    <th className="pb-2">TYPE</th>
                    <th className="pb-2">DRAFT / LEN</th>
                    <th className="pb-2">ASSIGNED BERTH</th>
                    <th className="pb-2">ETA (EST)</th>
                    <th className="pb-2">STATUS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                  <tr className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-white">MV Ocean Voyager</td>
                    <td className="py-2.5 text-slate-400">Container</td>
                    <td className="py-2.5">14.2m / 320m</td>
                    <td className="py-2.5 text-cyan-400">Berth B-02</td>
                    <td className="py-2.5">T+02:30</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40 text-[10px]">
                        ON TIME
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-white">CMA CGM Polaris</td>
                    <td className="py-2.5 text-slate-400">Container</td>
                    <td className="py-2.5">15.5m / 366m</td>
                    <td className="py-2.5 text-cyan-400">Berth B-01</td>
                    <td className="py-2.5">T+05:45</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/40 text-[10px]">
                        DELAY +45M
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-white">Nordic Stream</td>
                    <td className="py-2.5 text-slate-400">Bulk Carrier</td>
                    <td className="py-2.5">11.8m / 225m</td>
                    <td className="py-2.5 text-cyan-400">Berth B-04</td>
                    <td className="py-2.5">T+09:10</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/40 text-[10px]">
                        APPROACHING
                      </span>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-semibold text-white">Ever Sentinel</td>
                    <td className="py-2.5 text-slate-400">Ultra-Large</td>
                    <td className="py-2.5">16.0m / 400m</td>
                    <td className="py-2.5 text-cyan-400">Berth B-01</td>
                    <td className="py-2.5">T+14:00</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                        QUEUED
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Col: Operations Advisory & Engine Status */}
        <div className="space-y-6">
          <div className="ops-panel rounded-xl p-5 border border-harbor-border">
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 mb-3">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Engine Architecture Status
            </h3>
            <div className="space-y-3 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-400">ML Prediction Engine</span>
                <span className="text-cyan-400">Phase 4 Target</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-400">OR-Tools Optimizer</span>
                <span className="text-cyan-400">Phase 5 Target</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-400">Simulation Engine</span>
                <span className="text-cyan-400">Phase 2 Target</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <span className="text-slate-400">AI Copilot (watsonx/MCP)</span>
                <span className="text-cyan-400">Phase 9 Target</span>
              </div>
            </div>
          </div>

          <div className="ops-panel rounded-xl p-5 border border-amber-900/40 bg-amber-950/10">
            <h4 className="text-xs font-semibold text-amber-400 flex items-center gap-2 mb-2 font-mono">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              OPERATIONAL DIRECTIVE
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              All port operational decisions are governed by mathematical optimization (Google OR-Tools).
              The AI copilot provides natural language interpretation and explanations without computing mathematical schedules directly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
