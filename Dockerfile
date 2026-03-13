# ===========================================================================
# DIOTEC 360 IA - DOCKERFILE v3.6.0
# "The Global Launch Activation"
# ===========================================================================
# 
# Container Docker para deploy no Hugging Face Spaces
# Desenvolvido por: Kiro para Dionísio Sebastião Barros
# Data: 12 de Março de 2026
# ===========================================================================

FROM python:3.11-slim

# Metadados
LABEL maintainer="Dionísio Sebastião Barros <dionisio@diotec360.com>"
LABEL version="3.6.0"
LABEL description="DIOTEC 360 IA - First Angolan Sovereign Fintech with Mathematical Proof"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libz3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY api/requirements.txt /app/requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY diotec360 /app/diotec360
COPY api /app/api

# Criar diretórios de dados
RUN mkdir -p /app/.diotec360_state \
    /app/.diotec360_vault \
    /app/.diotec360_sentinel

# Expor porta
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health')"

# Comando de inicialização
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2"]
