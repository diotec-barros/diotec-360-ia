# 📡 DIOTEC360_P2P_BOOTSTRAP - O QUE COLOCAR?

**Data:** 2026-02-12  
**Contexto:** Triangle of Truth - HTTP-Only Resilience Mode

---

## 🎯 RESPOSTA RÁPIDA

**Para a arquitetura atual (HTTP-Only):**

```env
DIOTEC360_P2P_BOOTSTRAP=
```

**Deixe VAZIO!** ✅

---

## 🤔 POR QUÊ VAZIO?

A arquitetura atual do Triangle of Truth usa **HTTP-Only Resilience Mode**, onde:

- ✅ `DIOTEC360_P2P_ENABLED=false` (P2P desabilitado)
- ✅ `DIOTEC360_LATTICE_NODES` (HTTP sync entre nós)
- ✅ `DIOTEC360_P2P_BOOTSTRAP=` (vazio, não usado)

**O P2P está desabilitado por design**, então não precisamos de bootstrap peers.

---

## 📚 O QUE É DIOTEC360_P2P_BOOTSTRAP?

`DIOTEC360_P2P_BOOTSTRAP` é uma lista de **endereços P2P de nós iniciais** que um novo nó usa para se conectar à rede P2P.

### Formato (quando P2P está habilitado):

```env
DIOTEC360_P2P_BOOTSTRAP=/ip4/192.168.1.100/tcp/9000/p2p/12D3KooWABC123...,/ip4/10.0.0.50/tcp/9000/p2p/12D3KooWXYZ789...
```

**Componentes:**
- `/ip4/192.168.1.100` - Endereço IP do nó
- `/tcp/9000` - Porta TCP do P2P
- `/p2p/12D3KooWABC123...` - Peer ID (identificador único do nó)

---

## 🔺 ARQUITETURA ATUAL: HTTP-ONLY

```
┌─────────────────────────────────────────────────────────┐
│         TRIANGLE OF TRUTH - HTTP-ONLY MODE              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔵 Node 2: api.diotec360.com                          │
│     DIOTEC360_P2P_ENABLED=false                           │
│     DIOTEC360_P2P_BOOTSTRAP=                              │
│     DIOTEC360_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com │
│                                                         │
│  🟢 Node 1: diotec-diotec360-judge.hf.space              │
│     DIOTEC360_P2P_ENABLED=false                           │
│     DIOTEC360_P2P_BOOTSTRAP=                              │
│     DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://backup.diotec360.com │
│                                                         │
│  🟣 Node 3: backup.diotec360.com                       │
│     DIOTEC360_P2P_ENABLED=false                           │
│     DIOTEC360_P2P_BOOTSTRAP=                              │
│     DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://diotec-diotec360-judge.hf.space │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Sincronização:** HTTP Sync via `DIOTEC360_LATTICE_NODES`  
**P2P:** Desabilitado (não precisa de bootstrap)

---

## 🚀 QUANDO USAR DIOTEC360_P2P_BOOTSTRAP?

### Cenário 1: P2P Habilitado (Futuro)

Se você habilitar P2P no futuro:

```env
# Node 2 (Primary)
DIOTEC360_P2P_ENABLED=true
DIOTEC360_P2P_LISTEN=/ip4/0.0.0.0/tcp/9000
DIOTEC360_P2P_BOOTSTRAP=/ip4/node1.example.com/tcp/9001/p2p/12D3KooWNode1ABC,/ip4/node3.example.com/tcp/9002/p2p/12D3KooWNode3XYZ
```

**Aqui você precisa:**
1. Obter o Peer ID de cada nó (gerado automaticamente)
2. Adicionar os endereços completos dos outros nós

---

### Cenário 2: Rede P2P Pública

Se você quiser que novos nós se conectem à sua rede:

```env
# Novo nó se conectando à rede existente
DIOTEC360_P2P_ENABLED=true
DIOTEC360_P2P_BOOTSTRAP=/ip4/api.diotec360.com/tcp/9000/p2p/12D3KooWPrimaryNode,/ip4/backup.diotec360.com/tcp/9002/p2p/12D3KooWBackupNode
```

---

## 🔧 COMO OBTER PEER IDs?

Se você habilitar P2P no futuro, cada nó gera um Peer ID automaticamente.

### Método 1: Endpoint de Status

```bash
curl http://localhost:8000/api/lattice/p2p/status
```

**Resposta:**
```json
{
  "peer_id": "12D3KooWABC123...",
  "listen_addresses": ["/ip4/0.0.0.0/tcp/9000"],
  "connected_peers": []
}
```

### Método 2: Logs do Servidor

Quando o nó inicia com P2P habilitado:

```
INFO: P2P Node started with Peer ID: 12D3KooWABC123...
INFO: Listening on: /ip4/0.0.0.0/tcp/9000
```

---

## 📋 CONFIGURAÇÃO ATUAL (PRODUCTION)

### Node 2 (api.diotec360.com)

```env
# P2P Configuration - DISABLED
DIOTEC360_P2P_ENABLED=false
DIOTEC360_P2P_LISTEN=/ip4/0.0.0.0/tcp/9000
DIOTEC360_P2P_TOPIC=aethel/lattice/v1
DIOTEC360_P2P_BOOTSTRAP=

