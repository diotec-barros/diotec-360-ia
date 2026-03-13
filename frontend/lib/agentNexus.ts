"use client";

import { spawnAgent, buildSovereignLinkMessage } from "../../diotec360/agent/spawner";
import { createAgentRegistry } from "../../diotec360/nexo/agent_registry";
import { getDiotec360JudgeWasm } from "@/lib/diotec360Judge";
import {
  generateKeyPair,
  hashProofBundle,
  signProofHash,
  verifyAuthority,
  type KeyPairHex,
} from "@/lib/diotec360Auth";

export type AgentManifest = {
  agentId: string;
  name: string;
  mission: string;
  invariants: Record<string, unknown>;
  proven: {
    proofHash: string;
    judgeVersion: string;
  };
  creatorPublicKeyHex?: string;
  creatorSignatureHex?: string;
  createdAt?: number;
};

const KEYPAIR_STORAGE_KEY = "diotec360_sovereign_keypair_v1";
const BACKUP_STATUS_KEY = "diotec360_sovereign_keypair_backup_v1";

const SOVEREIGN_IDENTITY_EVENT = "diotec360_sovereign_identity_changed_v1";

function notifySovereignIdentityChanged() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(SOVEREIGN_IDENTITY_EVENT));
}

export function loadSovereignKeyPair(): KeyPairHex | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(KEYPAIR_STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (parsed?.publicKeyHex && parsed?.privateKeyHex) return parsed;
    return null;
  } catch {
    return null;
  }
}

export function storeSovereignKeyPair(kp: KeyPairHex) {
  if (typeof window === "undefined") {
    throw new Error("storeSovereignKeyPair requires browser environment");
  }
  window.localStorage.setItem(KEYPAIR_STORAGE_KEY, JSON.stringify(kp));
  notifySovereignIdentityChanged();
}

export function getSovereignBackupStatus(): { backedUp: boolean; backedUpAt?: number } {
  if (typeof window === "undefined") return { backedUp: false };
  const raw = window.localStorage.getItem(BACKUP_STATUS_KEY);
  if (!raw) return { backedUp: false };
  try {
    const parsed = JSON.parse(raw);
    if (parsed?.backedUpAt) return { backedUp: true, backedUpAt: Number(parsed.backedUpAt) };
    if (parsed?.backedUp === true) return { backedUp: true };
    return { backedUp: false };
  } catch {
    return { backedUp: false };
  }
}

export function setSovereignBackupStatus(backedUpAt: number = Date.now()) {
  if (typeof window === "undefined") {
    throw new Error("setSovereignBackupStatus requires browser environment");
  }
  window.localStorage.setItem(BACKUP_STATUS_KEY, JSON.stringify({ backedUp: true, backedUpAt }));
  notifySovereignIdentityChanged();
}

export function purgeSovereignIdentity() {
  if (typeof window === "undefined") {
    throw new Error("purgeSovereignIdentity requires browser environment");
  }
  window.localStorage.removeItem(KEYPAIR_STORAGE_KEY);
  window.localStorage.removeItem(BACKUP_STATUS_KEY);
  notifySovereignIdentityChanged();
}

export function getSovereignIdentityEventName() {
  return SOVEREIGN_IDENTITY_EVENT;
}

export async function getOrCreateSovereignKeyPair(): Promise<KeyPairHex> {
  if (typeof window === "undefined") {
    throw new Error("Sovereign keypair requires browser environment");
  }

  const existing = loadSovereignKeyPair();
  if (existing) return existing;

  const kp = await generateKeyPair();
  storeSovereignKeyPair(kp);
  return kp;
}

async function tryCreateGun() {
  if (typeof window === "undefined") return null;

  const w = window as unknown as { Gun?: any };
  if (w.Gun) return w.Gun;

  try {
    const mod: any = await import("gun");
    return mod?.default || mod;
  } catch {
    return null;
  }
}

async function tryCreateGunInstance() {
  const Gun = await tryCreateGun();
  if (!Gun) return null;

  const peersEnv = (process.env.NEXT_PUBLIC_GUN_PEERS || "").trim();
  const peers = peersEnv
    ? peersEnv
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
    : null;

  try {
    return peers ? Gun({ peers }) : Gun();
  } catch {
    try {
      return peers ? new Gun({ peers }) : new Gun();
    } catch {
      return null;
    }
  }
}

export async function spawnAgentFromFrontend(manifest: AgentManifest) {
  const gun = await tryCreateGunInstance();
  const registry = createAgentRegistry(gun ? { gun } : undefined);

  // 1) Local proof gate (Z3 WASM)
  const judge = getDiotec360JudgeWasm();
  const dslCode = (manifest as any)?.dslCode || manifest.mission;
  const verdict = await judge.verifyLocally(dslCode);
  if (verdict.status !== "PROVED") {
    throw new Error(`spawnAgentFromFrontend: local judge failed: ${verdict.reason || "FAILED"}`);
  }

  // 2) Build proof bundle hash and sign it (ED25519)
  const proofBundle = {
    agentId: manifest.agentId,
    name: manifest.name,
    mission: manifest.mission,
    dslCode,
    invariants: manifest.invariants,
    judge: {
      engine: "z3-wasm",
      status: verdict.status,
    },
  };
  const proofHash = hashProofBundle(proofBundle);

  const kp = await getOrCreateSovereignKeyPair();
  const signatureHex = await signProofHash(kp.privateKeyHex, proofHash);
  const sigOk = await verifyAuthority(kp.publicKeyHex, proofHash, signatureHex);
  if (!sigOk) {
    throw new Error("spawnAgentFromFrontend: sovereign signature self-check failed");
  }

  const gatedManifest: AgentManifest = {
    ...manifest,
    proven: {
      proofHash,
      judgeVersion: "z3-wasm-v1",
    },
    creatorPublicKeyHex: kp.publicKeyHex,
    creatorSignatureHex: signatureHex,
    createdAt: manifest.createdAt || Date.now(),
  };

  const spawned = await spawnAgent(gatedManifest, {
    handshakeTimeoutMs: 2000,
    requireSovereignLink: true,
    getSovereignMessage: (m: any) => m?.proven?.proofHash,
    verifySignature: async (publicKeyHex: string, message: string, signatureHex: string) => {
      return await verifyAuthority(publicKeyHex, message, signatureHex);
    },
  });

  await registry.register({
    agentId: gatedManifest.agentId,
    name: gatedManifest.name,
    mission: gatedManifest.mission,
    proofHash: gatedManifest.proven.proofHash,
    judgeVersion: gatedManifest.proven.judgeVersion,
    creatorPublicKeyHex: gatedManifest.creatorPublicKeyHex || "",
    nodeId: "frontend",
    createdAt: gatedManifest.createdAt || Date.now(),
    lastSeenAt: Date.now(),
  });

  return {
    spawned,
    registry,
    proofHash,
    publicKeyHex: kp.publicKeyHex,
    signatureHex,
    z3Verified: true,
  };
}

export { buildSovereignLinkMessage };
