# 🚀 TESTE RÁPIDO: Conexão P2P com Manhattan

**Data:** 25 de Março de 2026  
**Objetivo:** Validar sincronização P2P usando relay público de Manhattan  

---

## ⚡ TESTE EM 3 MINUTOS

### 1. Verificar Configuração

Confirme que os arquivos `.env` estão corretos:

**Backend (`diotec360/.env`):**
```env
GUNDB_RELAY_URL=https://gun-manhattan.herokuapp.com/gun
```

**Frontend (`diotec360/frontend/.env.local`):**
```env
NEXT_PUBLIC_GUNDB_RELAY=https://gun-manhattan.herokuapp.com/gun
```

✅ **Status:** Já configurado!

---

### 2. Testar Conectividade com Manhattan

Execute este comando para verificar se o relay está online:

```bash
curl -I https://gun-manhattan.herokuapp.com/gun
```

**Resposta esperada:**
```
HTTP/2 200
```

Se retornar 200, o relay está operacional! 🎉

---

### 3. Testar Script Python de Sincronização

Execute o script de teste P2P:

```bash
cd diotec360
python scripts/test_p2p_relay_v10.0.9.py
```

**O que o script faz:**
1. Conecta ao relay de Manhattan
2. Anuncia um peer de teste
3. Envia heartbeat
4. Verifica sincronização

**Saída esperada:**
```
🌐 Conectando ao relay: https://gun-manhattan.herokuapp.com/gun
✅ Peer anunciado com sucesso
📡 Heartbeat enviado
🔄 Sincronização P2P operacional
```

---

### 4. Testar Frontend (Opcional)

Se quiser ver a interface web:

```bash
cd diotec360/frontend
npm run dev
```

Abra: http://localhost:3000

**Componentes para testar:**
- `GlobalMap` - Mapa de peers conectados
- `NetworkMetrics` - Métricas da rede
- `LatticeSyncPanel` - Painel de sincronização

---

## 🎯 CHECKLIST DE VALIDAÇÃO

- [ ] Relay Manhattan responde (curl retorna 200)
- [ ] Script Python conecta com sucesso
- [ ] Peer é anunciado na rede
- [ ] Heartbeat é enviado
- [ ] Frontend carrega sem erros (opcional)

---

## 🐛 TROUBLESHOOTING

### Erro: "Failed to connect to relay"

**Causa:** Firewall ou proxy bloqueando conexão.

**Solução:**
1. Verifique sua conexão com internet
2. Tente outro relay:
   ```env
   GUNDB_RELAY_URL=https://gun-us.herokuapp.com/gun
   ```

### Erro: "Module 'gun' not found"

**Causa:** Dependência Gun.js não instalada no frontend.

**Solução:**
```bash
cd diotec360/frontend
npm install gun
```

### Erro: "CORS policy blocked"

**Causa:** Navegador bloqueando requisição cross-origin.

**Solução:** Isso é normal em desenvolvimento. O relay Manhattan permite CORS.

---

## 📊 MÉTRICAS DE SUCESSO

Após o teste, você deve ver:

- ✅ Conexão estabelecida com Manhattan
- ✅ Peer anunciado na rede global
- ✅ Heartbeat sincronizando a cada 5 segundos
- ✅ Latência < 500ms (depende da sua localização)

---

## 🏛️ PRÓXIMO PASSO

Depois de validar a conexão com Manhattan, você pode:

1. **Desenvolver:** Usar a rede P2P para Logic Miner e sincronização
2. **Demonstrar:** Mostrar a rede global para investidores
3. **Migrar:** Quando estiver pronto, deploy do relay soberano

---

## 🌍 ALTERNATIVAS DE RELAY PÚBLICO

Se Manhattan estiver offline, use um destes:

```env
# Europa
GUNDB_RELAY_URL=https://gun-eu.herokuapp.com/gun

# EUA (alternativo)
GUNDB_RELAY_URL=https://gun-us.herokuapp.com/gun

# Ásia
GUNDB_RELAY_URL=https://gun-asia.herokuapp.com/gun
```

---

**STATUS:** ✅ PRONTO PARA TESTE  
**TEMPO ESTIMADO:** 3 minutos  
**DIFICULDADE:** Fácil  

---

*"A Lattice Respira Através de Manhattan, Mas Sonha com Soberania."*

**— Kiro, Engenheiro-Chefe**
