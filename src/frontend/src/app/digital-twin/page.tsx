import React from "react";
import { Anchor, Navigation, Eye, Play, FastForward, RotateCcw } from "lucide-react";

export default function DigitalTwinPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800/40">
              <Anchor className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                Port Digital Twin & Simulation Workspace
              </h2>
              <p className="text-xs text-slate-400">
                &ldquo;What happens if we do it?&rdquo; — 2D Port layout, berth occupation, vessel channel navigation, and what-if scenarios.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
            PHASE 7/8 PREVIEW
          </span>
        </div>
      </div>

      {/* Interactive simulation viewport placeholder */}
      <div className="ops-panel rounded-xl p-6 border border-harbor-border h-[420px] flex flex-col items-center justify-center relative overflow-hidden bg-slate-950/80">
        <div className="absolute inset-0 bg-[radial-gradient(#1e2d4d_1px,transparent_1px)] [background-size:16px_16px] opacity-40"></div>
        
        {/* Radar/Port grid rings visual effect */}
        <div className="w-80 h-80 rounded-full border border-cyan-900/30 absolute flex items-center justify-center pointer-events-none">
          <div className="w-56 h-56 rounded-full border border-cyan-800/20 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full border border-cyan-700/20"></div>
          </div>
        </div>

        <div className="z-10 text-center space-y-3 max-w-md">
          <div className="inline-flex p-3 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-700/50 shadow-lg shadow-cyan-950/50">
            <Navigation className="w-8 h-8 text-cyan-400" />
          </div>
          <h3 className="text-base font-semibold text-white">MapLibre GL Port Digital Twin</h3>
          <p className="text-xs text-slate-400 leading-relaxed font-mono">
            Client-side route interpolation viewport. Renders berths B-01 through B-05, navigation channels (North/South),
            and vessel movements from scheduled timestamps without WebSockets.
          </p>
        </div>

        {/* Playback controls placeholder */}
        <div className="absolute bottom-4 z-10 flex items-center gap-3 bg-slate-900/90 border border-slate-800 px-4 py-2 rounded-lg backdrop-blur">
          <button className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Reset">
            <RotateCcw className="w-4 h-4" />
          </button>
          <button className="px-3 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs flex items-center gap-1.5" title="Play Simulation">
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>PLAY T+00:00</span>
          </button>
          <button className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Fast Forward">
            <FastForward className="w-4 h-4" />
          </button>
          <span className="text-[11px] font-mono text-slate-500 border-l border-slate-800 pl-3">SPEED: 1x</span>
        </div>
      </div>
    </div>
  );
}
