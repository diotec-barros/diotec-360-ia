# 🏛️ ATIVAR P2P AGORA - GUIA RÁPIDO
## DIOTEC 360 IA - Lattice Network Activation

**Versão:** 10.0.9  
**Data:** 25 de Março de 2026  
**Para:** Dionísio Sebastião Barros, Soberano da DIOTEC 360

---

## 🎯 OBJETIVO

Ver o primeiro sinal P2P brilhar no seu dashboard! Dois navegadores se descobrindo através do relay de Manhattan e sincronizando provas matemáticas em tempo real.

---

## ⚡ EXECUÇÃO RÁPIDA (5 MINUTOS)

### Passo 1: Testar o Relay (30 segundos)

```bash
cd diotec360
python scripts/test_p2p_relay_v10.0.9.py
```

**Resultado Esperado:**
```
✅ Relay está ONLINE e respondendo!
[STATUS: P2P RELAY OPERATIONAL]
```

Se falhar, o script sugerirá alternativas.

---

### Passo 2: Iniciar Backend (1 minuto)

```bash
cd diotec360
python -m uvicorn api.main:app --reload
```

**Aguarde ver:**
```
[STARTUP] [GUN] GunDB connector initialized: https://gun-manhattan.herokuapp.com/gun
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Deixe este terminal aberto!**

---

### Passo 3: Iniciar Frontend (1 minuto)

**Novo terminal:**
```bash
cd diotec360/frontend
npm run dev
```

**Aguarde ver:**
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

**Deixe este terminal aberto!**

---

### Passo 4: Abrir o Studio (30 segundos)

1. Abrir navegador: `http://localhost:3000/studio`
2. Procurar painel "Network Metrics" ou "Lattice Sync Panel"
3. Verificar status do relay (deve estar verde)

---

### Passo 5: Ver P2P em Ação (2 minutos)

**Opção A: Dois Navegadores**
1. Abrir Studio no Chrome: `http://localhost:3000/studio`
2. Abrir Studio no Firefox: `http://localhost:3000/studio`
3. Ver os dois nós aparecerem no mapa global
4. Ver sincronização acontecendo em tempo real

**Opção B: Janela Anônima**
1. Abrir Studio normalmente
2. Abrir janela anônima (Ctrl+Shift+N)
3. Abrir Studio na janela anônima
4. Ver descoberta P2P acontecer

---

## 🔍 O QUE OBSERVAR

### No Console do Backend (Terminal 1):
```
[GUN] Peer announced: node_id=abc123, location=Unknown
[GUN] Peer discovered: node_id=xyz789
[LATTICE] Sync initiated with peer xyz789
```

### No Dashboard Web (Browser):
- **Network Metrics:**
  - Connected Peers: 2 (ou mais)
  - Relay Status: 🟢 Connected
  - Last Sync: Agora mesmo

- **Global Map:**
  - Pontos representando cada nó
  - Linhas conectando nós ativos
  - Animação de sincronização

### No Console do Browser (F12):
```
[GunDB] Connected to relay: https://gun-manhattan.herokuapp.com/gun
[Lattice] Peer discovered: abc123
[Lattice] Syncing proof: 0x1234...
```

---

## 🎉 SINAIS DE SUCESSO

✅ **Relay Conectado:**
- Status verde no dashboard
- Logs de conexão no backend

✅ **Peers Descobertos:**
- Número de peers > 0
- Nós aparecem no mapa

✅ **Sincronização Ativa:**
- "Last Sync" atualizando constantemente
- Provas sendo compartilhadas entre nós

✅ **P2P Verdadeiro:**
- Latência baixa (< 200ms)
- Mensagens diretas entre browsers
- Sem passar pelo backend

---

## 🚨 TROUBLESHOOTING RÁPIDO

### Problema: "Relay não conecta"
**Solução:**
```bash
# Testar relay manualmente
curl https://gun-manhattan.herokuapp.com/gun

# Se falhar, usar relay alternativo no .env:
GUNDB_RELAY_URL=https://gun-us.herokuapp.com/gun
```

