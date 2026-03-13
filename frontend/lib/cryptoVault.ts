"use client";

function utf8Bytes(s: string) {
  return new TextEncoder().encode(s);
}

function bytesToBase64(bytes: Uint8Array) {
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

function base64ToBytes(b64: string) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function deriveKey(passphrase: string, salt: Uint8Array, iterations: number) {
  const keyMaterial = await crypto.subtle.importKey("raw", utf8Bytes(passphrase), "PBKDF2", false, ["deriveKey"]);
  return await crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      hash: "SHA-256",
      salt: salt as unknown as BufferSource,
      iterations,
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}

export type EncryptedBlobV1 = {
  v: 1;
  alg: "AES-GCM";
  kdf: "PBKDF2-SHA256";
  iterations: number;
  saltB64: string;
  ivB64: string;
  ctB64: string;
  createdAt: number;
};

export async function encryptJsonToBlob(json: unknown, passphrase: string): Promise<EncryptedBlobV1> {
  if (!passphrase || passphrase.length < 8) {
    throw new Error("Passphrase too short (min 8 chars)");
  }

  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const iterations = 210_000;

  const key = await deriveKey(passphrase, salt, iterations);

  const plaintext = utf8Bytes(JSON.stringify(json));
  const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv: iv as unknown as BufferSource }, key, plaintext);

  return {
    v: 1,
    alg: "AES-GCM",
    kdf: "PBKDF2-SHA256",
    iterations,
    saltB64: bytesToBase64(salt),
    ivB64: bytesToBase64(iv),
    ctB64: bytesToBase64(new Uint8Array(ct)),
    createdAt: Date.now(),
  };
}

export async function decryptBlobToJson(blob: EncryptedBlobV1, passphrase: string): Promise<any> {
  if (!blob || blob.v !== 1) throw new Error("Unsupported vault blob version");
  if (!passphrase) throw new Error("Passphrase required");

  const salt = base64ToBytes(blob.saltB64);
  const iv = base64ToBytes(blob.ivB64);
  const ct = base64ToBytes(blob.ctB64);

  const key = await deriveKey(passphrase, salt, blob.iterations);
  const pt = await crypto.subtle.decrypt({ name: "AES-GCM", iv: iv as unknown as BufferSource }, key, ct);

  const decoded = new TextDecoder().decode(new Uint8Array(pt));
  return JSON.parse(decoded);
}

export function downloadTextFile(filename: string, content: string) {
  const blob = new Blob([content], { type: "application/octet-stream" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
}

export async function readFileAsText(file: File): Promise<string> {
  return await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.onload = () => resolve(String(reader.result || ""));
    reader.readAsText(file);
  });
}
