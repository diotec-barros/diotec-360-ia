# ===========================================================================
# DIOTEC 360 SOVEREIGN RELAY - DOCKER IMAGE
# ===========================================================================
# 
# Container para o relay GunDB soberano
# Deploy em qualquer servidor com Docker
#
# Build: docker build -t diotec360-relay .
# Run: docker run -p 8765:8765 diotec360-relay
#
# ===========================================================================

FROM node:18-alpine

# Metadata
LABEL maintainer="Dionísio Sebastião Barros <dionisio@diotec360.com>"
LABEL description="DIOTEC 360 Sovereign P2P Relay"
LABEL version="1.0.0"

# Criar diretório de trabalho
WORKDIR /app

# Copiar package.json e instalar dependências
COPY package*.json ./
RUN npm ci --only=production

# Copiar código do servidor
COPY server.js ./

# Expor porta
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8765/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Variáveis de ambiente padrão
ENV RELAY_PORT=8765
ENV RELAY_HOST=0.0.0.0
ENV RELAY_CORS_ORIGINS=*
ENV NODE_ENV=production

# Iniciar servidor
CMD ["node", "server.js"]
