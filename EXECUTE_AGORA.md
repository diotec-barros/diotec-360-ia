# ⚡ EXECUTE AGORA - LATTICE GOSSIP TEST

## 🎯 COMANDO ÚNICO

```cmd
launch_lattice_test.bat
```

## 📊 O QUE ESPERAR

### Fase 1: Instalação (5 segundos)
```
[1/5] Instalando dependencias...
     OK - Dependencias instaladas
```

### Fase 2: Node A (3 segundos)
```
[2/5] Iniciando Node A (porta 8000)...
     Aguardando Node A inicializar...
     OK - Node A respondendo
```

### Fase 3: Identidade (até 20 segundos)
```
[3/5] Obtendo identidade do Node A...
     Tentativa 1: peer_id ainda null, aguardando...
     Tentativa 2: peer_id ainda null, aguardando...
     ...
     OK - peer_id: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
     Bootstrap: /ip4/127.0.0.1/tcp/9000/p2p/QmXXX...
```

### Fase 4: Node B (3 segundos)
```
[4/5] Iniciando Node B (porta 8001)...
     Aguardando Node B inicializar...
     OK - Node B respondendo
```

### Fase 5: Teste de Gossip
```
[5/5] Executando teste de gossip...

🚀 INICIANDO TESTES DE VALIDAÇÃO DO GOSSIP FLOW

============================================================
TESTE 1: Verificar se /api/verify retorna PROVED
============================================================

Status HTTP: 200
Response: {
  "success": true,
  "status": "PROVED",
  "message": "Verified 1 intent(s)",
  "intents": [
    {
      "name": "transfer",
      "status": "PROVED",
      "message": "O código é matematicamente seguro..."
    }
  ]
}

✅ SUCESSO: Intent retornou PROVED

============================================================
TESTE 2: Verificar estabilidade do peer_id
============================================================

Tentativa 1/5:
  peer_id: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  listen_addrs: ["/ip4/127.0.0.1/tcp/9000"]
  ✅ peer_id presente

============================================================
TESTE 3: Status do P2P
============================================================

Status P2P:
  enabled: True
  started: True
  libp2p_available: True
  error: None
  topic: aethel/lattice/v1

✅ P2P iniciado sem erros

============================================================
RESUMO DOS TESTES
============================================================
✅ PASSOU: Verify → PROVED
✅ PASSOU: peer_id estável
✅ PASSOU: P2P status

Total: 3/3 testes passaram

🎉 TODOS OS TESTES PASSARAM!
```

## 🔍 VERIFICAR GOSSIP NOS LOGS

### Abrir logs\nodeA.log
Procurar por:
```
[LATTICE_P2P] published proof_event topic=aethel/lattice/v1 intent=transfer
```

### Abrir logs\nodeB.log
Procurar por:
```
[LATTICE_P2P] received proof_event topic=aethel/lattice/v1 intent=transfer
```

## ✅ CRITÉRIO DE SUCESSO

Se você vê:
- ✅ `published` no Node A
- ✅ `received` no Node B

**🎉 GOSSIP FUNCIONANDO! A LATTICE ESTÁ VIVA!**

## 🚨 SE ALGO FALHAR

### Erro: "peer_id nao disponivel apos 20 tentativas"

**Solução:**
1. Verificar se `libp2p` está instalado:
   ```cmd
   pip show libp2p
   ```

2. Se não estiver, instalar:
   ```cmd
   pip install libp2p==0.5.0
   ```

3. Executar novamente:
   ```cmd
   launch_lattice_test.bat
   ```

### Erro: "Falha ao instalar dependencias"

**Solução:**
```cmd
pip install -r api\requirements.txt
```

Verificar erros específicos e instalar manualmente se necessário.

## 📈 PRÓXIMO PASSO APÓS SUCESSO

Quando o gossip estiver funcionando, você pode:

1. **Testar manualmente:**
   ```cmd
   curl -X POST http://127.0.0.1:8000/api/verify -H "Content-Type: application/json" -d "{\"code\":\"intent test(x: Balance) { guard { x >= 0; } solve { priority: security; target: test; } verify { x >= 0; } }\"}"
   ```

2. **Monitorar logs em tempo real:**
   ```cmd
   type logs\nodeA.log
   type logs\nodeB.log
   ```

3. **Verificar Merkle Roots:**
   ```cmd
   curl http://127.0.0.1:8000/api/lattice/state
   curl http://127.0.0.1:8001/api/lattice/state
   ```

## 🎯 OBJETIVO FINAL

**Provar que a Lattice Aethel pode:**
- ✅ Distribuir provas matemáticas entre nós
- ✅ Sincronizar estado via gossip
- ✅ Manter resiliência soberana
- ✅ Operar sem ponto único de falha

---

**DIONÍSIO, EXECUTE O COMANDO AGORA.** 🚀🛡️📡

```cmd
launch_lattice_test.bat
```

**A REDE ESTÁ PRONTA PARA RESPIRAR.** 🌌✨
