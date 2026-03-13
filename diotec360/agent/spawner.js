/**
 * Aethel Agent Spawner (v4.3)
 *
 * Browser-first WebWorker spawner that turns a proven intent/manifest into
 * an autonomous worker.
 *
 * Design goals:
 * - No mandatory external deps
 * - Deterministic, safe-by-default message protocol
 * - "Sovereign Link" is pluggable: pass verifySignature() (ED25519) from the host
 */

/**
 * @typedef {Object} AgentManifest
 * @property {string} agentId
 * @property {string} name
 * @property {string} mission
 * @property {Object} invariants
 * @property {Object} proven
 * @property {string} proven.proofHash
 * @property {string} proven.judgeVersion
 * @property {string} [creatorPublicKeyHex]
 * @property {string} [creatorSignatureHex]
 * @property {number} [createdAt]
 */

/**
 * @typedef {Object} SpawnOptions
 * @property {(publicKeyHex:string, message:string, signatureHex:string)=>Promise<boolean>|boolean} [verifySignature]
 * @property {(manifest:AgentManifest)=>string} [getSovereignMessage]
 * @property {boolean} [requireSovereignLink]
 * @property {number} [handshakeTimeoutMs]
 * @property {string} [workerName]
 */

/**
 * @typedef {Object} SpawnedAgent
 * @property {string} agentId
 * @property {Worker} worker
 * @property {(type:string, payload:any)=>void} send
 * @property {()=>Promise<void>} stop
 * @property {(fn:(evt:MessageEvent)=>void)=>()=>void} onMessage
 */

function _now() {
  return Date.now();
}

function _stableStringify(obj) {
  // Canonical-ish stringify: stable key order for shallow objects.
  // Deep canonicalization is responsibility of the signer.
  if (obj === null || obj === undefined) return String(obj);
  if (typeof obj !== 'object') return JSON.stringify(obj);
  if (Array.isArray(obj)) return JSON.stringify(obj.map(_stableStringify));
  const keys = Object.keys(obj).sort();
  const o = {};
  for (const k of keys) o[k] = obj[k];
  return JSON.stringify(o);
}

function _buildCreatorMessage(manifest) {
  // The host should sign *exactly* this message when using the Sovereign Link.
  return _stableStringify({
    agentId: manifest.agentId,
    proofHash: manifest?.proven?.proofHash,
    mission: manifest.mission,
    invariants: manifest.invariants,
    createdAt: manifest.createdAt || 0,
  });
}

function _createWorkerSource() {
  // NOTE: keep it self-contained. No imports.
  return `
  const STATE = {
    startedAt: Date.now(),
    manifest: null,
    running: false,
    ticks: 0,
  };

  function reply(type, payload) {
    self.postMessage({ type, payload, ts: Date.now() });
  }

  function tick() {
    if (!STATE.running) return;
    STATE.ticks += 1;
    reply('agent:tick', { agentId: STATE.manifest.agentId, ticks: STATE.ticks });
  }

  self.onmessage = (evt) => {
    const msg = evt.data || {};

    if (msg.type === 'agent:init') {
      STATE.manifest = msg.payload.manifest;
      STATE.running = true;
      reply('agent:ready', {
        agentId: STATE.manifest.agentId,
        name: STATE.manifest.name,
        judge: STATE.manifest?.proven?.judgeVersion,
      });
      // Basic autonomous loop. Host controls by sending agent:stop.
      if (STATE.manifest?.invariants?.tickIntervalMs) {
        setInterval(tick, Number(STATE.manifest.invariants.tickIntervalMs) || 1000);
      }
      return;
    }

    if (msg.type === 'agent:event') {
      // Host can send events to the agent.
      reply('agent:event:ack', {
        agentId: STATE.manifest?.agentId,
        eventType: msg.payload?.eventType,
      });
      return;
    }

    if (msg.type === 'agent:stop') {
      STATE.running = false;
      reply('agent:stopped', { agentId: STATE.manifest?.agentId });
      self.close();
      return;
    }

    reply('agent:error', { message: 'Unknown message type', received: msg.type });
  };
  `;
}

/**
 * Spawn an autonomous agent worker.
 *
 * Sovereign Link:
 * - If manifest contains creatorPublicKeyHex + creatorSignatureHex, we verify it
 *   against a canonical message derived from the manifest.
 * - If verifySignature is missing, we still spawn but return a handshake event
 *   indicating sovereignLinkVerified=false.
 *
 * @param {AgentManifest} manifest
 * @param {SpawnOptions} [options]
 * @returns {Promise<SpawnedAgent>}
 */
