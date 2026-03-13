# 🚀 DIOTEC 360 IA - Instruções de Deploy para Hugging Face

## 📋 Pré-requisitos

1. Conta no Hugging Face: https://huggingface.co
2. Space criado: `diotec-360/diotec-360-ia-judge`
3. Token de acesso com permissões de escrita

## 🎯 Método 1: Upload via Interface Web (Recomendado)

### Passo 1: Criar Arquivos de Configuração

No seu Space, clique em "Files" → "Add file" → "Create a new file" e crie:

1. **README.md** - Copie o conteúdo de `huggingface_deploy/README.md`
2. **requirements.txt** - Copie o conteúdo de `huggingface_deploy/requirements.txt`
3. **Dockerfile** - Copie o conteúdo de `huggingface_deploy/Dockerfile`
4. **.dockerignore** - Copie o conteúdo de `huggingface_deploy/.dockerignore`

### Passo 2: Upload do Código

1. Clique em "Files" → "Add file" → "Upload files"
2. Arraste as seguintes pastas:
   - `diotec360/` (código principal)
   - `api/` (API FastAPI)
3. Clique em "Commit changes to main"

### Passo 3: Aguardar Build

O Hugging Face iniciará automaticamente o build do Docker container. Você verá:
- 🟡 "Building" - Container sendo construído
- 🟢 "Running" - Deploy completo e online

### Passo 4: Testar

Acesse: https://diotec-360-diotec-360-ia-judge.hf.space

Você verá a resposta da API com o status do sistema.

## 🎯 Método 2: Deploy via Git (Avançado)

### Passo 1: Clonar o Space

```bash
# Instalar Hugging Face CLI
powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"

# Login
huggingface-cli login

# Clonar
git clone https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
cd diotec-360-ia-judge
```

### Passo 2: Copiar Arquivos

```powershell
# Copiar arquivos de configuração
Copy-Item ..\huggingface_deploy\README.md .
Copy-Item ..\huggingface_deploy\requirements.txt .
Copy-Item ..\huggingface_deploy\Dockerfile .
Copy-Item ..\huggingface_deploy\.dockerignore .

# Copiar código
Copy-Item -Recurse ..\diotec360 .
Copy-Item -Recurse ..\api .
```

### Passo 3: Commit e Push

```bash
git add .
git commit -m "Deploy DIOTEC 360 IA - Sovereign Judge"
git push
```

## 📊 Verificação de Deploy

### Endpoints Disponíveis

```bash
# Health check
curl https://diotec-360-diotec-360-ia-judge.hf.space/

# Verificar intent
curl -X POST https://diotec-360-diotec-360-ia-judge.hf.space/verify \
  -H "Content-Type: application/json" \
  -d '{"intent_name": "test", "code": "intent test() { guard { x > 0; } solve { priority: security; } verify { y == x; } }"}'

# Métricas
curl https://diotec-360-diotec-360-ia-judge.hf.space/metrics
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Adicione no Space Settings → Variables:

```
DIOTEC360_ENV=production
DIOTEC360_DEBUG=false
DIOTEC360_LOG_LEVEL=INFO
```

### Secrets

Para chaves sensíveis, use Secrets:

```
DIOTEC360_API_KEY=your_secret_key
DIOTEC360_ENCRYPTION_KEY=your_encryption_key
```

## 🐛 Troubleshooting

### Build Falha

1. Verifique os logs no Space
2. Confirme que todas as dependências estão em `requirements.txt`
3. Verifique se o Dockerfile está correto

### Container Não Inicia

1. Verifique se a porta 7860 está configurada
2. Confirme que o comando CMD está correto
3. Verifique logs de erro no Space

### API Não Responde

1. Teste o endpoint `/` primeiro
2. Verifique se o `api/main.py` existe
3. Confirme que o PYTHONPATH está configurado

## 📚 Recursos

- Documentação HF Spaces: https://huggingface.co/docs/hub/spaces
- Docker Spaces: https://huggingface.co/docs/hub/spaces-sdks-docker
- FastAPI Docs: https://fastapi.tiangolo.com

## ✅ Checklist de Deploy

- [ ] README.md criado com metadados corretos
- [ ] requirements.txt com todas as dependências
- [ ] Dockerfile configurado para porta 7860
- [ ] Código diotec360/ copiado
- [ ] Código api/ copiado
- [ ] .dockerignore configurado
- [ ] Commit realizado
- [ ] Build completado (verde)
- [ ] API respondendo em /
- [ ] Endpoints testados

## 🎉 Deploy Completo!

Quando tudo estiver verde, seu Space estará online em:

**https://diotec-360-diotec-360-ia-judge.hf.space**

O Sovereign Judge está pronto para servir! ⚖️🏛️

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
