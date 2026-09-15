"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Anchor,
  Navigation,
  Play,
  FastForward,
  RotateCcw,
  Pause,
  Ship,
  MapPin,
  Waves,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface VesselState {
  id: string;
  name: string;
  status: string;
  length_m: number;
  draft_m: number;
  assigned_berth_id: string | null;
  containers_to_handle: number | null;
}

interface BerthState {
  id: string;
  name: string;
  status: string;
  max_vessel_length_m: number;
}

interface SimData {
  simulation_time: string;
  is_running: boolean;
  elapsed_hours: number;
  total_steps: number;
  vessels: VesselState[];
  berths: BerthState[];
  kpis: Record<string, number>;
}

// Port layout constants (simulated 2D positions)
const BERTH_POSITIONS = [
  { id: "10000000-0000-0000-0000-000000000001", name: "Alpha", x: 140, y: 120, w: 120, h: 28 },
  { id: "10000000-0000-0000-0000-000000000002", name: "Bravo", x: 140, y: 160, w: 100, h: 28 },
  { id: "10000000-0000-0000-0000-000000000003", name: "Charlie", x: 140, y: 200, w: 90, h: 28 },
  { id: "10000000-0000-0000-0000-000000000004", name: "Delta", x: 140, y: 240, w: 80, h: 28 },
  { id: "10000000-0000-0000-0000-000000000005", name: "Echo", x: 140, y: 280, w: 130, h: 28 },
];

const CHANNEL_PATHS = [
  { name: "North Channel", points: "M 580,100 C 500,100 420,110 350,120 C 300,128 270,130 260,135", color: "#06b6d4" },
  { name: "South Channel", points: "M 580,300 C 500,290 420,280 350,270 C 300,260 270,255 260,250", color: "#8b5cf6" },
  { name: "Deep-water", points: "M 600,200 C 520,195 440,195 380,200 C 320,205 280,210 260,200", color: "#3b82f6" },
];

function vesselStatusColor(status: string) {
  switch (status) {
    case "crane_operations": return "#10b981";
    case "at_berth":
    case "entering_berth": return "#06b6d4";
    case "approaching": return "#f59e0b";
    case "waiting": return "#ef4444";
    case "at_sea": return "#6366f1";
    case "departing": return "#a855f7";
    default: return "#64748b";
  }
}

function berthStatusColor(status: string) {
  switch (status) {
    case "occupied": return "#10b981";
    case "available": return "#06b6d4";
    case "maintenance": return "#f59e0b";
    default: return "#64748b";
  }
}

// Position vessels based on their status
function getVesselPosition(v: VesselState, index: number) {
  if (v.status === "crane_operations" || v.status === "at_berth" || v.status === "entering_berth") {
    const berth = BERTH_POSITIONS.find((b) => v.assigned_berth_id?.includes(b.id));
    if (berth) return { x: berth.x + berth.w + 15, y: berth.y + 5 };
  }
  if (v.status === "waiting" || v.status === "berth_assigned") {
    return { x: 380 + (index % 3) * 40, y: 140 + Math.floor(index / 3) * 35 };
  }
  if (v.status === "approaching") {
    return { x: 480 + (index % 2) * 50, y: 120 + index * 30 };
  }
  if (v.status === "departing") {
    return { x: 500 + index * 30, y: 180 + index * 20 };
  }
  // at_sea
  return { x: 540 + (index % 3) * 30, y: 80 + index * 28 };
}

