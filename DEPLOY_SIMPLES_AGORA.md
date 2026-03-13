# 🚀 DEPLOY SIMPLES - EXECUTE AGORA

**Data:** 2026-02-12  
**Arquitetura:** 1 Frontend + 1 Backend

---

## 🎯 CONFIGURAÇÃO FINAL

```
Frontend: https://aethel.diotec360.com/ (Vercel)
Backend:  https://api.diotec360.com (Hugging Face)
```

---

## ✅ PASSO 1: CONFIGURAR DNS (2 min)

**No dashboard do Vercel:**

1. Acesse: https://vercel.com/dashboard
2. Selecione o domínio `diotec360.com`
3. Vá em "DNS"
4. Atualize/Crie o registro `api`:
   ```
   Type: CNAME
   Name: api
   Value: diotec-diotec360-judge.hf.space
   TTL: 60
   ```

---

## ✅ PASSO 2: DEPLOY HUGGING FACE (10 min)

```bash
# Execute o script
deploy_node1_huggingface.bat
```

**O que acontece:**
1. Faz push do código para Hugging Face
2. Hugging Face faz build automático (5-10 min)
3. Space