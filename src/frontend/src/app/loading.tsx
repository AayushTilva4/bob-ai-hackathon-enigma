import React from "react";
import { Compass } from "lucide-react";

export default function Loading() {
  return (
    <div className="h-64 flex flex-col items-center justify-center space-y-3">
      <Compass className="w-8 h-8 text-cyan-400 animate-spin" />
      <span className="text-xs font-mono text-slate-400 tracking-wider">
        SYNCHRONIZING HARBOR OPERATIONS TELEMETRY...
      </span>
    </div>
  );
}
