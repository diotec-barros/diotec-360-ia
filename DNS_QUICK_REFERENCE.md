# 🚀 DNS QUICK REFERENCE

**Configuração rápida do subdomínio HF**

---

## 📋 REGISTRO DNS

```
Type:  CNAME
Name:  hf
Value: diotec-diotec360-judge.hf.space
TTL:   60
```

---

## 🌐 ONDE CONFIGURAR

**Vercel Dashboard:**
https://vercel.com/dashboard

1. Selecione `diotec360.com`
2. Vá em "DNS"
3. Clique em "Add Record"
4. Preencha os campos acima
5. Clique em "Save"

---

## ✅ RESULTADO

**Antes:**
- ❌ https://hf.diotec360.com (não funciona)

**Depois:**
- ✅ https://hf.diotec360.com (funciona!)

---

## 🧪 TESTE

```bash
# Aguarde 2-5 minutos, depois:
curl https://hf.diotec360.com/health

# Deve retornar:
{"status":"healthy","version":"3.0.5"}
```

---

## 🔺 TRIANGLE COMPLETO

```
Node 1: https://hf.diotec360.com
Node 2: https://node2.diotec360.com
Node 3: https://backup.diotec360.com
```

---

## 📚 DOCUMENTAÇÃO

- `ACAO_IMEDIATA_DNS_HF.md` - Guia completo
- `RESUMO_SUBDOMINIO_HF.md` - Resumo
- `🎯_CONFIGURE_DNS_AGORA.txt` - Visual

---

**⏱️ TEMPO TOTAL: 5 minutos + 2-5 min propagação**

**🎯 AÇÃO: Configure o DNS agora!**
