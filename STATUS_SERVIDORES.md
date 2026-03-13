# 📊 STATUS DOS SERVIDORES - TEMPO REAL

**Última Atualização**: 27/02/2026

---

## 🟢 BACKEND API (Processo ID: 2)

**URL**: http://127.0.0.1:8000

**Status**: ✅ RODANDO

**Atividade Recente**:
- ✅ Lattice HTTP Sync ativo
- ✅ Sincronizando com Hugging Face Space (200 OK)
- ⚠️ api.diotec360.com retornando 404 (esperado - domínio ainda não configurado)
- ✅ Persistence layer funcionando
- ✅ Vault e State prontos

**Logs Importantes**:
```
INFO: Uvicorn running on http://127.0.0.1:8000
[ROCKET] LATTICE READY - Hybrid Sync Active
[HTTP_SYNC] Monitoring 2 peer node(s)
```

---

## 🟢 FRONTEND (Processo ID: 3)

**URL**: http://localhost:3000

**Status**: ✅ RODANDO

**Atividade Recente**:
- ✅ Next.js 16.1.6 com Turbopack
- ✅ Página inicial compilada (51s)
- ✅ Cache do filesystem escrito (11.5s)
- ⚠️ Aviso de CORS cross-origin (não crítico para desenvolvimento)

**Logs Importantes**:
```
✓ Ready in 26.4s
GET / 200 in 51s (compile: 51s, render: 587ms)
✓ Finished writing to filesystem cache
```

---

## 🧪 PRONTO PARA TESTE PAYPAL

### URLs de Acesso:
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

### Configuração PayPal:
- ✅ Modo: SANDBOX
- ✅ Client ID: Configurado
- ✅ Secret: Configurado
- ✅ Webhook ID: 68N36636YR118321L
- ✅ Webhook URL: https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook

### Próximo Passo:
1. Abra http://localhost:3000 no navegador
2. Navegue até a página de pagamento
3. Clique em "Pagar com PayPal"
4. Use conta Personal do sandbox para testar

---

## 📝 Comandos Úteis

### Ver logs em tempo real:
```powershell
# Backend
Get-Content api\*.log -Wait

# Ou use o monitor
.\monitor_test_logs.ps1
```

### Verificar processos:
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"}
```

### Parar servidores:
```powershell
# Parar backend
Stop-Process -Name python -Force

# Parar frontend
Stop-Process -Name node -Force
```

---

## 🏛️ THE MONOLITH IS ALIVE AND READY
## ⚖️ AWAITING YOUR TEST TRANSACTION
