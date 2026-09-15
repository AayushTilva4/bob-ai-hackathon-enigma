"use client";

import React, { useEffect } from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("HarborAI Frontend Operational Error:", error);
  }, [error]);

  return (
    <div className="ops-panel rounded-xl p-8 border border-red-900/50 bg-red-950/20 text-center max-w-lg mx-auto my-12 space-y-4">
      <div className="w-12 h-12 rounded-full bg-red-900/40 border border-red-700/50 flex items-center justify-center mx-auto text-red-400">
        <AlertOctagon className="w-6 h-6" />
      </div>
      <h2 className="text-base font-semibold text-white">Operations Display Telemetry Error</h2>
      <p className="text-xs text-slate-400 font-mono">
        {error.message || "An unexpected error occurred in the operations display module."}
      </p>
      <button
        onClick={() => reset()}
        className="px-4 py-2 rounded-lg bg-red-800 hover:bg-red-700 text-white text-xs font-mono font-medium flex items-center gap-2 mx-auto transition-colors"
      >
        <RotateCcw className="w-3.5 h-3.5" />
        <span>RETRY SUBSYSTEM</span>
      </button>
    </div>
  );
}
