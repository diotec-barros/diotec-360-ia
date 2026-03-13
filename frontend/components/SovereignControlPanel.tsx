'use client';

import { useEffect, useMemo, useState } from 'react';
import { Crown, Power, ShieldCheck, Sparkles } from 'lucide-react';
import { getSovereignIdentityEventName, loadSovereignKeyPair, purgeSovereignIdentity } from '@/lib/agentNexus';

function bytesFromHexNibble(n: string) {
  const v = parseInt(n, 16);
  return Number.isFinite(v) ? v : 0;
}

function makeIdenticon(seedHex: string) {
  const hex = seedHex.toLowerCase().replace(/^0x/, '').padEnd(40, '0');
  const size = 5;

  const pattern: boolean[][] = [];
  for (let y = 0; y < size; y++) {
    pattern[y] = [];
    for (let x = 0; x < size; x++) {
      const index = x < 3 ? x : 4 - x;
      const charIndex = (y * 3 + index) % hex.length;
      const value = bytesFromHexNibble(hex[charIndex]);
      pattern[y][x] = value > 7;
    }
  }

  const hue = parseInt(hex.slice(0, 3), 16) % 360;
  const color = `hsl(${hue}, 70%, 60%)`;

  return { pattern, color, short: hex.slice(0, 10) };
}

export type SovereignControlPanelProps = {
  onSpawn: () => Promise<void>;
  onKill: () => void;
  isSpawning: boolean;
  canKill: boolean;
};

export default function SovereignControlPanel({ onSpawn, onKill, isSpawning, canKill }: SovereignControlPanelProps) {
  const [publicKeyHex, setPublicKeyHex] = useState<string>('');
  const [wipeArmed, setWipeArmed] = useState(false);
  const [wipeMessage, setWipeMessage] = useState('');

  useEffect(() => {
    const refresh = () => {
      const kp = loadSovereignKeyPair();
      setPublicKeyHex(kp?.publicKeyHex || '');
    };

    refresh();
    const ev = getSovereignIdentityEventName();
    window.addEventListener(ev, refresh);
    return () => window.removeEventListener(ev, refresh);
  }, []);

  useEffect(() => {
    if (!wipeArmed) return;
    const t = window.setTimeout(() => setWipeArmed(false), 2500);
    return () => window.clearTimeout(t);
  }, [wipeArmed]);

  const identicon = useMemo(() => (publicKeyHex ? makeIdenticon(publicKeyHex) : null), [publicKeyHex]);

  return (
    <div className="bg-black/30 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex items-center gap-2">
            <Crown className="w-4 h-4 text-amber-300" />
            <span className="text-sm font-semibold">Sovereign Control</span>
          </div>

          {identicon ? (
            <div className="flex items-center gap-3 ml-3">
              <div className="relative w-9 h-9 rounded border-2 overflow-hidden" style={{ borderColor: identicon.color }}>
                <div className="absolute inset-0 bg-gray-900" />
                <div className="absolute inset-0 grid grid-cols-5 grid-rows-5 p-0.5 gap-0.5">
                  {identicon.pattern.map((row, y) =>
                    row.map((cell, x) => (
                      <div
                        key={`${x}-${y}`}
                        className="rounded-sm"
                        style={{ backgroundColor: cell ? identicon.color : 'transparent' }}
                      />
                    ))
                  )}
                </div>
                <div className="absolute inset-0 opacity-20 blur-sm" style={{ backgroundColor: identicon.color }} />
              </div>

              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-mono text-gray-300 truncate">{identicon.short}...</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Sparkles className="w-4 h-4 text-purple-300" />
                  <span className="text-xs text-gray-400">ED25519 local key</span>
                </div>
              </div>
            </div>
          ) : (
            <span className="text-xs text-gray-500 ml-3">No sovereign key</span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={onSpawn}
            disabled={isSpawning}
            className="px-4 py-2 rounded-lg font-semibold transition-colors border border-purple-400/30 bg-gradient-to-r from-purple-700 to-amber-600 hover:from-purple-600 hover:to-amber-500 disabled:bg-gray-700 disabled:cursor-not-allowed"
          >
            {isSpawning ? 'Spawning…' : 'Spawn Sovereign Agent'}
          </button>

          <button
            onClick={onKill}
            disabled={!canKill}
            className="px-3 py-2 rounded-lg font-semibold transition-colors bg-red-700 hover:bg-red-600 disabled:bg-gray-700 disabled:cursor-not-allowed flex items-center gap-2"
            title="Kill-Switch"
          >
            <Power className="w-4 h-4" />
            Kill
          </button>

          <button
            onClick={() => {
              setWipeMessage('');
              if (!wipeArmed) {
                setWipeArmed(true);
                return;
              }
              purgeSovereignIdentity();
              setWipeArmed(false);
              setWipeMessage('Identity Purged. Device is now a blank node.');
            }}
            disabled={isSpawning}
            className={
              wipeArmed
                ? 'px-3 py-2 rounded-lg font-semibold transition-colors bg-red-600 hover:bg-red-500 disabled:bg-gray-700 disabled:cursor-not-allowed'
                : 'px-3 py-2 rounded-lg font-semibold transition-colors bg-red-900/60 hover:bg-red-800 disabled:bg-gray-700 disabled:cursor-not-allowed'
            }
            title={wipeArmed ? 'Click again to confirm purge' : 'Wipe Secure'}
          >
            {wipeArmed ? 'Confirm Wipe' : 'Wipe Secure'}
          </button>
        </div>
      </div>

      {wipeMessage ? (
        <div className="mt-3 bg-red-900/20 border border-red-700/40 rounded p-3 text-sm text-red-100">
          {wipeMessage}
        </div>
      ) : null}
    </div>
  );
}
