"use client";

import * as ed from "@noble/ed25519";
import { sha512 } from "@noble/hashes/sha512";
import { sha256 } from "@noble/hashes/sha256";

function ensureNobleReady() {
  // noble/ed25519 needs a SHA-512 implementation in some environments.
  // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
  if (!ed.etc.sha512Sync) {
    ed.etc.sha512Sync = (...m: Uint8Array[]) => sha512(ed.etc.concatBytes(...m));
  }
}

function hexToBytes(hex: string) {
  const clean = hex.trim().toLowerCase().replace(/^0x/, "");
  if (clean.length % 2 !== 0) throw new Error("Invalid hex length");
  const out = new Uint8Array(clean.length / 2);
  for (let i = 0; i < out.length; i++) {
    out[i] = parseInt(clean.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

function bytesToHex(bytes: Uint8Array) {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function utf8Bytes(s: string) {
  return new TextEncoder().encode(s);
}

export type KeyPairHex = {
  publicKeyHex: string;
  privateKeyHex: string;
};

export async function generateKeyPair(): Promise<KeyPairHex> {
  ensureNobleReady();
  const priv = ed.utils.randomPrivateKey();
  const pub = await ed.getPublicKeyAsync(priv);
  return {
    publicKeyHex: bytesToHex(pub),
    privateKeyHex: bytesToHex(priv),
  };
}

export async function signMessage(privateKeyHex: string, message: string) {
  ensureNobleReady();
  const priv = hexToBytes(privateKeyHex);
  const msg = utf8Bytes(message);
  const sig = await ed.signAsync(msg, priv);
  return bytesToHex(sig);
}

export async function verifyMessage(publicKeyHex: string, message: string, signatureHex: string) {
  ensureNobleReady();
  const pub = hexToBytes(publicKeyHex);
  const msg = utf8Bytes(message);
  const sig = hexToBytes(signatureHex);
  return await ed.verifyAsync(sig, msg, pub);
}

export function hashProofBundle(payload: unknown) {
  // Deterministic proof hash used as the anchor for sovereign link.
  // Callers MUST pass a stable/canonical structure.
  const json = JSON.stringify(payload);
  const digest = sha256(utf8Bytes(json));
  return bytesToHex(digest);
}

export async function signProofHash(privateKeyHex: string, proofHash: string) {
  return await signMessage(privateKeyHex, proofHash);
}

export async function verifyAuthority(publicKeyHex: string, proofHash: string, signatureHex: string) {
  return await verifyMessage(publicKeyHex, proofHash, signatureHex);
}
