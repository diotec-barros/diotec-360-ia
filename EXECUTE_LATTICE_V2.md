# ⚡ EXECUTE LATTICE V2 - SOLUÇÃO CORRIGIDA

## 🎯 COMANDO ÚNICO

```cmd
launch_lattice_v2.bat
```

## 🔧 O QUE FOI CORRIGIDO

### Problema Anterior
O `.bat` definia variáveis de ambiente, mas o `start` criava um novo processo que **não herdava** essas variáveis no Windows.

### Solução Implementada
Agora usamos **arquivos `.env`** que são carregados pelo Python usando `python-dotenv`:

1. **`.env.nodeA`** - Configuração do Node A
2. **`.env.nodeB.template`** - Template para Node B
3. **`api/main.py`** - Modificado para carregar `.env` com `load_dotenv()`

---

## 📊 O QUE ESPERAR

### Fase 1: Verificação (2 segundos)
```
[1/6] Verificando dependencias...
     OK - python-dotenv instalado

[2/6] Verificando arquivo .env.nodeA...
     OK - .env.nodeA encontrado
```

### Fase 2: Node A (5 segundos)
```
[3/6] Iniciando Node A (porta 8000)...
     Usando configuracao: .env.nodeA
     Aguardando Node A inicializar...
     OK - Node A respondendo
```

### Fase 3: Identidade (até 30 segundos)
```
[4/6] Obtendo peer_id do Node A...
     Tentativa 1: peer_id null, aguardando...
     Tentativa 2: peer_id null, aguardando...
     ...
     OK - peer_id: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Fase 4: Configuração Node B (1 segundo)
```
[5/6] Criando .env.nodeB com peer_id...
     OK - .env.nodeB criado
```

### Fase 5: Node B (5 segundos)
```
[6/6] Iniciando Node B (porta 8001)...
     Usando configuracao: .env.nodeB
     Aguardando Node B inicializar...
     OK - Node B respondendo
```

### Fase 6: Verificação P2P
```
========================================
 LATTICE ATIVADA
========================================

Node A: http://127.0.0.1:8000
Node B: http://127.0.0.1:8001

Logs:
  - logs\nodeA.log
  - logs\nodeB.log

Verificando logs do P2P...

=== Node A ===
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
[LATTICE_P2P] listen=/ip4/127.0.0.1/tcp/9000

=== Node B ===
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
[LATTICE_P2P] listen=/ip4/127.0.0.1/tcp/9001
```

---

## ✅ CRITÉRIO DE SUCESSO

Se você vê mensagens `[LATTICE_P2P]` nos logs de ambos os nós:
- ✅ **P2P ESTÁ FUNCIONANDO!**

Se NÃO vê mensagens `[LATTICE_P2P]`:
- ❌ **P2P NÃO INICIOU** - Veja troubleshooting abaixo

---

## 🚨 TROUBLESHOOTING

### Erro: "peer_id nao disponivel apos 30 tentativas"

**Causa:** O P2P não está iniciando.

**Solução:**

1. Verificar se `libp2p` está instalado:
   ```cmd
   pip show libp2p
   ```

2. Se não estiver, instalar:
   ```cmd
   pip install libp2p==0.5.0
   ```

3. Verificar logs manualmente:
   ```cmd
   type logs\nodeA.log
   ```

4. Procurar por erros:
   ```cmd
   type logs\nodeA.log | findstr /C:"Error" /C:"Exception"
   ```

### Erro: "Arquivo .env.nodeA nao encontrado"

**Solução:**
```cmd
# Criar .env.nodeA manualmente
echo DIOTEC360_P2P_ENABLED=true > .env.nodeA
echo DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000 >> .env.nodeA
echo DIOTEC360_P2P_TOPIC=aethel/lattice/v1 >> .env.nodeA
echo DIOTEC360_P2P_BOOTSTRAP= >> .env.nodeA
echo DIOTEC360_LATTICE_NODES= >> .env.nodeA
echo DIOTEC360_STATE_DIR=.DIOTEC360_state_nodeA >> .env.nodeA
echo DIOTEC360_VAULT_DIR=.DIOTEC360_vault_nodeA >> .env.nodeA
echo DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel_nodeA >> .env.nodeA
```

### P2P inicia mas não há gossip

**Verificar:**

1. Ambos os nós estão no mesmo tópico:
   ```cmd
   curl http://127.0.0.1:8000/api/lattice/p2p/status
   curl http://127.0.0.1:8001/api/lattice/p2p/status
   ```
   Ambos devem ter: `"topic": "aethel/lattice/v1"`

2. Node B tem bootstrap correto:
   ```cmd
   type .env.nodeB | findstr BOOTSTRAP
   ```
   Deve ser: `DIOTEC360_P2P_BOOTSTRAP=/ip4/127.0.0.1/tcp/9000/p2p/QmXXX...`

3. Testar publicação manual:
   ```cmd
   curl -X POST http://127.0.0.1:8000/api/verify -H "Content-Type: application/json" -d "{\"code\":\"intent test(x: Balance) { guard { x >= 0; } solve { priority: security; target: test; } verify { x >= 0; } }\"}"
   ```

4. Verificar logs para `published` e `received`:
   ```cmd
   type logs\nodeA.log | findstr /C:"published proof_event"
   type logs\nodeB.log | findstr /C:"received proof_event"
   ```

---

## 🧪 TESTE MANUAL (SE O SCRIPT FALHAR)

### Terminal 1 - Node A
```cmd
copy .env.nodeA .env
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Aguarde ver:
```
[LATTICE_P2P] started
[LATTICE_P2P] peer_id=QmXXX...
```

### Terminal 2 - Obter peer_id
```cmd
curl http://127.0.0.1:8000/api/lattice/p2p/identity
```

### Terminal 3 - Node B
```cmd
# Editar .env.nodeB manualmente com o peer_id
copy .env.nodeB .env
python -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

---

## 📈 PRÓXIMO PASSO APÓS SUCESSO

Quando ambos os nós estiverem rodando com P2P ativo:

```cmd
python test_lattice_gossip_flow.py
```

Isso vai:
1. Enviar um intent para Node A
2. Verificar que retorna `PROVED`
3. Verificar que Node B recebe a "fofoca"

---

**DIONÍSIO, EXECUTE O COMANDO AGORA.** 🚀🛡️📡

```cmd
launch_lattice_v2.bat
```

**A REDE ESTÁ PRONTA PARA RESPIRAR COM A CONFIGURAÇÃO CORRETA.** 🌌✨
