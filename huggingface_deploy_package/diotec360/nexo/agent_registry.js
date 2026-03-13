/**
 * Aethel Agent Registry (v4.3)
 *
 * P2P-first registry interface, designed to run in browser or Node.
 * - If GunDB is available (provided by host), it will use it.
 * - Otherwise, it falls back to an in-memory registry (single runtime scope).
 *
 * This module intentionally does NOT import Gun to avoid adding a hard dependency.
 */

/**
 * @typedef {Object} AgentRecord
 * @property {string} agentId
 * @property {string} name
 * @property {string} mission
 * @property {string} proofHash
 * @property {string} judgeVersion
 * @property {string} creatorPublicKeyHex
 * @property {string} nodeId
 * @property {number} createdAt
 * @property {number} lastSeenAt
 * @property {Object} [meta]
 */

/**
 * @typedef {Object} RegistryOptions
 * @property {any} [gun]          // Pass a configured Gun instance if available
 * @property {string} [namespace] // key prefix / root set name
 * @property {number} [ttlMs]     // stale cutoff
 */

function _now() {
  return Date.now();
}

function _nsKey(ns) {
  return (ns || 'aethel_agent_registry').toString();
}

class InMemoryBackend {
  constructor(ttlMs) {
    /** @type {Map<string, AgentRecord>} */
    this.map = new Map();
    this.ttlMs = ttlMs;
  }

  _gc() {
    const cutoff = _now() - this.ttlMs;
    for (const [k, v] of this.map.entries()) {
      if ((v.lastSeenAt || 0) < cutoff) this.map.delete(k);
    }
  }

  async put(record) {
    this._gc();
    this.map.set(record.agentId, record);
  }

  async del(agentId) {
    this._gc();
    this.map.delete(agentId);
  }

  async get(agentId) {
    this._gc();
    return this.map.get(agentId) || null;
  }

  async list() {
    this._gc();
    return Array.from(this.map.values());
  }
}

class GunBackend {
  constructor(gun, namespace, ttlMs) {
    this.gun = gun;
    this.namespace = namespace;
    this.ttlMs = ttlMs;
  }

  _root() {
    return this.gun.get(this.namespace);
  }

  async put(record) {
    // Gun is eventually consistent; we store by agentId.
    this._root().get(record.agentId).put(record);
  }

  async del(agentId) {
    // Tombstone delete.
    this._root().get(agentId).put({ deleted: true, lastSeenAt: _now() });
  }

  async get(agentId) {
    return await new Promise((resolve) => {
      this._root().get(agentId).once((data) => {
        if (!data || data.deleted) return resolve(null);
        resolve(data);
      });
    });
  }

  async list() {
    const cutoff = _now() - this.ttlMs;
    return await new Promise((resolve) => {
      /** @type {AgentRecord[]} */
      const out = [];
      this._root().map().once((data) => {
        if (!data || data.deleted) return;
        if ((data.lastSeenAt || 0) < cutoff) return;
        out.push(data);
      });

      // Gun map() is streaming; settle after a small delay.
      setTimeout(() => resolve(out), 150);
    });
  }
}

export class AgentRegistry {
  /**
   * @param {RegistryOptions} [options]
   */
  constructor(options = {}) {
    this.namespace = _nsKey(options.namespace);
    this.ttlMs = Number(options.ttlMs || 60_000);

    if (options.gun) {
      this.backend = new GunBackend(options.gun, this.namespace, this.ttlMs);
      this.mode = 'gun';
    } else {
      this.backend = new InMemoryBackend(this.ttlMs);
      this.mode = 'memory';
    }
  }

  /**
   * Register or upsert an agent record.
   *
   * @param {Omit<AgentRecord,'lastSeenAt'> & {lastSeenAt?:number}} record
   */
  async register(record) {
    if (!record || !record.agentId) throw new Error('AgentRegistry.register: agentId required');
    const now = _now();
    const r = {
      ...record,
      createdAt: Number(record.createdAt || now),
      lastSeenAt: Number(record.lastSeenAt || now),
    };
    await this.backend.put(r);
    return r;
  }

  /**
   * Update lastSeenAt for an agent.
   * @param {string} agentId
   */
  async heartbeat(agentId) {
    if (!agentId) throw new Error('AgentRegistry.heartbeat: agentId required');
    const existing = await this.backend.get(agentId);
    if (!existing) return null;
    const updated = { ...existing, lastSeenAt: _now() };
    await this.backend.put(updated);
    return updated;
  }

  /**
   * Unregister/tombstone an agent.
   * @param {string} agentId
   */
  async unregister(agentId) {
    if (!agentId) throw new Error('AgentRegistry.unregister: agentId required');
    await this.backend.del(agentId);
  }

  /**
   * Find a specific agent.
   * @param {string} agentId
   * @returns {Promise<AgentRecord|null>}
   */
  async get(agentId) {
    return await this.backend.get(agentId);
  }

  /**
   * Discover active agents.
   * @param {{ missionIncludes?: string, creatorPublicKeyHex?: string }} [query]
   * @returns {Promise<AgentRecord[]>}
   */
  async discover(query = {}) {
    const all = await this.backend.list();
    const mi = query.missionIncludes ? query.missionIncludes.toLowerCase() : null;
    const pk = query.creatorPublicKeyHex ? query.creatorPublicKeyHex.toLowerCase() : null;

    return all.filter((r) => {
      if (mi && !(r.mission || '').toLowerCase().includes(mi)) return false;
      if (pk && (r.creatorPublicKeyHex || '').toLowerCase() !== pk) return false;
      return true;
    });
  }
}

/**
 * Convenience creator.
 * @param {RegistryOptions} [options]
 */
export function createAgentRegistry(options = {}) {
  return new AgentRegistry(options);
}
