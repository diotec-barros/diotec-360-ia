# 🚀 UPLOAD PARA HUGGING FACE - INSTRUÇÕES IMEDIATAS

## ⚡ FAÇA ISSO AGORA (5 MINUTOS)

### PASSO 1: Acesse o Hugging Face (1 min)
1. Abra: https://huggingface.co/spaces
2. Clique no botão verde "Create new Space"

### PASSO 2: Configure o Space (1 min)
- **Owner**: Sua conta
- **Space name**: `diotec360-api`
- **License**: `apache-2.0`
- **Select the Space SDK**: `Docker`
- **Space hardware**: `CPU basic - Free`
- **Repo type**: `Public`

Clique em "Create Space"

### PASSO 3: Upload de Arq min)

Na página do Space, clique em "Files" e faça upload destes arquivos:

**ARQUIVOS OBRIGATÓRIOS:**
```
📁 Raiz do Space:
├── Dockerfile (diotec360/Dockerfile)
├── README.md (renomeie diotec360/README_HF.md)
├── requirements.tx

📁 Copie estas pastas completas:
├── diotec360/ (pasta completa)
└── api/ (pasta completa)
```

**COMO FAZER UPLOAD:**
- Clique em "Add file" > "Upload files"
- Arraste as pastas e arquivos
- Ou use Git (se preferir):
  ```bash
  git clone https://hugg
  cd diotec360-api
  # Copie os arquivos
  git add .
  git commit -m "Initial deploy v3.6.0"
  git push
  ```

### PASSO 4: Configure Secrets (1 min)

No Space, vá em "Settings" > "Variables and secrets":

Adicione estas variáveis:

```
PAYPAL_CLIENT_ID = AZCY3ggrDLD9XNnvyVOGdU2ir7PsycmAyjro-0mFHv0XC5Fw2EAVrVrU1rqFDQZkWjYbAyksruNQGgAn
PAYPAL_SECRET = EESM6eSh2vtHdf4hGvMr_v2EI0jSOP
PAYPAL_WEBHOOK_ID = 68N36636YR118321L
PAYPAL_MODE = sandbox
DIOTEC360_CORS_ORIGINS = *
```

### PASSO 5: Deploy Automático!

O Hugging Face vai:
1. Detectar o Dockerfile
2. Fazer build da imagem
3. Iniciar o container
4. Expor na porta 7860

**URL final**: `https://SEU_USERNAME-diotec360-api.hf.space`

---

## ✅ VERIFICAÇÃO PÓS-DEPLOY

Após o deploy, teste:

```bash
# Health check
curl https://SEU_USERNAME-diotec360-api.hf.space/health

# Treasury health
curl https://SEU_USERNAME-diotec360-api.hf.space/api/treasury/health
```

---

## 🎯 ALTERNATIVA RÁPIDA: USE O SCRIPT

Execute este comando na pasta diotec360:

```powershell
.\scripts\prepare_hf_upload.ps1
```

Isso criará uma pasta `hf_upload_package/` com tudo pronto!

---

**TEMPO TOTAL: 5 MINUTOS**  
**DIFICULDADE: FÁCIL**  
**RESULTADO: IMPÉRIO ONLINE** 🏛️💰🚀
