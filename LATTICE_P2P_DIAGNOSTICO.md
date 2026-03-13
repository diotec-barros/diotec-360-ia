# 🔍 DIAGNÓSTICO LATTICE P2P - PROBLEMA IDENTIFICADO

## ❌ PROBLEMA

O `peer_id` retorna `null` porque **o P2P não está sendo inicializado**.

### Evidência nos Logs

```
# logs/nodeA.log - SEM mensagens [LATTICE_P2P]
INFO:     Started server process [12196]
INFO:     Application startup complete.
[MERKLE DB] Initialized at: ...
[VAULT DB] Initialized at: ...
[AUDITOR] Initialized at: ...
# ❌ FALTA: [LATTICE_P2P] started
# ❌ FALTA: [LATTICE_P2P] peer_id=...
```

Se o P2P estivesse funcionando, veríamos:
```
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
[LATTICE_P2P] listen=/ip4/127.0.0.1/tcp/9000
```

---

## 🔎 CAUSA RAIZ

O `.bat` define as variáveis de ambiente **ANTES** de iniciar o processo:

```bat
set DIOTEC360_P2P_ENABLED=true
set DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
start "Diotec360 Node A" cmd /c "python -m uvicorn api.main:app ..."
```

**MAS** o `start` cria um novo processo CMD que **NÃO herda** as variáveis de ambiente do processo pai no Windows.

---

## ✅ SOLUÇÃO

### Opção 1: Usar arquivo `.env` (RECOMENDADO)

O Python pode ler variáveis de um arquivo `.env` usando `python-dotenv`.

**Passo 1:** Criar `.env.nodeA` e `.env.nodeB`

**`.env.nodeA`:**
```env
DIOTEC360_P2P_ENABLED=true
DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
DIOTEC360_P2P_TOPIC=aethel/lattice/v1
DIOTEC360_P2P_BOOTSTRAP=
DIOTEC360_LATTICE_NODES=
DIOTEC360_STATE_DIR=.DIOTEC360_state_nodeA
DIOTEC360_VAULT_DIR=.DIOTEC360_vault_nodeA
DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel_nodeA
```

**`.env.nodeB`:**
```env
DIOTEC360_P2P_ENABLED=true
DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9001
DIOTEC360_P2P_TOPIC=aethel/lattice/v1
DIOTEC360_P2P_BOOTSTRAP=/ip4/127.0.0.1/tcp/9000/p2p/{PEER_ID_DO_NODE_A}
DIOTEC360_LATTICE_NODES=http://127.0.0.1:8000
DIOTEC360_STATE_DIR=.DIOTEC360_state_nodeB
DIOTEC360_VAULT_DIR=.DIOTEC360_vault_nodeB
DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel_nodeB
```

**Passo 2:** Modificar `api/main.py` para carregar `.env`

```python
from dotenv import load_dotenv
import os

# Carregar .env se existir
load_dotenv()
```

**Passo 3:** Modificar `.bat` para usar `--env-file`

```bat
start "Diotec360 Node A" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --env-file .env.nodeA > logs\nodeA.log 2>&1"
```

---

### Opção 2: Passar variáveis inline (ALTERNATIVA)

Usar `set` dentro do mesmo comando:

```bat
start "Diotec360 Node A" cmd /c "set DIOTEC360_P2P_ENABLED=true && set DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000 && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 > logs\nodeA.log 2>&1"
```

**Problema:** Linha muito longa e difícil de manter.

---

### Opção 3: Script Python wrapper (MAIS LIMPO)

Criar `start_node.py`:

```python
import os
import sys
import subprocess

def start_node(port, p2p_port, bootstrap=None):
    env = os.environ.copy()
    env['DIOTEC360_P2P_ENABLED'] = 'true'
    env['DIOTEC360_P2P_LISTEN'] = f'/ip4/127.0.0.1/tcp/{p2p_port}'
    env['DIOTEC360_P2P_TOPIC'] = 'aethel/lattice/v1'
    env['DIOTEC360_P2P_BOOTSTRAP'] = bootstrap or ''
    env['DIOTEC360_STATE_DIR'] = f'.DIOTEC360_state_node{port}'
    env['DIOTEC360_VAULT_DIR'] = f'.DIOTEC360_vault_node{port}'
    env['DIOTEC360_SENTINEL_DIR'] = f'.DIOTEC360_sentinel_node{port}'
    
    subprocess.run([
        'python', '-m', 'uvicorn', 'api.main:app',
        '--host', '127.0.0.1',
        '--port', str(port)
    ], env=env)

if __name__ == '__main__':
    port = int(sys.argv[1])
    p2p_port = int(sys.argv[2])
    bootstrap = sys.argv[3] if len(sys.argv) > 3 else None
    start_node(port, p2p_port, bootstrap)
```

Usar no `.bat`:
```bat
start "Diotec360 Node A" python start_node.py 8000 9000
```

---

## 🎯 RECOMENDAÇÃO FINAL

**Use a Opção 1 (arquivo `.env`)** porque:
- ✅ Mais limpo e organizado
- ✅ Fácil de editar e versionar
- ✅ Padrão da indústria
- ✅ `python-dotenv` já está instalado

---

## 📝 PRÓXIMOS PASSOS

1. Criar `.env.nodeA` e `.env.nodeB`
2. Modificar `api/main.py` para carregar `.env`
3. Testar com um único nó primeiro
4. Verificar logs para `[LATTICE_P2P] started`
5. Depois iniciar o segundo nó

---

## 🧪 TESTE RÁPIDO

Para testar se o P2P está funcionando:

```cmd
# Terminal 1 - Node A
set DIOTEC360_P2P_ENABLED=true
set DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
set DIOTEC360_STATE_DIR=.DIOTEC360_state_nodeA
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Você deve ver nos logs:
```
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmXXX...
```

Se não ver, o problema está no código Python, não no `.bat`.
