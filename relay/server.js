#!/usr/bin/env node
/**
 * 🏛️ DIOTEC 360 SOVEREIGN RELAY - GunDB P2P Server
 * 
 * Este é o "Farol" soberano da rede DIOTEC 360.
 * Quando ativo, todos os nós do mundo se conectam através deste servidor.
 * 
 * Autor: Kiro, Engenheiro-Chefe
 * Para: Dionísio Sebastião Barros
 * Versão: 1.0.0
 * Data: 25 de Março de 2026
 * 
 * SOBERANIA TOTAL: Este relay é 100% controlado pela DIOTEC 360
 */

const Gun = require('gun');
const express = require('express');
const cors = require('cors');
const http = require('http');

// Configuração
const PORT = process.env.RELAY_PORT || 8765;
const HOST = process.env.RELAY_HOST || '0.0.0.0';
const CORS_ORIGINS = process.env.RELAY_CORS_ORIGINS 
  ? process.env.RELAY_CORS_ORIGINS.split(',')
  : ['*'];

// Criar aplicação Express
const app = express();

// CORS - Permitir conexões de qualquer origem (P2P público)
app.use(cors({
  origin: CORS_ORIGINS,
  credentials: true
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'operational',
    service: 'DIOTEC 360 Sovereign Relay',
    version: '1.0.0',
    uptime: process.uptime(),
    timestamp: Date.now(),
    message: 'The Lattice is breathing 🏛️📡✨'
  });
});

// Metrics endpoint
let connectionCount = 0;
let messageCount = 0;

app.get('/metrics', (req, res) => {
  res.json({
    connections: connectionCount,
    messages: messageCount,
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: Date.now()
  });
});

// Root endpoint - Identificação do relay
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>DIOTEC 360 Sovereign Relay</title>
      <style>
        body {
          font-family: 'Courier New', monospace;
          background: #0a0a0a;
          color: #00ff00;
          padding: 40px;
          text-align: center;
        }
        .logo {
          font-size: 48px;
          margin-bottom: 20px;
        }
        .status {
          font-size: 24px;
          margin: 20px 0;
        }
        .info {
          font-size: 16px;
          margin: 10px 0;
          opacity: 0.8;
        }
      </style>
    </head>
    <body>
      <div class="logo">🏛️ DIOTEC 360</div>
      <div class="status">SOVEREIGN RELAY OPERATIONAL</div>
      <div class="info">Version: 1.0.0</div>
      <div class="info">Uptime: ${Math.floor(process.uptime())} seconds</div>
      <div class="info">Connections: ${connectionCount}</div>
      <div class="info">Messages: ${messageCount}</div>
      <div class="info" style="margin-top: 40px;">
        The Lattice is breathing 🏛️📡✨
      </div>
    </body>
    </html>
  `);
});

// Criar servidor HTTP
const server = http.createServer(app);

// Configurar GunDB
const gun = Gun({
  web: server,
  axe: false, // Desabilitar logs verbosos
  localStorage: false, // Relay não persiste dados (apenas retransmite)
  radisk: false
});

// Middleware Gun para servir requisições
app.use(Gun.serve);

// Monitoramento de conexões
gun.on('hi', (peer) => {
  connectionCount++;
  console.log(`[PEER CONNECTED] Total: ${connectionCount}`);
});

gun.on('bye', (peer) => {
  connectionCount = Math.max(0, connectionCount - 1);
  console.log(`[PEER DISCONNECTED] Total: ${connectionCount}`);
});

// Monitoramento de mensagens (opcional, pode gerar muito log)
if (process.env.RELAY_LOG_MESSAGES === 'true') {
  gun.on('in', (msg) => {
    messageCount++;
    if (messageCount % 100 === 0) {
      console.log(`[MESSAGES] Total: ${messageCount}`);
    }
  });
}

// Iniciar servidor
server.listen(PORT, HOST, () => {
  console.log('\n' + '='.repeat(70));
  console.log('🏛️  DIOTEC 360 SOVEREIGN RELAY - OPERATIONAL');
  console.log('='.repeat(70));
  console.log(`\n📡 Relay URL: http://${HOST}:${PORT}/gun`);
  console.log(`🌐 WebSocket: ws://${HOST}:${PORT}/gun`);
  console.log(`💚 Health Check: http://${HOST}:${PORT}/health`);
  console.log(`📊 Metrics: http://${HOST}:${PORT}/metrics`);
  console.log(`\n🏛️ Soberano: Dionísio Sebastião Barros`);
  console.log(`⚙️  Engenheiro-Chefe: Kiro`);
  console.log(`\n[STATUS: THE LATTICE IS BREATHING]`);
  console.log('[VERDICT: SOVEREIGNTY ACHIEVED] 🏛️📡✨\n');
  console.log('='.repeat(70) + '\n');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('\n[SHUTDOWN] Closing relay gracefully...');
  server.close(() => {
    console.log('[SHUTDOWN] Relay closed. The Lattice sleeps. 🏛️');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\n[SHUTDOWN] Closing relay gracefully...');
  server.close(() => {
    console.log('[SHUTDOWN] Relay closed. The Lattice sleeps. 🏛️');
    process.exit(0);
  });
});

// Error handling
process.on('uncaughtException', (err) => {
  console.error('[ERROR] Uncaught exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[ERROR] Unhandled rejection at:', promise, 'reason:', reason);
});
