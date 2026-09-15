"use client";

import React, { useState, useRef, useEffect } from "react";
import { Bot, Send, Terminal, Sparkles, AlertCircle, Loader2 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
  tool_calls?: { tool: string; params: Record<string, string> }[];
  timestamp: Date;
}

const SUGGESTED_QUERIES = [
  "What is the current port status?",
  "Show me the congestion forecast",
  "What berths are available?",
  "How many cranes are active?",
  "Give me an operations brief",
  "Where is MV Northern Light?",
  "What vessels are waiting?",
];

export default function AICopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "system",
      content: "**HarborAI Copilot Agent Initialized.** Ready to answer questions about port congestion, vessel status, berth assignments, and optimization results. All responses are grounded in real-time system data via tool calling.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (msg?: string) => {
    const text = msg || input.trim();
    if (!text) return;

    const userMsg: ChatMessage = { role: "user", content: text, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/api/copilot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: data.reply,
        tool_calls: data.tool_calls,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      const errMsg: ChatMessage = {
        role: "assistant",
        content: `**Connection Error:** ${e.message}. Ensure the backend is running at ${API}.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    }

    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

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
                Operational AI Copilot (Tool-Calling Agent)
              </h2>
              <p className="text-xs text-slate-400">
                Natural language queries grounded in real-time system data. Ask about vessels, berths, congestion, or get an operations brief.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-700/40">
            ACTIVE
          </span>
        </div>
      </div>

      {/* Suggested Queries */}
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUERIES.map((q, i) => (
          <button
            key={i}
            onClick={() => sendMessage(q)}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-400 hover:text-cyan-400 hover:border-cyan-800/50 transition-colors disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Interface */}
      <div className="ops-panel rounded-xl border border-harbor-border flex flex-col h-[520px]">
        {/* Chat Log */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto">
          {messages.map((msg, i) => {
            if (msg.role === "system") {
              return (
                <div key={i} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-400 flex items-start gap-2.5 text-xs font-mono">
                  <Terminal className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div dangerouslySetInnerHTML={{ __html: msg.content.replace(/\*\*(.*?)\*\*/g, '<span class="text-white font-semibold">$1</span>') }} />
                </div>
              );
            }

            if (msg.role === "user") {
              return (
                <div key={i} className="flex justify-end">
                  <div className="max-w-md p-3 rounded-lg bg-cyan-950/60 border border-cyan-800/50 text-cyan-200 text-xs font-mono">
                    {msg.content}
                  </div>
                </div>
              );
            }

            return (
              <div key={i} className="flex justify-start">
                <div className="max-w-2xl p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 space-y-2 text-xs font-mono">
                  {msg.tool_calls && msg.tool_calls.length > 0 && (
                    <div className="flex items-center gap-1.5 text-cyan-400 font-semibold text-[10px]">
                      <Sparkles className="w-3 h-3" />
                      <span>Tool: [{msg.tool_calls[0].tool}]</span>
                    </div>
                  )}
                  <div className="leading-relaxed whitespace-pre-wrap" dangerouslySetInnerHTML={{
                    __html: msg.content
                      .replace(/\*\*(.*?)\*\*/g, '<span class="text-white font-semibold">$1</span>')
                      .replace(/\n/g, '<br />')
                  }} />
                </div>
              </div>
            );
          })}
          {loading && (
            <div className="flex justify-start">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 text-xs font-mono flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <span>Querying system tools...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-harbor-border bg-harbor-panel/60">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask HarborAI Copilot about congestion, berths, or optimization plans..."
              className="flex-1 bg-slate-900/80 border border-harbor-border rounded-lg px-4 py-2.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-700 transition-colors"
              disabled={loading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="px-4 py-2.5 rounded-lg bg-cyan-700 hover:bg-cyan-600 text-white text-xs font-semibold flex items-center gap-2 disabled:opacity-50 transition-colors"
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
