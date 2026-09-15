import React from "react";
import { TrendingUp, AlertCircle, BarChart3, Clock, HelpCircle } from "lucide-react";

export default function PredictionsPage() {
  return (
    <div className="space-y-6">
      {/* Header advisory */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800/40">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                Machine Learning Congestion & Turnaround Predictor
              </h2>
              <p className="text-xs text-slate-400">
                &ldquo;What is likely to happen?&rdquo; — XGBoost Tabular ETA variance & congestion risk modeling.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
            PHASE 4 PREVIEW
          </span>
        </div>
      </div>

      {/* Grid of ML forecast placeholders */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="ops-panel rounded-xl p-5 border border-harbor-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Predicted Congestion Risk
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-400 border border-amber-800/40">
              MEDIUM RISK
            </span>
          </div>
          <div className="text-3xl font-mono font-bold text-white">42%</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Peak congestion predicted between T+18h and T+24h at Quay Sector North due to overlapping arrivals.
          </p>
          <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-500">
            <span>Model: XGBoost-v1</span>
            <span>Target: T+72h</span>
          </div>
        </div>

        <div className="ops-panel rounded-xl p-5 border border-harbor-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
              ETA Variance Uncertainty
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800/40">
              ± 45 MIN
            </span>
          </div>
          <div className="text-3xl font-mono font-bold text-white">92.8%</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Confidence interval across 12 scheduled arrivals based on simulated maritime channel speed factors.
          </p>
          <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-500">
            <span>Features: 14 tabular</span>
            <span>Seed: 42</span>
          </div>
        </div>

        <div className="ops-panel rounded-xl p-5 border border-harbor-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Yard Storage Saturation
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800/40">
              STABLE
            </span>
          </div>
          <div className="text-3xl font-mono font-bold text-white">78.0% MAX</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Yard Zone B peak utilization expected to peak below maximum safety ceiling (85%).
          </p>
          <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-500">
            <span>Threshold: 85%</span>
            <span>Alerts: 0 critical</span>
          </div>
        </div>
      </div>

      {/* Feature explanation card */}
      <div className="ops-panel rounded-xl p-6 border border-harbor-border space-y-3">
        <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-cyan-400" />
          Feature Importance & Explainability Blueprint
        </h3>
        <p className="text-xs text-slate-400">
          In Phase 4, HarborAI will integrate XGBoost tabular predictors with JSON explanation metadata
          (top influencing features, baseline metrics, confidence intervals).
        </p>
      </div>
    </div>
  );
}
