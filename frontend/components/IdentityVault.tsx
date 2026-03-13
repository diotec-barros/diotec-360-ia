'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { Download, Upload, TriangleAlert, BadgeCheck } from 'lucide-react';
import * as ed from '@noble/ed25519';
import { sha512 } from '@noble/hashes/sha512';
import { QRCodeSVG } from 'qrcode.react';
import * as pako from 'pako';
import {
  getSovereignIdentityEventName,
  getOrCreateSovereignKeyPair,
  getSovereignBackupStatus,
  loadSovereignKeyPair,
  setSovereignBackupStatus,
  storeSovereignKeyPair,
} from '@/lib/agentNexus';
import {
  decryptBlobToJson,
  downloadTextFile,
  encryptJsonToBlob,
  readFileAsText,
  type EncryptedBlobV1,
} from '@/lib/cryptoVault';

const QR_PREFIX = 'diotec360qr1:';

function bytesToBase64(bytes: Uint8Array) {
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

function base64ToBytes(b64: string) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function encodeQrPayloadFromBlob(blob: EncryptedBlobV1) {
  const json = JSON.stringify(blob);
  const raw = new TextEncoder().encode(json);
  const deflated = pako.deflate(raw);
  return `${QR_PREFIX}${bytesToBase64(deflated)}`;
}

function decodeBlobFromQrPayload(payload: string): EncryptedBlobV1 {
  const trimmed = String(payload || '').trim();

  if (trimmed.startsWith(QR_PREFIX)) {
    const b64 = trimmed.slice(QR_PREFIX.length);
    const deflatedBytes = base64ToBytes(b64);
    const inflated = pako.inflate(deflatedBytes);
    const json = new TextDecoder().decode(inflated);
    return JSON.parse(json) as EncryptedBlobV1;
  }

  return JSON.parse(trimmed) as EncryptedBlobV1;
}

function tryBeep() {
  try {
    const AudioCtx: any = (window as any).AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = 880;
    gain.gain.value = 0.05;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.08);
    osc.onended = () => {
      try {
        ctx.close();
      } catch {
        // ignore
      }
    };
  } catch {
    // ignore
  }
}

