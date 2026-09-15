/**
 * HarborAI API Client
 * 
 * Centralized API client for all backend calls.
 * Uses environment variable NEXT_PUBLIC_API_URL for the backend URL.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Core Data APIs
// ---------------------------------------------------------------------------

export async function fetchVessels() {
  return fetchAPI<{ data: any[]; total: number }>('/api/vessels?limit=50');
}

export async function fetchBerths() {
  return fetchAPI<{ data: any[]; total: number }>('/api/berths?limit=20');
}

export async function fetchCranes() {
  return fetchAPI<{ data: any[]; total: number }>('/api/cranes?limit=20');
}

export async function fetchYardZones() {
  return fetchAPI<{ data: any[]; total: number }>('/api/yard?limit=20');
}

export async function fetchRoutes() {
  return fetchAPI<{ data: any[]; total: number }>('/api/routes?limit=10');
}

export async function fetchPortStatus() {
  return fetchAPI<any>('/api/port-status');
}

// ---------------------------------------------------------------------------
// Simulation APIs
// ---------------------------------------------------------------------------

export async function fetchSimulationState() {
  return fetchAPI<any>('/api/simulation/state');
}

export async function fetchSimulationKPIs() {
  return fetchAPI<any>('/api/simulation/kpis');
}

export async function startSimulation(seed?: number) {
  return fetchAPI<any>('/api/simulation/start', {
    method: 'POST',
    body: JSON.stringify(seed ? { seed } : {}),
  });
}

export async function pauseSimulation() {
  return fetchAPI<any>('/api/simulation/pause', { method: 'POST' });
}

export async function resetSimulation(seed: number = 42) {
  return fetchAPI<any>('/api/simulation/reset', {
    method: 'POST',
    body: JSON.stringify({ seed }),
  });
}

export async function advanceSimulation(hours: number = 1) {
  return fetchAPI<any>('/api/simulation/advance', {
    method: 'POST',
    body: JSON.stringify({ hours }),
  });
}

export async function fetchSimulationEvents(limit: number = 20) {
  return fetchAPI<any>(`/api/simulation/events?limit=${limit}`);
}

// ---------------------------------------------------------------------------
// Prediction APIs
// ---------------------------------------------------------------------------

export async function fetchPredictionStatus() {
  return fetchAPI<any>('/api/prediction/status');
}

export async function predictCongestion(features: Record<string, number>) {
  return fetchAPI<any>('/api/prediction/congestion', {
    method: 'POST',
    body: JSON.stringify(features),
  });
}

// ---------------------------------------------------------------------------
// Optimization APIs
// ---------------------------------------------------------------------------

export async function runOptimization(timeLimitSeconds: number = 10) {
  return fetchAPI<any>('/api/optimization/run', {
    method: 'POST',
    body: JSON.stringify({ time_limit_seconds: timeLimitSeconds }),
  });
}

export async function fetchOptimizationResult() {
  return fetchAPI<any>('/api/optimization/result');
}

export async function comparePlans() {
  return fetchAPI<any>('/api/optimization/compare', { method: 'POST' });
}

export async function runScenario(
  scenarioType: string,
  targetId: string,
  parameters: Record<string, any> = {},
) {
  return fetchAPI<any>('/api/optimization/scenario', {
    method: 'POST',
    body: JSON.stringify({
      scenario_type: scenarioType,
      target_id: targetId,
      parameters,
    }),
  });
}

export async function fetchRouteRecommendation(vesselId: string) {
  return fetchAPI<any>(`/api/optimization/routes/${vesselId}`);
}

export async function fetch72HPlan() {
  return fetchAPI<any>('/api/optimization/plan72h');
}

// ---------------------------------------------------------------------------
// AI Copilot APIs
// ---------------------------------------------------------------------------

export async function chatWithCopilot(message: string) {
  return fetchAPI<any>('/api/copilot/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

export async function fetchOperationsBrief() {
  return fetchAPI<any>('/api/copilot/brief');
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export async function fetchHealth() {
  return fetchAPI<any>('/api/health');
}
