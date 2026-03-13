# PRODUCTION_HARDENING_SUITE

## Objective

Hardening checklist to ensure Aethel runs with real integrations (no demo keys / no sandbox / no in-memory-only fallbacks) when operating in production.

## Environments

Aethel uses a simple environment switch:

- `DIOTEC360_ENV=production` enables production hardening rules.
- `DIOTEC360_ENV=development` (or unset) keeps developer-friendly defaults.

## Required Environment Variables (Production)

### Core mode

- `DIOTEC360_ENV`
  - **production** | development

- `DIOTEC360_SAFE_MODE`
  - Optional.
  - When set to `1`, components should disable risky external actions.

### CORS / API Exposure (Backend)

- `DIOTEC360_CORS_ORIGINS`
  - Comma-separated list of allowed origins.
  - Example:
    - `https://studio.diotec360.com,https://admin.diotec360.com`
  - **Production rule**: must not be `*` and must not be empty.

### P2P / Lattice (Backend)

- `DIOTEC360_P2P_ENABLED`
  - `1` | `0`

- `DIOTEC360_P2P_LISTEN`
  - Comma-separated multiaddrs.
  - Example:
    - `/ip4/0.0.0.0/tcp/9000`

- `DIOTEC360_P2P_BOOTSTRAP`
  - Comma-separated multiaddrs (neighbors).
  - Example:
    - `/ip4/203.0.113.10/tcp/9000/p2p/12D3KooW...,...`
  - **Production rule**: if `DIOTEC360_P2P_ENABLED=1`, bootstrap list must be non-empty.

- `DIOTEC360_P2P_TOPIC`
  - Optional.
  - Default: `aethel/lattice/v1`

### Lattice HTTP fallback (Backend)

- `DIOTEC360_LATTICE_NODES`
  - Optional in dev.
  - Comma-separated URLs used by HTTP sync fallback.

- `DIOTEC360_TRUSTED_STATE_PUBKEYS`
  - Comma-separated ED25519 public keys (hex) that are allowed to sign state reconciliations.
  - **Strongly recommended in production**.

- `DIOTEC360_NODE_PRIVKEY_HEX`
  - ED25519 private key (hex) used to sign this node’s state.

### Forex / Oracles

- `ALPHA_VANTAGE_API_KEY`
  - **Production rule**: must be set and must not equal `demo`.

- `POLYGON_API_KEY`
  - Optional (but recommended for redundancy).

- `DIOTEC360_TEST_MODE`
  - `1` forces test quotes (no real network).
  - **Production rule**: must be unset / false.

- `DIOTEC360_OFFLINE`
  - `1` forces offline behavior.
  - **Production rule**: must be unset / false.

### Payments

#### PayPal

- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_SANDBOX`
  - `1` | `0`
  - **Production rule**: must be `0`.

#### Multicaixa Express

- `MULTICAIXA_MERCHANT_ID`
- `MULTICAIXA_API_KEY`
- `MULTICAIXA_SANDBOX`
  - `1` | `0`
  - **Production rule**: must be `0`.

### Gun / Agent Registry (Frontend)

- `NEXT_PUBLIC_GUN_PEERS`
  - Comma-separated peer URLs.
  - **Production rule**: should be non-empty to prevent in-memory-only registry.

## How to switch sandbox to live

### PayPal

Set:

- `PAYPAL_SANDBOX=0`

and use live credentials:

- `PAYPAL_CLIENT_ID=...`
- `PAYPAL_CLIENT_SECRET=...`

### Multicaixa Express

Set:

- `MULTICAIXA_SANDBOX=0`

and use live credentials:

- `MULTICAIXA_MERCHANT_ID=...`
- `MULTICAIXA_API_KEY=...`

## Hardening Smoke Tests

### Backend boot integrity

- Start the API with `DIOTEC360_ENV=production`.
- Expected: startup runs `env_guard` checks.
- Expected: if any production violation is detected, Safe Mode is enabled (`DIOTEC360_SAFE_MODE=1`) and a report is printed.

### Forex live quote

- Set `ALPHA_VANTAGE_API_KEY` to a real key.
- Run a quote retrieval from `RealForexOracle`.
- Expected: quote provider is not `test_mode`, and API does not rate-limit immediately.

### Payments live endpoints

- Set `PAYPAL_SANDBOX=0` and live credentials.
- Create order.
- Expected: base URL is `https://api-m.paypal.com`.

### P2P neighbors

- Set `DIOTEC360_P2P_ENABLED=1` and a non-empty `DIOTEC360_P2P_BOOTSTRAP`.
- Start two nodes.
- Expected: peer count becomes > 0.

### Frontend local judge arithmetic

- Add constraints with arithmetic, e.g.:
  - `balance_after == balance_before + amount;`
  - `amount * 2 <= limit;`
- Expected: local judge returns `PROVED` when constraints are satisfiable.