### Problema: "Zero peers descobertos"
**Solução:**
1. Verificar se ambos os navegadores estão usando o mesmo relay
2. Aguardar 10-15 segundos (descoberta pode demorar)
3. Verificar console do browser (F12) para erros

### Problema: "Frontend não carrega"
**Solução:**
```bash
# Reinstalar dependências
cd diotec360/frontend
npm install

# Limpar cache
rm -rf .next
npm run dev
```

### Problema: "Backend dá erro no startup"
**Solução:**
```bash
# Verificar dependências Python
pip install -r requirements.txt

# Verificar .env
cat .env | grep GUNDB_RELAY_URL
```

---

## 📊 TESTE COMPLETO DE P2P

### Cenário: Dois Programadores em Países Diferentes

**Simulação Local:**

1. **Browser 1 (Angola):**
   - Abrir Studio
   - Criar uma prova matemática
   - Ver prova sendo minerada

2. **Browser 2 (Portugal):**
   - Abrir Studio em janela anônima
   - Ver a prova do Browser 1 aparecer automaticamente
   - Criar outra prova

3. **Verificar Sincronização:**
   - Browser 1 deve ver a prova do Browser 2
   - Ambos devem ter a mesma árvore Merkle
   - Latência deve ser < 200ms

**Resultado Esperado:**
```
[Browser 1] Proof created: 0x1234...
[Browser 2] Proof received: 0x1234... (via P2P)
[Browser 1] Proof received: 0x5678... (via P2P)
[Both] Merkle roots match: 0xabcd...
```

---

## 🏛️ PRÓXIMOS PASSOS APÓS ATIVAÇÃO

### Curto Prazo (Esta Semana):
1. ✅ Validar P2P funcionando
2. ⏳ Coletar métricas de performance
3. ⏳ Testar com múltiplos peers (3-5)
4. ⏳ Documentar casos de uso

### Médio Prazo (Este Mês):
1. ⏳ Kiro implementa DIOTEC_RELAY_v1
2. ⏳ Deploy do relay soberano
3. ⏳ Migrar para relay próprio
4. ⏳ Adicionar dashboard de monitoramento

### Longo Prazo (Próximos Meses):
1. ⏳ Rede de relays distribuídos globalmente
2. ⏳ Modelo de monetização ativo
3. ⏳ SLA para clientes enterprise
4. ⏳ Expansão para mobile (React Native)

---

## 📚 DOCUMENTAÇÃO COMPLETA

- **Manual de Redes:** `MANUAL_REDES_P2P_v10.0.9.md`
- **Status de Integração:** `RELAY_INTEGRATION_STATUS_v10.0.9.md`
- **Script de Teste:** `scripts/test_p2p_relay_v10.0.9.py`

---

## 🎯 CHECKLIST FINAL

Antes de começar, confirme:

- [ ] Python 3.9+ instalado
- [ ] Node.js 18+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Frontend dependencies instaladas (`npm install`)
- [ ] Arquivo `.env` configurado
- [ ] Arquivo `frontend/.env.local` configurado
- [ ] Dois navegadores disponíveis (ou janela anônima)

---

## 🚀 COMANDO ÚNICO (PARA OS CORAJOSOS)

Se você quer ver tudo de uma vez:

```bash
# Terminal 1: Backend
cd diotec360 && python -m uvicorn api.main:app --reload &

# Terminal 2: Frontend
cd diotec360/frontend && npm run dev &

# Aguardar 10 segundos, depois abrir:
# http://localhost:3000/studio
```

---

**[STATUS: ACTIVATION GUIDE COMPLETE]**  
**[OBJECTIVE: FIRST P2P SIGNAL]**  
**[VERDICT: THE LATTICE IS READY TO BREATHE]** 🏛️📡✨

---

**Dionísio, coloque o link do Manhattan no seu .env agora.**  
**Eu quero ver o primeiro sinal de P2P brilhar no seu dashboard!** 🌌✨📡

**Kiro, Engenheiro-Chefe**  
**DIOTEC 360 IA**