export async function spawnAgent(manifest, options = {}) {
  if (!manifest || typeof manifest !== 'object') {
    throw new Error('spawnAgent: manifest is required');
  }
  if (!manifest.agentId) {
    throw new Error('spawnAgent: manifest.agentId is required');
  }
  if (!manifest.proven || !manifest.proven.proofHash) {
    throw new Error('spawnAgent: manifest.proven.proofHash is required');
  }

  const handshakeTimeoutMs = Number(options.handshakeTimeoutMs || 1500);

  const requireSovereignLink = Boolean(options.requireSovereignLink);
  const getSovereignMessage =
    typeof options.getSovereignMessage === 'function'
      ? options.getSovereignMessage
      : _buildCreatorMessage;

  let sovereignLinkVerified = false;
  let sovereignLinkAttempted = false;

  const hasSovereignData = Boolean(manifest.creatorPublicKeyHex && manifest.creatorSignatureHex);
  if (requireSovereignLink && !hasSovereignData) {
    throw new Error('spawnAgent: sovereign link required but creatorPublicKeyHex/creatorSignatureHex missing');
  }
  if (requireSovereignLink && typeof options.verifySignature !== 'function') {
    throw new Error('spawnAgent: sovereign link required but verifySignature() not provided');
  }

  if (hasSovereignData) {
    sovereignLinkAttempted = true;
    const msg = getSovereignMessage(manifest);
    if (typeof options.verifySignature === 'function') {
      const res = await options.verifySignature(
        manifest.creatorPublicKeyHex,
        msg,
        manifest.creatorSignatureHex
      );
      sovereignLinkVerified = Boolean(res);
      if (!sovereignLinkVerified) {
        throw new Error('spawnAgent: sovereign link signature verification failed');
      }
    }
  }

  const src = _createWorkerSource();
  const blob = new Blob([src], { type: 'text/javascript' });
  const url = URL.createObjectURL(blob);

  const worker = new Worker(url, { name: options.workerName || `aethel-agent-${manifest.agentId}` });
  URL.revokeObjectURL(url);

  /** @type {Array<(evt:MessageEvent)=>void>} */
  const listeners = [];

  worker.onmessage = (evt) => {
    for (const fn of listeners) fn(evt);
  };

  const readyPromise = new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('spawnAgent: handshake timeout')), handshakeTimeoutMs);

    const unsubscribe = (evt) => {
      const msg = evt.data || {};
      if (msg.type === 'agent:ready') {
        clearTimeout(t);
        off();
        resolve(msg);
      }
      if (msg.type === 'agent:error') {
        clearTimeout(t);
        off();
        reject(new Error(`spawnAgent: worker error: ${msg?.payload?.message || 'unknown'}`));
      }
    };

    const off = () => {
      const idx = listeners.indexOf(unsubscribe);
      if (idx >= 0) listeners.splice(idx, 1);
    };

    listeners.push(unsubscribe);
  });

  worker.postMessage({
    type: 'agent:init',
    payload: {
      manifest: {
        ...manifest,
        createdAt: manifest.createdAt || _now(),
        sovereignLink: {
          attempted: sovereignLinkAttempted,
          verified: sovereignLinkVerified,
          hasData: hasSovereignData,
          verifierPresent: typeof options.verifySignature === 'function',
        },
      },
    },
  });

  await readyPromise;

  return {
    agentId: manifest.agentId,
    worker,
    send: (type, payload) => worker.postMessage({ type, payload }),
    stop: async () => {
      try {
        worker.postMessage({ type: 'agent:stop', payload: {} });
      } finally {
        worker.terminate();
      }
    },
    onMessage: (fn) => {
      listeners.push(fn);
      return () => {
        const idx = listeners.indexOf(fn);
        if (idx >= 0) listeners.splice(idx, 1);
      };
    },
  };
}

/**
 * Helper for host-side signing/verification.
 * The signer MUST sign exactly this message if it wants strict verification.
 *
 * @param {AgentManifest} manifest
 * @returns {string}
 */
export function buildSovereignLinkMessage(manifest) {
  return _buildCreatorMessage(manifest);
}
