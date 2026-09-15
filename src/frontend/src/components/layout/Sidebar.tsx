"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  Cpu,
  Anchor,
  Bot,
  Sliders,
  Compass,
  Radio,
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Predictions", href: "/predictions", icon: TrendingUp },
  { name: "Optimization", href: "/optimization", icon: Cpu },
  { name: "Digital Twin", href: "/digital-twin", icon: Anchor },
  { name: "AI Copilot", href: "/ai-copilot", icon: Bot, badge: "AI" },
  { name: "Settings", href: "/settings", icon: Sliders },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-harbor-bg border-r border-harbor-border flex flex-col h-screen shrink-0">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-harbor-border bg-harbor-panel/50">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
          <Compass className="w-5 h-5 text-white animate-spin-slow" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-base tracking-wider text-white">HarborAI</span>
            <span className="text-[10px] font-mono font-semibold bg-cyan-950 text-cyan-400 border border-cyan-800/60 px-1 rounded">
              v0.1
            </span>
          </div>
          <p className="text-[10px] text-harbor-muted font-mono tracking-tight">
            PORT OPS OPTIMIZER
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-widest text-slate-500">
          Operations Control
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                isActive
                  ? "bg-cyan-950/50 text-cyan-300 border border-cyan-700/50 shadow-sm shadow-cyan-950/50"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive
                      ? "text-cyan-400"
                      : "text-slate-500 group-hover:text-slate-300"
                  }`}
                />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700/40">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-harbor-border bg-harbor-panel/40">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="font-mono text-[11px]">Telemetry Feed</span>
          </div>
          <span className="font-mono text-[10px] text-slate-500">OFFLINE-SIM</span>
        </div>
        <div className="mt-2 text-[10px] text-slate-500 font-mono text-center">
          IBM BoB Hackathon 2026 • Team Enigma
        </div>
      </div>
    </aside>
  );
}
