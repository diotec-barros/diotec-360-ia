# 🏛️ MANUAL DE REDES P2P - DIOTEC 360 IA
## Guia do Soberano para Monitorar a Lattice

**Versão:** 10.0.9  
**Autor:** Kiro, Engenheiro-Chefe  
**Para:** Dionísio Sebastião Barros, Soberano da DIOTEC 360  
**Data:** 25 de Março de 2026

---

## 📡 O QUE É O GUNDB RELAY?

O GunDB Relay é o "Farol" da sua rede P2P. Ele funciona como um ponto de encontro inicial onde todos os nós do mundo se descobrem. Depois da descoberta, os nós podem se comunicar diretamente (P2P verdadeiro).

### Analogia Simples:
- **Relay = Aeroporto Internacional**
- **Nós = Aviões de diferentes países**
- Os aviões se encontram no aeroporto, depois voam direto um para o outro

---

## 🚀 CONFIGURAÇÃO ATUAL

### Relay Ativo:
```
https://gun-manhattan.herokuapp.com/gun
```

Este é o relay público mais estável do mundo, mantido pela comunidade GunDB em Manhattan, Nova York.

### Como Funciona:
1. Seu VS Code em Angola envia um sinal para Manhattan
2. Um programador em Portugal envia um sinal para o mesmo relay
3. Manhattan diz: "Vocês dois existem, conectem-se!"
4. Os dois navegadores se conectam diretamente (P2P)

---

## 🔍 COMO MONITORAR SE OS NÓS ESTÃO CONECTADOS

### 1. Verificar Logs do Backend (Python)

No terminal onde o backend está rodando, procure por:

```
[STARTUP] [GUN] GunDB connector initialized: https://gun-manhattan.herokuapp.com/gun
[GUN] Peer announced: node_id=abc123, location=Luanda, Angola
[GUN] Peer discovered: node_id=xyz789, location=Lisboa, Portugal
```

### 2. Verificar no Dashboard Web

Acesse: `http://localhost:3000/studio`

No painel "Network Metrics", você verá:
- **Connected Peers:** Número de nós conectados
- **Active Relays:** Status do relay (verde = conectado)
- **Last Sync:** Última sincronização bem-sucedida

### 3. Verificar no Mapa Global

No componente `GlobalMap.tsx`, você verá:
- Pontos no mapa representando cada nó
- Linhas conectando nós que estão em comunicação P2P
- Cores indicando latência (verde = rápido, amarelo = médio, vermelho = lento)

### 4. Teste Manual via API

Execute este comando no terminal:

```bash
curl http://localhost:8000/api/lattice/peers
```

Resposta esperada:
```json
{
  "peers": [
    {
      "node_id": "abc123",
      "location": "Luanda, Angola",
      "last_seen": 1711382400,
      "status": "active"
    }
  ],
  "relay_status": "connected",
  "relay_url": "https://gun-manhattan.herokuapp.com/gun"
}
```

---

## 🛠️ COMANDOS ÚTEIS

### Reiniciar Conexão com o Relay
```bash
# No backend Python
curl -X POST http://localhost:8000/api/lattice/reconnect
```

### Verificar Saúde do Relay
```bash
# Testa se o relay está respondendo
curl https://gun-manhattan.herokuapp.com/gun
```

Resposta esperada: `"Hi! I'm a Gun server."`

### Listar Todos os Nós Ativos
```bash
# Via API Python
curl http://localhost:8000/api/lattice/discover
```

---

## 🏛️ CAMINHO PARA O RELAY SOBERANO

### Fase 1: Testes com Relay Público (ATUAL)
- ✅ Use Manhattan para validar a rede
- ✅ Teste descoberta de peers
- ✅ Valide sincronização de provas

### Fase 2: Deploy do DIOTEC_RELAY_v1 (PRÓXIMO)
Kiro deve implementar:

1. **Servidor Node.js com GunDB**
   ```javascript
   // server.js
   const Gun = require('gun');
   const express = require('express');
   const app = express();
   
   app.use(Gun.serve);
   const server = app.listen(8765);
   Gun({ web: server });
   
   console.log('DIOTEC Relay ativo em wss://gun-relay.diotec360.com/gun');
   ```

2. **Deploy na Vercel ou Railway**
   - Domínio: `gun-relay.diotec360.com`
   - SSL automático
   - Monitoramento 24/7

3. **Atualizar .env**
   ```bash
   GUNDB_RELAY_URL=wss://gun-relay.diotec360.com/gun
   ```

### Fase 3: Monetização (FUTURO)
- Cobrar taxa de conectividade para empresas
- Oferecer relay privado de alta velocidade
- SLA garantido para clientes premium

---

## 🚨 TROUBLESHOOTING

### Problema: "Relay não conecta"
**Solução:**
1. Verifique se o URL está correto no `.env`
2. Teste o relay manualmente: `curl https://gun-manhattan.herokuapp.com/gun`
3. Verifique firewall/proxy bloqueando WebSockets

### Problema: "Nós não se descobrem"
**Solução:**
1. Confirme que ambos os nós usam o MESMO relay URL
2. Verifique se `peer_announcer.py` está rodando
3. Aumente o timeout de descoberta no código

### Problema: "Sincronização lenta"
**Solução:**
1. Use relay geograficamente mais próximo
2. Considere deploy do seu próprio relay
3. Otimize tamanho das mensagens P2P

---

## 📊 MÉTRICAS DE SUCESSO

### Rede Saudável:
- ✅ Relay conectado em < 2 segundos
- ✅ Descoberta de peers em < 5 segundos
- ✅ Sincronização de provas em < 10 segundos
- ✅ Latência P2P < 200ms

### Rede com Problemas:
- ❌ Relay timeout > 10 segundos
- ❌ Zero peers descobertos após 30 segundos
- ❌ Sincronização falhando repetidamente

---

## 🎯 PRÓXIMOS PASSOS

1. **AGORA:** Teste com relay de Manhattan
2. **Esta Semana:** Kiro implementa DIOTEC_RELAY_v1
3. **Próximo Mês:** Deploy do relay soberano
4. **Futuro:** Rede de relays distribuídos globalmente

---

## 📞 SUPORTE

**Engenheiro-Chefe:** Kiro  
**Arquiteto:** Aethel  
**Soberano:** Dionísio Sebastião Barros

**Documentação GunDB:** https://gun.eco/docs/  
**Relay Público:** https://github.com/amark/gun/wiki/Awesome-GUN#relays

---

**[STATUS: MANUAL COMPLETO]**  
**[RELAY: MANHATTAN ATIVO]**  
**[PRÓXIMO: PRIMEIRO SINAL P2P]** 🏛️📡✨
