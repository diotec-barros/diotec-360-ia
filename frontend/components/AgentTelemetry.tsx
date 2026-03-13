'use client';

import { useMemo } from 'react';

export type TelemetryEntry = {
  t: number;
  source: 'agent' | 'sentinel' | 'system';
  message: string;
};

export type AgentTelemetryProps = {
  entries: TelemetryEntry[];
};

function formatMs(ms: number) {
  const s = (ms / 1000).toFixed(3);
  return `[${s}s]`;
}

export default function AgentTelemetry({ entries }: AgentTelemetryProps) {
  const rendered = useMemo(() => {
    const base = entries.slice(-200);
    return base;
  }, [entries]);

  return (
    <div className="bg-black/30 border border-gray-800 rounded-lg p-4">
      <div className="text-sm font-semibold mb-3">Agent Telemetry</div>
      <div className="bg-black/40 border border-gray-900 rounded p-3 h-56 overflow-auto font-mono text-xs text-gray-300 space-y-1">
        {rendered.length === 0 ? (
          <div className="text-gray-500">No telemetry yet.</div>
        ) : (
          rendered.map((e, idx) => (
            <div key={idx} className="whitespace-pre-wrap break-words">
              <span className="text-gray-500">{formatMs(e.t)} </span>
              <span className={
                e.source === 'agent'
                  ? 'text-emerald-300'
                  : e.source === 'sentinel'
                    ? 'text-amber-300'
                    : 'text-purple-300'
              }>
                {e.source.toUpperCase()}:
              </span>
              <span className="text-gray-200"> {e.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