# HTTP Sync (ATIVO)
DIOTEC360_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com
```

### Node 1 (Hugging Face)

```env
# P2P Configuration - DISABLED
DIOTEC360_P2P_ENABLED=false
DIOTEC360_P2P_BOOTSTRAP=

# HTTP Sync (ATIVO)
DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://backup.diotec360.com
```

### Node 3 (Backup)

```env
# P2P Configuration - DISABLED
DIOTEC360_P2P_ENABLED=false
DIOTEC360_P2P_BOOTSTRAP=

# HTTP Sync (ATIVO)
DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://diotec-diotec360-judge.hf.space
```

---

## 🎯 RESUMO EXECUTIVO

| Variável | Valor Atual | Quando Usar |
|----------|-------------|-------------|
| `DIOTEC360_P2P_ENABLED` | `false` | HTTP-Only mode (atual) |
| `DIOTEC360_P2P_BOOTSTRAP` | `` (vazio) | P2P desabilitado |
| `DIOTEC360_LATTICE_NODES` | URLs HTTP | Sincronização ativa |

**Para a arquitetura atual:**
- ✅ Deixe `DIOTEC360_P2P_BOOTSTRAP` vazio
- ✅ Use `DIOTEC360_LATTICE_NODES` para sincronização
- ✅ P2P permanece desabilitado

**Para habilitar P2P no futuro:**
1. Mude `DIOTEC360_P2P_ENABLED=true`
2. Obtenha os Peer IDs de cada nó
3. Configure `DIOTEC360_P2P_BOOTSTRAP` com os endereços completos

---

## 🏛️ FILOSOFIA DA ARQUITETURA

**HTTP-Only Resilience Mode** foi escolhido porque:

1. **Simplicidade:** HTTP funciona em qualquer lugar
2. **Confiabilidade:** Atravessa firewalls e proxies
3. **Monitoramento:** Ferramentas HTTP padrão funcionam
4. **Debugging:** Padrões request/response claros

**P2P permanece no roadmap** como "camada de camuflagem" opcional para adicionar resiliência extra no futuro.

---

## 📝 CHECKLIST

- [x] `DIOTEC360_P2P_ENABLED=false` em todos os nós
- [x] `DIOTEC360_P2P_BOOTSTRAP=` (vazio) em todos os nós
- [x] `DIOTEC360_LATTICE_NODES` configurado com URLs HTTP
- [x] HTTP Sync operacional
- [x] Triangle sincronizado (Merkle Root: 5df3daee...)

---

**🔺 TRIANGLE OF TRUTH - HTTP-ONLY RESILIENCE 🔺**

**P2P Bootstrap não é necessário na arquitetura atual!**

**🏛️⚖️✨**
