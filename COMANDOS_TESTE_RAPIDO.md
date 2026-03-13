# ⚡ COMANDOS DE TESTE RÁPIDO

**Use estes comandos para testar rapidamente após configurar os domínios**

---

## 🔍 TESTE 1: DNS Propagou?

### Windows (CMD)
```cmd
nslookup api.diotec360.com
nslookup aethel.diotec360.com
```

**Resultado esperado**:
```
Name:    api.diotec360.com
Address: [IP do Railway]

Name:    aethel.diotec360.com
Address: [IP do Vercel]
```

Se retornar "can't find" ou "NXDOMAIN", aguarde mais um pouco.

---

## 🏥 TESTE 2: Backend Está Vivo?

### Windows (CMD)
```cmd
curl https://api.diotec360.com/health
```

**Resultado esperado**:
```json
{"status":"healthy"}
```

### Se não tiver curl, use PowerShell:
```powershell
Invoke-WebRequest -Uri https://api.diotec360.com/health
```

---

## 📋 TESTE 3: Exemplos Carregam?

### Windows (CMD)
```cmd
curl https://api.diotec360.com/api/examples
```

**Resultado esperado**:
```json
[
  {
    "name": "Financial Transfer",
    "code": "intent transfer..."
  },
  ...
]
```

---

## ✅ TESTE 4: Verificação Funciona?

### Windows (CMD)
```cmd
curl -X POST https://api.diotec360.com/api/verify ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"intent test() { verify { true; } }\"}"
```

**Resultado esperado**:
```json
{
  "status": "proved",
  "merkle_root": "...",
  ...
}
```

---

## 🌐 TESTE 5: Frontend Carrega?

### Abrir no navegador:
```
https://aethel.diotec360.com
```

**Verificar**:
- [ ] Página carrega
- [ ] Editor aparece
- [ ] Sem erros no console (F12)
- [ ] Cadeado verde (SSL)

---

## 🔮 TESTE 6: Ghost-Runner Funciona?

### No navegador:
1. Acesse: https://aethel.diotec360.com
2. Ative Ghost-Runner
3. Digite código
4. Observe Ghost Panel aparecer

**Verificar no console (F12)**:
```javascript
// Deve ver requisições para:
POST https://api.diotec360.com/api/ghost/predict
// Status: 200 OK
```

---

## 🪞 TESTE 7: Mirror Funciona?

### No navegador:
1. Verifique um código
2. Clique "Manifest Reality"
3. Mirror deve abrir

**Verificar no console (F12)**:
```javascript
// Deve ver requisições para:
POST https://api.diotec360.com/api/mirror/manifest
GET https://api.diotec360.com/api/mirror/preview/[id]
// Status: 200 OK
```

---

## 🔐 TESTE 8: SSL Ativo?

### Windows (CMD)
```cmd
curl -I https://api.diotec360.com/health
```

**Verificar**:
```
HTTP/2 200
...
```

Se aparecer "HTTP/2", SSL está ativo!

### Ou no navegador:
- Cadeado verde na barra de endereço
- Clique no cadeado → "Conexão segura"

---

## 📊 TESTE 9: Performance

### Medir tempo de resposta:

**Windows PowerShell**:
```powershell
Measure-Command { Invoke-WebRequest -Uri https://api.diotec360.com/health }
```

**Resultado esperado**:
```
TotalMilliseconds : 200-500
```

---

## 🐛 TESTE 10: Logs do Backend

### No Railway Dashboard:
1. Acesse o projeto
2. Clique em "View Logs"
3. Procure por:

**Logs bons** ✅:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Logs ruins** ❌:
```
ERROR: ...
Traceback ...
```

---

## 📱 TESTE 11: Mobile

### No celular:
1. Acesse: https://aethel.diotec360.com
2. Teste interface
3. Verifique responsividade

---

## 🌍 TESTE 12: Diferentes Navegadores

### Testar em:
- [ ] Chrome
- [ ] Firefox
- [ ] Edge
- [ ] Safari (se tiver Mac)

---

## ⚡ SCRIPT DE TESTE COMPLETO

### Windows (CMD)
```cmd
@echo off
echo ========================================
echo TESTANDO Diotec360 v1.1
echo ========================================
echo.

echo [1/5] Testando DNS...
nslookup api.diotec360.com
echo.

echo [2/5] Testando Backend Health...
curl https://api.diotec360.com/health
echo.

echo [3/5] Testando Examples...
curl https://api.diotec360.com/api/examples
echo.

echo [4/5] Testando Verify...
curl -X POST https://api.diotec360.com/api/verify ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"intent test() { verify { true; } }\"}"
echo.

echo [5/5] Abrindo Frontend...
start https://aethel.diotec360.com
echo.

echo ========================================
echo TESTES CONCLUIDOS!
echo ========================================
pause
```

**Salve como**: `teste_aethel.bat`  
**Execute**: Duplo clique

---

## 🎯 CHECKLIST RÁPIDO

Após configurar domínios, execute na ordem:

1. [ ] `nslookup api.diotec360.com` - DNS propagou?
2. [ ] `curl https://api.diotec360.com/health` - Backend vivo?
3. [ ] Abrir https://aethel.diotec360.com - Frontend carrega?
4. [ ] Testar Ghost-Runner - Funciona?
5. [ ] Testar Mirror - Funciona?
6. [ ] Verificar SSL - Cadeado verde?
7. [ ] Testar em mobile - Responsivo?
8. [ ] Testar em outro navegador - Compatível?

---

## 💡 DICAS

### Se DNS não propagou ainda:
```cmd
# Aguarde 5 minutos e teste novamente
timeout /t 300
nslookup api.diotec360.com
```

### Se backend não responde:
1. Verificar logs no Railway
2. Verificar se container está rodando
3. Verificar se porta está correta

### Se frontend não conecta:
1. Verificar console (F12)
2. Verificar variável NEXT_PUBLIC_API_URL
3. Verificar CORS no backend

---

## 🚀 QUANDO TUDO FUNCIONAR

Execute o teste completo:
```cmd
teste_aethel.bat
```

Se tudo passar, você está pronto para:
1. ✅ Executar TESTES_FINAIS_V1_1.md
2. ✅ Lançar oficialmente
3. ✅ Celebrar! 🎉

---

**Boa sorte nos testes!** 🌟
