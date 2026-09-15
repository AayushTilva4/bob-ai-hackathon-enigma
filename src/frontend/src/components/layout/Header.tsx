"use client";

import React, { useEffect, useState } from "react";
import { Activity, Database, ShieldAlert, User, Terminal } from "lucide-react";
import { usePathname } from "next/navigation";

const routeTitles: Record<string, string> = {
  "/dashboard": "Operations Overview",
  "/predictions": "Congestion & ETA Predictions",
  "/optimization": "Resource & Berth Optimizer",
  "/digital-twin": "Port Digital Twin Simulation",
  "/ai-copilot": "Operational AI Copilot",
  "/settings": "System & Port Parameters",
};

export default function Header() {
  const pathname = usePathname();
  const [utcTime, setUtcTime] = useState<string>("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().replace("GMT", "UTC"));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const pageTitle = routeTitles[pathname] || "Port Operations Center";

  return (
    <header className="h-16 border-b border-harbor-border bg-harbor-panel/90 backdrop-blur-md px-6 flex items-center justify-between z-10 sticky top-0">
      <div className="flex items-center space-x-4">
        <div>
          <h1 className="text-lg font-semibold text-harbor-text tracking-wide flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-harbor-cyan animate-pulse"></span>
            {pageTitle}
          </h1>
          <p className="text-xs text-harbor-muted font-mono">PORT ID: IN-BOM-01 // SECTOR NORTH</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Synthetic Data Badge */}
        <div className="ops-badge-synthetic px-3 py-1 rounded text-xs font-mono font-semibold flex items-center gap-1.5 shadow-sm">
          <Database className="w-3.5 h-3.5 text-amber-400" />
          <span>SYNTHETIC DATA</span>
        </div>

        {/* System Status */}
        <div className="hidden sm:flex items-center space-x-2 bg-emerald-950/30 border border-emerald-500/30 px-3 py-1 rounded text-xs font-mono text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>SYSTEM OPERATIONAL</span>
        </div>

        {/* Operations Clock */}
        <div className="hidden lg:flex items-center text-xs font-mono text-harbor-muted bg-harbor-card px-3 py-1 rounded border border-harbor-border">
          <Activity className="w-3.5 h-3.5 text-harbor-cyan mr-1.5" />
          <span>{utcTime || "UTC TIME SYNC..."}</span>
        </div>

        {/* User / Operator Badge */}
        <div className="flex items-center space-x-2 border-l border-harbor-border pl-4">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-harbor-border flex items-center justify-center text-harbor-cyan">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-medium text-slate-200">Enigma Ops</p>
            <p className="text-[10px] text-slate-500 font-mono">OPERATOR #42</p>
          </div>
        </div>
      </div>
    </header>
  );
}
