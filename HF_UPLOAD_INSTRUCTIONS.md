# UPLOAD HUGGING FACE - 5 MINUTOS

## PASSO 1: Criar Space
1. https://huggingface.co/spaces
2. "Create new Space"
3. Nome: `diotec360-api`
4. SDK: `Docker`
5. Hardware: `CPU basic`

## PASSO 2: Upload Arquivos
Arraste para o Space:
- `Dockerfile`
- `README_HF.md` (renomeie para README.md)
- Pasta `diotec360/`
- Pasta `api/`

## PASSO 3: Configure Secrets
Settings > Variables:
```
PAYPAL_CLIENT_ID=AZCY3ggrDLD9XNnvyVOGdU2ir7PsycmAyjro-0mFHv0XC5Fw2EAVrVrU1rqFDQZkWjYbAyksruNQGgAn
PAYPAL_SECRET=EESM6eSh2vMjZUeNBCytDtbiIPAJan5hQgfwFb6rHZKvYAwta_SMO75MzNCrtHdf4hGvMr_v2EI0jSOP
PAYPAL_WEBHOOK_ID=68N36636YR118321L
PAYPAL_MODE=sandbox
DIOTEC360_CORS_ORIGINS=*
```

## PASSO 4: Deploy Automático!
Aguarde 2-3 minutos.

URL: `https://SEU_USERNAME-diotec360-api.hf.space`

PRONTO! 🚀
