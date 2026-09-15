import React from "react";
import { Sliders, Database, Server, Key, ShieldCheck } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                HarborAI Operations & Environment Configuration
              </h2>
              <p className="text-xs text-slate-400">
                Port infrastructure parameters, synthetic dataset controls, and backend API connections.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
            SYSTEM CONFIG
          </span>
        </div>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend Connectivity */}
        <div className="ops-panel rounded-xl p-5 border border-harbor-border space-y-4">
          <div className="flex items-center gap-2 text-white text-sm font-semibold border-b border-harbor-border pb-3">
            <Server className="w-4 h-4 text-cyan-400" />
            <span>FastAPI Backend Services</span>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div>
              <label className="text-slate-400 block mb-1">API Target URL</label>
              <input
                type="text"
                readOnly
                value="http://localhost:8000"
                className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-slate-300"
              />
            </div>
            <div className="flex items-center justify-between text-slate-400 pt-2">
              <span>Health Endpoint:</span>
              <span className="text-cyan-400">/api/health</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Architecture Mode:</span>
              <span className="text-emerald-400">Modular Monolith</span>
            </div>
          </div>
        </div>

        {/* Port Simulator Parameters */}
        <div className="ops-panel rounded-xl p-5 border border-harbor-border space-y-4">
          <div className="flex items-center gap-2 text-white text-sm font-semibold border-b border-harbor-border pb-3">
            <Database className="w-4 h-4 text-amber-400" />
            <span>Synthetic Simulation Parameters</span>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between text-slate-400">
              <span>Deterministic Seed:</span>
              <span className="text-amber-400 font-bold">42</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Planning Horizon:</span>
              <span className="text-slate-200">72 Hours</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Berth Count:</span>
              <span className="text-slate-200">5 Berths (B-01 to B-05)</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Crane Fleet:</span>
              <span className="text-slate-200">6 Quay Cranes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