export default function DigitalTwinPage() {
  const [data, setData] = useState<SimData | null>(null);
  const [speed, setSpeed] = useState(1);
  const [autoPlay, setAutoPlay] = useState(false);
  const [selectedVessel, setSelectedVessel] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/simulation/state`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    if (!autoPlay) return;
    const interval = setInterval(async () => {
      await fetch(`${API}/api/simulation/advance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hours: speed }),
      });
      await fetchData();
    }, 2000);
    return () => clearInterval(interval);
  }, [autoPlay, speed, fetchData]);

  const handleReset = async () => {
    setAutoPlay(false);
    await fetch(`${API}/api/simulation/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed: 42 }),
    });
    await fetchData();
  };

  const vessels = data?.vessels || [];
  const selectedVesselData = vessels.find((v) => v.id === selectedVessel);

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
                Port Digital Twin &amp; Simulation Workspace
              </h2>
              <p className="text-xs text-slate-400">
                2D Port layout with live vessel positions, berth occupation, and channel navigation.
              </p>
            </div>
          </div>
          <div className="text-right text-xs font-mono text-slate-500">
            <div>T: {data?.simulation_time ? new Date(data.simulation_time).toLocaleTimeString() : "—"}</div>
            <div>Elapsed: {data?.elapsed_hours?.toFixed(1) || 0}h | Steps: {data?.total_steps || 0}</div>
          </div>
        </div>
      </div>

      {/* Port Visualization */}
      <div className="ops-panel rounded-xl border border-harbor-border overflow-hidden relative">
        <svg
          viewBox="0 0 650 380"
          className="w-full h-[420px] bg-slate-950"
          style={{ background: "radial-gradient(ellipse at 70% 50%, #0c1929 0%, #020617 70%)" }}
        >
          {/* Grid */}
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" strokeWidth="0.3" />
            </pattern>
          </defs>
          <rect width="650" height="380" fill="url(#grid)" opacity="0.5" />

          {/* Quay Wall */}
          <rect x="130" y="100" width="6" height="230" fill="#334155" rx="2" />
          <text x="125" y="95" fill="#64748b" fontSize="8" textAnchor="end" fontFamily="monospace">QUAY WALL</text>

          {/* Water area label */}
          <text x="450" y="40" fill="#1e3a5f" fontSize="10" fontFamily="monospace" textAnchor="middle" opacity="0.6">
            — PORT WATERS —
          </text>

          {/* Navigation Channels */}
          {CHANNEL_PATHS.map((ch, i) => (
            <g key={i}>
              <path d={ch.points} fill="none" stroke={ch.color} strokeWidth="1.5" strokeDasharray="6 4" opacity="0.3" />
              <path d={ch.points} fill="none" stroke={ch.color} strokeWidth="0.5" opacity="0.6" />
            </g>
          ))}

          {/* Channel Labels */}
          <text x="560" y="90" fill="#06b6d4" fontSize="7" fontFamily="monospace" opacity="0.7">North Ch.</text>
          <text x="560" y="310" fill="#8b5cf6" fontSize="7" fontFamily="monospace" opacity="0.7">South Ch.</text>
          <text x="570" y="192" fill="#3b82f6" fontSize="7" fontFamily="monospace" opacity="0.7">Deep-water</text>

          {/* Berths */}
          {BERTH_POSITIONS.map((bp) => {
            const berthData = data?.berths?.find((b: any) => b.id?.includes?.(bp.id) || b.name?.includes?.(bp.name));
            const status = berthData?.status || "available";
            const color = berthStatusColor(status);

            return (
              <g key={bp.id}>
                <rect
                  x={bp.x}
                  y={bp.y}
                  width={bp.w}
                  height={bp.h}
                  fill={`${color}15`}
                  stroke={color}
                  strokeWidth="1"
                  rx="3"
                />
                <text x={bp.x + 5} y={bp.y + 12} fill={color} fontSize="7" fontFamily="monospace" fontWeight="bold">
                  B-{bp.name}
                </text>
                <text x={bp.x + 5} y={bp.y + 22} fill="#64748b" fontSize="6" fontFamily="monospace">
                  {status.toUpperCase()} | {bp.w * 2.5}m
                </text>
              </g>
            );
          })}

          {/* Yard Zones */}
          <rect x="20" y="110" width="90" height="50" fill="#1e293b" stroke="#334155" strokeWidth="0.5" rx="3" />
          <text x="30" y="128" fill="#64748b" fontSize="7" fontFamily="monospace">YARD A</text>
          <text x="30" y="140" fill="#f59e0b" fontSize="6" fontFamily="monospace">{((data?.kpis?.yard_utilization || 0) * 100).toFixed(0)}% util</text>

          <rect x="20" y="170" width="90" height="50" fill="#1e293b" stroke="#334155" strokeWidth="0.5" rx="3" />
          <text x="30" y="188" fill="#64748b" fontSize="7" fontFamily="monospace">YARD B-C</text>

          <rect x="20" y="230" width="90" height="50" fill="#1e293b" stroke="#334155" strokeWidth="0.5" rx="3" />
          <text x="30" y="248" fill="#64748b" fontSize="7" fontFamily="monospace">YARD D-F</text>
          <text x="30" y="260" fill="#64748b" fontSize="6" fontFamily="monospace">Reefer/Hazmat</text>

          {/* Anchorage Zone */}
          <rect x="360" y="130" width="80" height="100" fill="none" stroke="#475569" strokeWidth="0.5" strokeDasharray="4 4" rx="5" />
          <text x="370" y="145" fill="#475569" fontSize="7" fontFamily="monospace">ANCHORAGE</text>

          {/* Vessels */}
          {vessels.map((v, i) => {
            const pos = getVesselPosition(v, i);
            const color = vesselStatusColor(v.status);
            const isSelected = v.id === selectedVessel;
            const size = Math.max(8, Math.min(16, v.length_m / 25));

            return (
              <g
                key={v.id}
                onClick={() => setSelectedVessel(isSelected ? null : v.id)}
                style={{ cursor: "pointer" }}
              >
                {isSelected && (
                  <circle cx={pos.x} cy={pos.y} r={size + 5} fill="none" stroke={color} strokeWidth="1" opacity="0.5">
                    <animate attributeName="r" from={size + 3} to={size + 8} dur="1.5s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.5" to="0" dur="1.5s" repeatCount="indefinite" />
                  </circle>
                )}
                <polygon
                  points={`${pos.x},${pos.y - size / 2} ${pos.x + size},${pos.y} ${pos.x},${pos.y + size / 2} ${pos.x - size / 3},${pos.y}`}
                  fill={color}
                  stroke={isSelected ? "#fff" : color}
                  strokeWidth={isSelected ? 1.5 : 0.5}
                  opacity={0.9}
                />
                <text
                  x={pos.x + size + 3}
                  y={pos.y + 3}
                  fill={color}
                  fontSize="5.5"
                  fontFamily="monospace"
                  opacity="0.8"
                >
                  {v.name.replace("MV ", "")}
                </text>
              </g>
            );
          })}

          {/* Legend */}
          <g transform="translate(460, 340)">
            {[
              { label: "At Berth/Ops", color: "#10b981" },
              { label: "Approaching", color: "#f59e0b" },
              { label: "Waiting", color: "#ef4444" },
              { label: "At Sea", color: "#6366f1" },
            ].map((item, i) => (
              <g key={i} transform={`translate(${i * 48}, 0)`}>
                <circle cx="4" cy="4" r="3" fill={item.color} />
                <text x="10" y="7" fill="#94a3b8" fontSize="5" fontFamily="monospace">{item.label}</text>
              </g>
            ))}
          </g>
        </svg>

        {/* Playback Controls */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 bg-slate-900/90 border border-slate-800 px-4 py-2 rounded-lg backdrop-blur">
          <button onClick={handleReset} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white" title="Reset">
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setAutoPlay(!autoPlay)}
            className="px-3 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs flex items-center gap-1.5"
          >
            {autoPlay ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>{autoPlay ? "PAUSE" : "PLAY"} T+{data?.elapsed_hours?.toFixed(0) || "00"}h</span>
          </button>
          <button
            onClick={() => setSpeed((s) => (s >= 6 ? 1 : s * 2))}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
            title="Change Speed"
          >
            <FastForward className="w-4 h-4" />
          </button>
          <span className="text-[11px] font-mono text-slate-500 border-l border-slate-800 pl-3">
            SPEED: {speed}x
          </span>
        </div>
      </div>

      {/* Selected Vessel Info */}
      {selectedVesselData && (
        <div className="ops-panel rounded-xl p-4 border border-cyan-900/40 bg-cyan-950/10">
          <div className="flex items-center gap-3 mb-2">
            <Ship className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-semibold text-white">{selectedVesselData.name}</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono border`} style={{ color: vesselStatusColor(selectedVesselData.status), borderColor: vesselStatusColor(selectedVesselData.status) + "60" }}>
              {selectedVesselData.status.toUpperCase().replace("_", " ")}
            </span>
          </div>
          <div className="grid grid-cols-4 gap-4 text-xs font-mono text-slate-400">
            <div>Length: <span className="text-white">{selectedVesselData.length_m}m</span></div>
            <div>Draft: <span className="text-white">{selectedVesselData.draft_m}m</span></div>
            <div>Containers: <span className="text-white">{selectedVesselData.containers_to_handle?.toLocaleString() || "N/A"}</span></div>
            <div>Berth: <span className="text-cyan-400">{selectedVesselData.assigned_berth_id ? "Assigned" : "None"}</span></div>
          </div>
        </div>
      )}
    </div>
  );
}
