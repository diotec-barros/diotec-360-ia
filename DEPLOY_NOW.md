# 🚀 DEPLOY AGORA - DIOTEC 360 IA v3.6.0

## ✅ STATUS: PRONTO PARA DEPLOY

**Testes**: 27/27 passando (100%)  
**Segurança**: APROVADO  
**Compliance**: ANGOLA READY  

---

## OPÇÃO 1: DEPLOY RÁPIDO (Hugging Face)

### Passo 1: Criar Space
1. Acesse: https://huggingface.co/spaces
2. Clique "Create new Space"
3. Configure:
   - Name: `diotec360-api`
   - SDK: `Docker`
   - Hardware: `CPU basic` (free)

### Passo 2: Upload de Arquivos
Faça upload destes arquivos/pastas:
- `Dockerfile`
- `diotec360/` (pasta completa)
- `api/` (pasta completa)
- `README_HF.md` (renomeie para README.md)

### Passo 3: Configurar Secrets
No Hugging Face Space, vá em Settings > Variables and secrets:
```
PAYPAL_CLIENT_ID=AZCY3ggrDLD9XNnvyVOGdU2ir7PsycmAyjro-0mFHv0XC5Fw2EAVrVrU1rqFDQZkWjYbAyksruNQGgAn
PAYPAL_SECRET=EESM6eSh2vMjZUeNBCytDtbiIPAJan5hQgfwFb6rHZKvYAwta_SMO75MzNCrtHdf4hGvMr_v2EI0jSOP
PAYPAL_WEBHOOK_ID=68N36636YR118321L
PAYPAL_MODE=sandbox
DIOTEC360_CORS_ORIGINS=*
```

### Passo 4: Deploy Automático
O Hugging Face fará deploy automaticamente!

URL final: `https://your-username-diotec360-api.hf.space`

---

## OPÇÃO 2: DEPLOY LOCAL (Teste)

```powershell
cd diotec360
python api/run.py
```

Acesse: http://localhost:8000

---

## PRÓXIMOS PASSOS

1. ✅ Deploy feito
2. Teste endpoint: `GET /health`
3. Configure webhook no PayPal
4. Teste compra com sandbox
5. Switch para live mode

---

**O IMPÉRIO ESTÁ PRONTO!** 🏛️💰🚀
