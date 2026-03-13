# 🌐 CONFIGURAÇÃO FINAL - Domínios Aethel

**Data**: 3 de Fevereiro de 2026  
**Status**: ✅ Backend no ar | 🔄 Configurando domínios

---

## 📊 SITUAÇÃO ATUAL

✅ **Backend Railway**: Funcionando  
✅ **Domínio**: diotec360.com (comprado no Vercel)  
🔄 **Configuração DNS**: Em andamento

---

## 🎯 ESTRUTURA FINAL

```
Frontend: https://aethel.diotec360.com  (Vercel)
Backend:  https://api.diotec360.com     (Railway)
```

---

## 📋 PASSO 1: CONFIGURAR BACKEND (Railway)

### 1.1 No Railway Dashboard

1. Acesse: https://railway.app
2. Entre no projeto "Aethel"
3. Clique em **Settings** → **Networking**
4. Em **Custom Domain**, clique em **Add Domain**
5. Digite: `api.diotec360.com`
6. Railway vai mostrar um CNAME (exemplo: `7m1g5de7.up.railway.app`)

### 1.2 Copie o CNAME

Railway vai mostrar algo como:
```
Configure DNS Records
Add the following DNS records to diotec360.com

Type    Name    Value
CNAME   api     7m1g5de7.up.railway.app
```

**COPIE O VALOR** (exemplo: `7m1g5de7.up.railway.app`)

---

## 📋 PASSO 2: CONFIGURAR DNS NO VERCEL

Como você comprou o domínio no Vercel, vamos configurar lá:

### 2.1 Acesse Vercel Domains

1. Vá para: https://vercel.com/dashboard
2. Clique em **Domains** (menu lateral)
3. Encontre `diotec360.com`
4. Clique em **Manage** ou **DNS**

### 2.2 Adicionar Registro CNAME para Backend

Clique em **Add Record** e preencha:

```
Type:     CNAME
Name:     api
Value:    7m1g5de7.up.railway.app    (o valor que Railway mostrou)
TTL:      Auto (ou 3600)
Comment:  Aethel Backend API
```

Clique em **Save** ou **Add**

---

## 📋 PASSO 3: CONFIGURAR FRONTEND (Vercel)

### 3.1 No Projeto Vercel

1. Acesse seu projeto "diotec360-lang" no Vercel
2. Vá em **Settings** → **Domains**
3. Clique em **Add**
4. Digite: `aethel.diotec360.com`
5. Clique em **Add**

### 3.2 Vercel vai Configurar Automaticamente

Como o domínio já é do Vercel, ele vai:
- ✅ Criar o registro DNS automaticamente
- ✅ Gerar certificado SSL
- ✅ Configurar tudo em segundos

**Você não precisa fazer nada no DNS para o frontend!**

---

## 📋 PASSO 4: ATUALIZAR VARIÁVEL DE AMBIENTE

### 4.1 No Vercel

1. No projeto "diotec360-lang"
2. Vá em **Settings** → **Environment Variables**
3. Encontre `NEXT_PUBLIC_API_URL`
4. Clique em **Edit**
5. Mude para: `https://api.diotec360.com`
6. Clique em **Save**

### 4.2 Redeploy

1. Vá em **Deployments**
2. Clique nos 3 pontinhos da última deployment
3. Clique em **Redeploy**
4. Aguarde 1-2 minutos

---

## 📋 PASSO 5: AGUARDAR PROPAGAÇÃO

### DNS do Backend (api.diotec360.com)
- Tempo: 5-30 minutos (geralmente 10 minutos)
- Vercel DNS é rápido

### SSL Automático
- Railway: 5-10 minutos após DNS propagar
- Vercel: Instantâneo

---

## 🧪 PASSO 6: TESTAR

### 6.1 Testar Backend

Aguarde 10-15 minutos, depois teste:

```bash
curl https://api.diotec360.com/health
```

**Deve retornar**:
```json
{"status":"healthy"}
```

Se der erro de DNS, aguarde mais um pouco.

### 6.2 Testar Frontend

1. Acesse: https://aethel.diotec360.com
2. Deve carregar o Aethel Studio
3. Carregue um exemplo
4. Clique em "Verify"
5. Deve funcionar!

---

## 📊 RESUMO DOS REGISTROS DNS

No Vercel DNS (diotec360.com):

