import React from "react";
import { Bot, Send, Terminal, Sparkles, AlertCircle } from "lucide-react";

export default function AICopilotPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="ops-panel rounded-xl p-5 border border-harbor-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-950 text-blue-400 border border-blue-800/40">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                Operational AI Copilot (watsonx & Tool-Calling)
              </h2>
              <p className="text-xs text-slate-400">
                &ldquo;How do we interact with and understand the system?&rdquo; — Natural language queries, what-if scenario prompts, and schedule explanations.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
            PHASE 9 PREVIEW
          </span>
        </div>
      </div>

      {/* Chat Terminal Interface Placeholder */}
      <div className="ops-panel rounded-xl border border-harbor-border flex flex-col h-[480px]">
        {/* Chat Log */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto font-mono text-xs">
          {/* System Message */}
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-400 flex items-start gap-2.5">
            <Terminal className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="text-white font-semibold">HarborAI Copilot Agent Initialized.</span>
              <p className="mt-1 text-slate-400">
                Ready to answer questions regarding port congestion forecasts, vessel turnarounds,
                and OR-Tools optimization results. Mathematical decisions are delegated to optimization tools.
              </p>
            </div>
          </div>

          {/* Sample Operator Prompt */}
          <div className="flex justify-end">
            <div className="max-w-md p-3 rounded-lg bg-cyan-950/60 border border-cyan-800/50 text-cyan-200">
              Why was MV Ocean Voyager assigned to Berth B-02 instead of Berth B-01?
            </div>
          </div>

          {/* Sample Copilot Explanation */}
          <div className="flex justify-start">
            <div className="max-w-lg p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 space-y-2">
              <div className="flex items-center gap-1.5 text-cyan-400 font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Tool Explanation: [BerthAssignmentReasoning]</span>
              </div>
              <p className="leading-relaxed">
                MV Ocean Voyager requires a draft of 14.2m and length of 320m. While Berth B-01 could accommodate it,
                B-01 is reserved for CMA CGM Polaris (366m / 15.5m draft) arriving at T+05:45.
                Assigning Voyager to B-02 minimizes total port turnaround time and avoids a 3.5h anchorage delay.
              </p>
            </div>
          </div>
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-harbor-border bg-harbor-panel/60">
          <div className="flex items-center gap-3">
            <input
              type="text"
              readOnly
              placeholder="Ask HarborAI Copilot about congestion, berths, or optimization plans..."
              className="flex-1 bg-slate-900/80 border border-harbor-border rounded-lg px-4 py-2.5 text-xs text-slate-300 font-mono focus:outline-none cursor-not-allowed opacity-80"
            />
            <button
              disabled
              className="px-4 py-2.5 rounded-lg bg-cyan-700 text-white text-xs font-semibold flex items-center gap-2 opacity-50 cursor-not-allowed"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