export default function IdentityVault() {
  const fileRef = useRef<HTMLInputElement | null>(null);
  const scanRegionId = useMemo(() => `diotec360-qr-scan-${Math.random().toString(16).slice(2)}`, []);
  const [backedUp, setBackedUp] = useState(false);
  const [backedUpAt, setBackedUpAt] = useState<number | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [passphrase, setPassphrase] = useState('');
  const [importPassphrase, setImportPassphrase] = useState('');
  const [exportQrPayload, setExportQrPayload] = useState<string>('');
  const [exportFilename, setExportFilename] = useState<string>('');
  const [scanOpen, setScanOpen] = useState(false);
  const [scanOk, setScanOk] = useState(false);
  const [scanRemainingMs, setScanRemainingMs] = useState<number>(0);
  const [scanTimeoutMessage, setScanTimeoutMessage] = useState<string>('');

  useEffect(() => {
    const refresh = () => {
      const s = getSovereignBackupStatus();
      setBackedUp(Boolean(s.backedUp));
      setBackedUpAt(s.backedUpAt);
    };
    refresh();
    const ev = getSovereignIdentityEventName();
    window.addEventListener(ev, refresh);
    return () => window.removeEventListener(ev, refresh);
  }, []);

  useEffect(() => {
    if (!scanOpen) return;

    let stopped = false;
    let qr: any = null;
    let handled = false;

    const windowMs = 10_000;
    const deadline = Date.now() + windowMs;
    setScanTimeoutMessage('');
    setScanRemainingMs(windowMs);

    const intervalId = window.setInterval(() => {
      const remaining = Math.max(0, deadline - Date.now());
      setScanRemainingMs(remaining);
    }, 100);

    const timeoutId = window.setTimeout(async () => {
      if (handled || stopped) return;
      handled = true;
      try {
        if (qr) {
          try {
            await qr.stop();
          } catch {
            // ignore
          }
          try {
            qr.clear();
          } catch {
            // ignore
          }
        }
      } finally {
        setScanTimeoutMessage('Scan Timeout: Perimeter Secured.');
        setScanOpen(false);
        setScanOk(false);
      }
    }, windowMs);

    (async () => {
      try {
        const mod: any = await import('html5-qrcode');
        const Html5Qrcode = mod?.Html5Qrcode;
        if (!Html5Qrcode) throw new Error('QR scanner unavailable');
        if (stopped) return;

        qr = new Html5Qrcode(scanRegionId);
        const config = { fps: 10, qrbox: 240 };

        await qr.start(
          { facingMode: 'environment' },
          config,
          async (decodedText: string) => {
            if (handled) return;
            handled = true;
            try {
              setError('');
              setScanOk(true);
              tryBeep();

              // Bunker Mode: cut camera feed immediately on first successful decode
              try {
                await qr.stop();
              } catch {
                // ignore
              }
              try {
                qr.clear();
              } catch {
                // ignore
              }
              setScanOpen(false);

              setBusy(true);

              const blob = decodeBlobFromQrPayload(decodedText);
              await importFromBlob(blob);

              const s = getSovereignBackupStatus();
              setBackedUp(Boolean(s.backedUp));
              setBackedUpAt(s.backedUpAt);

              window.setTimeout(() => setScanOk(false), 1200);
            } catch (e: any) {
              setError(e?.message ? String(e.message) : String(e));
            } finally {
              setBusy(false);
            }
          }
        );
      } catch (e: any) {
        setError(e?.message ? String(e.message) : String(e));
        setScanOpen(false);
      }
    })();

    return () => {
      stopped = true;
      window.clearInterval(intervalId);
      window.clearTimeout(timeoutId);
      if (qr) {
        try {
          const p = qr.stop();
          Promise.resolve(p).catch(() => undefined);
        } catch {
          // ignore
        }
        try {
          qr.clear();
        } catch {
          // ignore
        }
      }
    };
  }, [scanOpen, scanRegionId]);

  const warning = useMemo(() => {
    if (backedUp) return null;
    return '⚠️ Identity not backed up. Secure your keys.';
  }, [backedUp]);

  const exportIdentity = async () => {
    setBusy(true);
    setError('');
    try {
      const kp = await getOrCreateSovereignKeyPair();
      const blob = await encryptJsonToBlob(
        {
          t: 'diotec360_sovereign_identity',
          publicKeyHex: kp.publicKeyHex,
          privateKeyHex: kp.privateKeyHex,
        },
        passphrase
      );

      const filename = `sovereign_identity_${kp.publicKeyHex.slice(0, 12)}.diotec360_key`;
      downloadTextFile(filename, JSON.stringify(blob, null, 2));
      setExportFilename(filename);
      setExportQrPayload(encodeQrPayloadFromBlob(blob));

      setSovereignBackupStatus(Date.now());
      const s = getSovereignBackupStatus();
      setBackedUp(Boolean(s.backedUp));
      setBackedUpAt(s.backedUpAt);
    } catch (e: any) {
      setError(e?.message ? String(e.message) : String(e));
    } finally {
      setBusy(false);
    }
  };

  const importFromBlob = async (blob: EncryptedBlobV1) => {
    if (!ed.etc.sha512Sync) {
      ed.etc.sha512Sync = (...m: Uint8Array[]) => sha512(ed.etc.concatBytes(...m));
    }

    const json = await decryptBlobToJson(blob, importPassphrase);

    if (json?.t !== 'diotec360_sovereign_identity') {
      throw new Error('Invalid identity file');
    }
    if (!json.publicKeyHex || !json.privateKeyHex) {
      throw new Error('Invalid identity payload');
    }

    const privBytes = ed.etc.hexToBytes(json.privateKeyHex);
    const derivedPub = await ed.getPublicKeyAsync(privBytes);
    const derivedPubHex = ed.etc.bytesToHex(derivedPub);
    if (derivedPubHex.toLowerCase() !== String(json.publicKeyHex).toLowerCase()) {
      throw new Error('🚨 INTEGRITY ERROR: The keypair does not match. Import aborted.');
    }

    storeSovereignKeyPair({ publicKeyHex: json.publicKeyHex, privateKeyHex: json.privateKeyHex });
    setSovereignBackupStatus(Date.now());
    setExportQrPayload('');
    setExportFilename('');
  };

  const importIdentity = async (file: File) => {
    setBusy(true);
    setError('');
    try {
      const txt = await readFileAsText(file);
      const blob = JSON.parse(txt) as EncryptedBlobV1;
      await importFromBlob(blob);

      const s = getSovereignBackupStatus();
      setBackedUp(Boolean(s.backedUp));
      setBackedUpAt(s.backedUpAt);
    } catch (e: any) {
      setError(e?.message ? String(e.message) : String(e));
    } finally {
      setBusy(false);
    }
  };

  const current = useMemo(() => loadSovereignKeyPair(), [backedUp, backedUpAt]);

  return (
    <div className="bg-black/30 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold">Identity Vault</div>
          <div className="text-xs text-gray-400 mt-1">
            {current?.publicKeyHex ? `Active key: ${current.publicKeyHex.slice(0, 16)}…` : 'No key loaded'}
          </div>
          {warning ? (
            <div className="mt-2 flex items-center gap-2 text-xs text-amber-300">
              <TriangleAlert className="w-4 h-4" />
              <span>{warning}</span>
            </div>
          ) : (
            <div className="mt-2 flex items-center gap-2 text-xs text-emerald-300">
              <BadgeCheck className="w-4 h-4" />
              <span>
                Identity backed up
                {backedUpAt ? ` (${new Date(backedUpAt).toLocaleString()})` : ''}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <input
            type="password"
            placeholder="Export passphrase"
            value={passphrase}
            onChange={(e) => setPassphrase(e.target.value)}
            className="px-3 py-2 rounded bg-gray-900 border border-gray-700 text-sm w-44"
          />
          <button
            onClick={exportIdentity}
            disabled={busy}
            className="px-3 py-2 rounded-lg font-semibold transition-colors bg-emerald-700 hover:bg-emerald-600 disabled:bg-gray-700 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export
          </button>

          <input
            type="file"
            ref={fileRef}
            accept=".diotec360_key,application/octet-stream,application/json,text/plain"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) void importIdentity(f);
              if (fileRef.current) fileRef.current.value = '';
            }}
          />

          <input
            type="password"
            placeholder="Import passphrase"
            value={importPassphrase}
            onChange={(e) => setImportPassphrase(e.target.value)}
            className="px-3 py-2 rounded bg-gray-900 border border-gray-700 text-sm w-44"
          />
          <button
            onClick={() => fileRef.current?.click()}
            disabled={busy}
            className="px-3 py-2 rounded-lg font-semibold transition-colors bg-blue-700 hover:bg-blue-600 disabled:bg-gray-700 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            Import
          </button>

          <button
            onClick={() => {
              setError('');
              setScanOpen((v) => !v);
            }}
            disabled={busy}
            className="px-3 py-2 rounded-lg font-semibold transition-colors bg-gray-800 hover:bg-gray-700 disabled:bg-gray-700 disabled:cursor-not-allowed"
            title="Scan QR"
          >
            {scanOpen ? 'Close Scan' : 'Scan QR'}
          </button>
        </div>
      </div>

      {error ? (
        <div className="mt-3 bg-red-900/20 border border-red-700/40 rounded p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {exportQrPayload ? (
        <div className="mt-4 flex items-start gap-4">
          <div className="bg-white rounded p-2">
            <QRCodeSVG value={exportQrPayload} size={160} />
          </div>
          <div className="min-w-0">
            <div className="text-xs text-gray-400">Encrypted QR payload</div>
            <div className="mt-1 text-xs text-gray-500 break-all">
              {exportFilename ? `File: ${exportFilename}` : null}
            </div>
            <div className="mt-2 text-xs text-gray-500 break-all">
              {exportQrPayload.slice(0, 220)}{exportQrPayload.length > 220 ? '…' : ''}
            </div>
          </div>
        </div>
      ) : null}

      {scanOpen ? (
        <div className="mt-4">
          <div
            className={
              scanOk
                ? 'rounded-lg border border-emerald-500/60 bg-emerald-900/10 p-3'
                : 'rounded-lg border border-gray-700 bg-black/20 p-3'
            }
          >
            <div className="h-1 w-full rounded bg-gray-800 overflow-hidden mb-3">
              <div
                className={scanOk ? 'h-1 bg-emerald-400 transition-all' : 'h-1 bg-purple-400 transition-all'}
                style={{ width: `${Math.max(0, Math.min(100, (scanRemainingMs / 10000) * 100))}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 mb-2">Optical Handshake Scanner</div>
            <div className="relative">
              <div id={scanRegionId} className="w-full max-w-md" />
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                <div className={scanOk ? 'w-28 h-28 rounded-full border-2 border-emerald-400/70 animate-pulse' : 'w-28 h-28 rounded-full border-2 border-purple-400/40 animate-pulse'} />
              </div>
            </div>
            <div className="mt-2 text-xs text-gray-500">Tip: use the same import passphrase used on export.</div>
          </div>
        </div>
      ) : null}

      {scanTimeoutMessage ? (
        <div className="mt-3 bg-gray-900/30 border border-gray-700/60 rounded p-3 text-sm text-gray-200">
          {scanTimeoutMessage}
        </div>
      ) : null}
    </div>
  );
}