```
# Backend (Railway) - VOCÊ PRECISA ADICIONAR
Type: CNAME
Name: api
Value: 7m1g5de7.up.railway.app  (o valor que Railway mostrou)

# Frontend (Vercel) - AUTOMÁTICO
Type: CNAME
Name: aethel
Value: cname.vercel-dns.com  (Vercel adiciona automaticamente)
```

---

## 🎯 CHECKLIST COMPLETO

### Railway
- [ ] Projeto Aethel funcionando
- [ ] Settings → Networking → Custom Domain
- [ ] Adicionar: api.diotec360.com
- [ ] Copiar o CNAME mostrado

### Vercel DNS
- [ ] Acessar Domains → diotec360.com
- [ ] Add Record → CNAME
- [ ] Name: api
- [ ] Value: [CNAME do Railway]
- [ ] Save

### Vercel Frontend
- [ ] Projeto diotec360-lang
- [ ] Settings → Domains
- [ ] Add: aethel.diotec360.com
- [ ] (Vercel configura automaticamente)

### Variável de Ambiente
- [ ] Settings → Environment Variables
- [ ] NEXT_PUBLIC_API_URL = https://api.diotec360.com
- [ ] Save
- [ ] Redeploy

### Testes
- [ ] Aguardar 10-15 minutos
- [ ] curl https://api.diotec360.com/health
- [ ] Acessar https://aethel.diotec360.com
- [ ] Testar verificação de código

---

## 🐛 TROUBLESHOOTING

### "DNS not found" ou "Cannot resolve"
- **Causa**: DNS ainda não propagou
- **Solução**: Aguarde 10-30 minutos
- **Teste**: `nslookup api.diotec360.com`

### "Certificate error" ou "Not secure"
- **Causa**: SSL ainda não gerado
- **Solução**: Aguarde 5-10 minutos após DNS propagar
- Railway/Vercel geram automaticamente

### Frontend não conecta com backend
- **Causa**: Variável de ambiente incorreta
- **Solução**: 
  1. Verificar `NEXT_PUBLIC_API_URL` no Vercel
  2. Deve ser: `https://api.diotec360.com`
  3. Redeploy após mudar

### CORS error no console
- **Causa**: Backend não permite origem do frontend
- **Solução**: Verificar CORS no `api/main.py`
- Deve incluir: `https://aethel.diotec360.com`

---

## ✅ RESULTADO FINAL

Quando tudo estiver configurado (15-30 minutos):

```
✅ https://api.diotec360.com/health
   → {"status":"healthy"}

✅ https://aethel.diotec360.com
   → Aethel Studio carrega

✅ Verificação de código funciona
✅ Ghost-Runner ativo
✅ Mirror funcionando
✅ Certificados SSL ativos
✅ Pronto para o mundo! 🌍
```

---

## 🚀 ORDEM DE EXECUÇÃO

1. ✅ **Railway**: Adicionar domínio api.diotec360.com
2. ✅ **Copiar**: CNAME que Railway mostrou
3. ✅ **Vercel DNS**: Adicionar registro CNAME
4. ✅ **Vercel Frontend**: Adicionar domínio aethel.diotec360.com
5. ✅ **Variável**: Atualizar NEXT_PUBLIC_API_URL
6. ✅ **Redeploy**: Frontend no Vercel
7. ⏳ **Aguardar**: 10-30 minutos
8. ✅ **Testar**: Ambos os domínios
9. 🎉 **Celebrar**: Aethel está no ar!

---

## 💡 DICA IMPORTANTE

**Não se preocupe se não funcionar imediatamente!**

DNS leva tempo para propagar. É normal:
- Primeiros 5 minutos: Pode dar erro
- 10-15 minutos: Geralmente já funciona
- 30 minutos: Definitivamente funcionando
- 24 horas: Propagação completa mundial

**Seja paciente e teste periodicamente!**

---

## 📞 PRÓXIMOS PASSOS

Depois que tudo estiver funcionando:

1. ✅ Executar testes finais (FINAL_TESTS_V1_1.md)
2. ✅ Postar anúncios (LAUNCH_V1_1_ANNOUNCEMENTS.md)
3. ✅ Monitorar feedback
4. ✅ Celebrar o lançamento! 🎉

---

**Você está a 30 minutos de ter o Aethel no ar com domínios profissionais!** 🚀

**Qualquer dúvida, me chame!**
