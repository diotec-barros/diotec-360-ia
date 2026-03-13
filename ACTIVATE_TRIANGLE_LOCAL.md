# 🏛️ ATIVAR TRIÂNGULO COMPLETO - SIMULAÇÃO LOCAL

## Objetivo
Ativar os 3 nós localmente para testar o Triângulo da Verdade antes do deploy em produção.

---

## 🚀 ATIVAÇÃO RÁPIDA (3 Terminais)

### Terminal 1: Node 2 (Primary - Porta 8000)
```bash
# JÁ ESTÁ RODANDO! ✅
# Se não estiver, executar:
activate_node2_http.bat
```

### Terminal 2: Node 1 (Hugging Face Sim - Porta 8001)
```bash
activate_node1_local.bat
```

### Terminal 3: Node 3 (Backup Sim - Porta 8002)
```bash
activate_node3_local.bat
```

---

## ✅ VALIDAÇÃO

### Passo 1: Verificar Health de Todos
```bash
# Node 1
curl http://localhost:8001/health

# Node 2
curl http://localhost:8000/health

# Node 3
curl http://localhost:8002/health

# Todos devem retornar: {"status":"healthy"}
```

### Passo 2: Verificar Merkle Roots
```bash
# Node 1
curl http://localhost:8001/api/lattice/state

# Node 2
curl http://localhost:8000/api/lattice/state

# Node 3
curl http://localhost:8002/api/lattice/state

# Verificar se merkle_root é o mesmo em todos!
```

### Passo 3: Executar Teste de Conectividade
```bash
# Editar scripts/test_lattice_connectivity.py
# Mudar URLs para:
# - http://localhost:8000
# - http://localhost:8001
# - http://localhost:8002

python scripts/test_lattice_connectivity.py
```

---

## 📊 RESULTADO ESPERADO

```
========================================
DIOTEC360 LATTICE CONNECTIVITY TEST
========================================

Testing Node 1: http://localhost:8001
[✓] Health check passed
[✓] Merkle Root: 5df3daee3a0ca23c388a16c3db2c2388...

Testing Node 2: http://localhost:8000
[✓] Health check passed
[✓] Merkle Root: 5df3daee3a0ca23c388a16c3db2c2388...

Testing Node 3: http://localhost:8002
[✓] Health check passed
[✓] Merkle Root: 5df3daee3a0ca23c388a16c3db2c2388...

========================================
[SUCCESS] Real Lattice is fully operational!
========================================
Health:        3/3 nodes healthy
HTTP Sync:     3/3 nodes capable
State Sync:    CONSISTENT
Merkle Root:   IDENTICAL across all nodes
========================================
```

---

## 🎯 APÓS VALIDAÇÃO LOCAL

1. ✅ Triângulo local funcionando
2. ✅ Merkle Roots consistentes
3. ✅ HTTP Sync operacional
4. 🚀 Pronto para deploy em produção!

---

**"Três nós locais, uma verdade matemática. O Triângulo respira."**

🏛️⚡📡🔗🛡️👑🌌✨

