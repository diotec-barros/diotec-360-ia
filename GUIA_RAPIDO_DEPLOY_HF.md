# 🚀 Guia Rápido - Deploy DIOTEC 360 IA no Hugging Face

## ⚡ Deploy em 5 Minutos

### Passo 1: Preparar Pacote (30 segundos)

```powershell
.\prepare_huggingface_deploy.ps1
```

Este script cria a pasta `huggingface_deploy_package` com tudo pronto para upload.

### Passo 2: Criar Arquivos no Space (2 minutos)

Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge

#### 2.1 - Criar README.md
1. Clique em "Files" → "Add file" → "Create a new file"
2. Nome: `README.md`
3. Cole o conteúdo de: `huggingface_deploy_package/README.md`
4. Clique em "Commit new file to main"

#### 2.2 - Criar requirements.txt
1. "Add file" → "Create a new file"
2. Nome: `requirements.txt`
3. Cole o conteúdo de: `huggingface_deploy_package/requirements.txt`
4. Commit

#### 2.3 - Criar Dockerfile
1. "Add file" → "Create a new file"
2. Nome: `Dockerfile`
3. Cole o conteúdo de: `huggingface_deploy_package/Dockerfile`
4. Commit

#### 2.4 - Criar .dockerignore
1. "Add file" → "Create a new file"
2. Nome: `.dockerignore`
3. Cole o conteúdo de: `huggingface_deploy_package/.dockerignore`
4. Commit

### Passo 3: Upload do Código (2 minutos)

1. Clique em "Files" → "Add file" → "Upload files"
2. Arraste as pastas:
   - `huggingface_deploy_package/diotec360/`
   - `huggingface_deploy_package/api/`
3. Clique em "Commit changes to main"

### Passo 4: Aguardar Build (1-2 minutos)

O Hugging Face iniciará o build automaticamente. Você verá:

- 🟡 **Building** - Container sendo construído
- 🟢 **Running** - Deploy completo!

### Passo 5: Testar (30 segundos)

Acesse: https://diotec-360-diotec-360-ia-judge.hf.space

Você deve ver a resposta JSON com o status do sistema.

## 🎯 Conteúdo dos Arquivos

### README.md
```markdown
---
title: DIOTEC 360 IA - Sovereign Judge
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
license: apache-2.0
---

# DIOTEC 360 IA - The Sovereign Judge

**The first mathematically proved sovereign AI infrastructure.**

Developed by **Kiro** for **Dionísio Sebastião Barros**.
```

### requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
z3-solver==4.12.6.0
lark==1.1.9
psutil==5.9.8
cryptography==42.0.2
python-dotenv==1.0.1
aiohttp==3.9.3
pydantic==2.6.0
python-multipart==0.0.9
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    z3 \
    libz3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
ENV PYTHONPATH="/app"

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . .

EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

## 🧪 Testar Endpoints

### Health Check
```bash
curl https://diotec-360-diotec-360-ia-judge.hf.space/
```

### Verificar Intent
```bash
curl -X POST https://diotec-360-diotec-360-ia-judge.hf.space/verify \
  -H "Content-Type: application/json" \
  -d '{
    "intent_name": "test",
    "code": "intent test() { guard { x > 0; } solve { priority: security; } verify { y == x; } }"
  }'
```

### Métricas
```bash
curl https://diotec-360-diotec-360-ia-judge.hf.space/metrics
```

## 🐛 Troubleshooting

### Build Falha
- Verifique os logs no Space
- Confirme que o Dockerfile está correto
- Verifique se todas as dependências estão em requirements.txt

### Container Não Inicia
- Confirme que a porta 7860 está configurada
- Verifique se o comando CMD está correto no Dockerfile
- Veja os logs de erro no Space

### API Não Responde
- Teste primeiro o endpoint `/`
- Verifique se `api/main.py` existe
- Confirme que o PYTHONPATH está configurado

## ✅ Checklist

- [ ] Script `prepare_huggingface_deploy.ps1` executado
- [ ] README.md criado no Space
- [ ] requirements.txt criado no Space
- [ ] Dockerfile criado no Space
- [ ] .dockerignore criado no Space
- [ ] Pasta diotec360/ enviada
- [ ] Pasta api/ enviada
- [ ] Build completado (verde)
- [ ] API respondendo em /
- [ ] Endpoints testados

## 🎉 Pronto!

Quando tudo estiver verde, o Sovereign Judge estará online em:

**https://diotec-360-diotec-360-ia-judge.hf.space**

⚖️ **The Monolith is Alive!** 🏛️

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
