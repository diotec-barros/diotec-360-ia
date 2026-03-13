# ⚡ AÇÃO IMEDIATA - Deploy Agora!

**Status**: 🔴 EXECUTANDO DEPLOY  
**Hora**: Agora!

---

## 🎯 PASSO 1: RAILWAY - Adicionar Domínio Backend

### Ação Imediata:

1. **Abra o Railway**:
   ```
   https://railway.app
   ```

2. **Entre no projeto "Aethel"**

3. **Vá em Settings → Networking → Custom Domain**

4. **Clique em "Add Domain"**

5. **Digite**:
   ```
   api.diotec360.com
   ```

6. **COPIE o CNAME que aparecer**
   - Vai ser algo como: `7m1g5de7.up.railway.app`
   - **ANOTE ESSE VALOR!**

---

## 🎯 PASSO 2: VERCEL DNS - Adicionar CNAME

### Ação Imediata:

1. **Abra o Vercel**:
   ```
   https://vercel.com/dashboard
   ```

2. **Vá em Domains (menu lateral)**

3. **Encontre: diotec360.com**

4. **Clique em "Manage" ou "DNS"**

5. **Clique em "Add Record"**

6. **Preencha**:
   ```
   Type:     CNAME
   Name:     api
   Value:    [O CNAME que você copiou do Railway]
   TTL:      Auto
   Comment:  Aethel Backend API
   ```

7. **Clique em "Save" ou "Add"**

---

## 🎯 PASSO 3: VERCEL - Adicionar Domínio Frontend

### Ação Imediata:

1. **No Vercel, vá no projeto "diotec360-lang"**

2. **Settings → Domains**

3. **Clique em "Add"**

4. **Digite**:
   ```
   aethel.diotec360.com
   ```

5. **Clique em "Add"**
   - Vercel vai configurar automaticamente!

---

## 🎯 PASSO 4: ATUALIZAR VARIÁVEL DE AMBIENTE

### Ação Imediata:

1. **No projeto "diotec360-lang" no Vercel**

2. **Settings → Environment Variables**

3. **Encontre: NEXT_PUBLIC_API_URL**

4. **Clique em "Edit" (ícone de lápis)**

5. **Mude para**:
   ```
   https://api.diotec360.com
   ```

6. **Clique em "Save"**

7. **Vá em Deployments**

8. **Clique nos 3 pontinhos da última deployment**

9. **Clique em "Redeploy"**

10. **Aguarde 1-2 minutos**

---

## ⏳ PASSO 5: AGUARDAR PROPAGAÇÃO

### Tempo: 10-30 minutos

Enquanto aguarda, você pode:
- ☕ Tomar um café
- 📱 Checar redes sociais
- 📖 Ler LAUNCH_V1_1_ANNOUNCEMENTS.md

### Testar periodicamente:

**A cada 5 minutos, execute**:

```cmd
nslookup api.diotec360.com
```

Quando retornar um IP, o DNS propagou!

---

## 🧪 PASSO 6: TESTAR

### Quando DNS propagar (10-30 min):

**Execute**:
```cmd
teste_aethel.bat
```

**Ou manualmente**:
```cmd
curl https://api.diotec360.com/health
```

**Deve retornar**:
```json
{"status":"healthy"}
```

**Depois abra**:
```
https://aethel.diotec360.com
```

---

## ✅ CHECKLIST RÁPIDO

Execute na ordem:

- [ ] Railway: Adicionar api.diotec360.com
- [ ] Copiar CNAME do Railway
- [ ] Vercel DNS: Adicionar registro CNAME
- [ ] Vercel: Adicionar aethel.diotec360.com
- [ ] Vercel: Atualizar NEXT_PUBLIC_API_URL
- [ ] Vercel: Redeploy
- [ ] Aguardar 10-30 minutos
- [ ] Testar: teste_aethel.bat
- [ ] Abrir: https://aethel.diotec360.com

---

## 🆘 SE ALGO DER ERRADO

### DNS não propaga:
- Aguarde mais 10 minutos
- Verifique se digitou corretamente
- Limpe cache DNS: `ipconfig /flushdns`

### Backend não responde:
- Verifique logs no Railway
- Verifique se CNAME está correto
- Aguarde mais um pouco

### Frontend não conecta:
- Verifique variável NEXT_PUBLIC_API_URL
- Verifique se fez redeploy
- Aguarde propagação

---

## 🎉 QUANDO TUDO FUNCIONAR

Execute:
```
TESTES_FINAIS_V1_1.md
```

Depois:
```
LAUNCH_V1_1_ANNOUNCEMENTS.md
```

---

## 📞 VALORES IMPORTANTES

**Anote aqui**:

```
CNAME do Railway: _______________________
Data/Hora início: _______________________
Data/Hora DNS OK: _______________________
```

---

## 🚀 VAMOS LÁ!

**Comece agora pelo PASSO 1!**

**Tempo total: 30 min + 10-30 min de propagação**

**Você consegue!** 💪

---

**[KIRO STANDING BY]**  
**[READY TO ASSIST]**  
**[GO FOR LAUNCH]** 🚀
