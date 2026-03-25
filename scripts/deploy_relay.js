#!/usr/bin/env node
/**
 * DIOTEC 360 IA - Sovereign Relay Deployment Script
 * 
 * Este script prepara e implanta o seu próprio relay GunDB
 * para soberania total sobre a rede Lattice.
 * 
 * "O Soberano Controla Seu Próprio Farol"
 * 
 * Uso:
 *   node scripts/deploy_relay.js
 * 
 * Pré-requisitos:
 *   - Node.js instalado
 *   - Servidor com IP público (VPS, AWS, Azure, etc.)
 *   - Domínio configurado (gun-relay.diotec360.com)
 */

const fs = require('fs');
const path = require('path');

console.log('🏛️ DIOTEC 360 IA - Sovereign Relay Deployment');
console.log('================================================\n');

// Verificar se o diretório relay existe
const relayDir = path.join(__dirname, '..', 'relay');

if (!fs.existsSync(relayDir)) {
  console.error('❌ Diretório relay/ não encontrado!');
  console.log('\n📋 Criando estrutura do relay...\n');
  
  // Criar diretório
  fs.mkdirSync(relayDir, { recursive: true });
  
  // Criar package.json
  const packageJson = {
    name: 'diotec360-gundb-relay',
    version: '1.0.0',
    description: 'DIOTEC 360 IA Sovereign GunDB Relay',
    main: 'server.js',
    scripts: {
      start: 'node server.js',
      dev: 'nodemon server.js'
    },
    dependencies: {
      gun: '^0.2020.1240',
      express: '^4.18.2',
      cors: '^2.8.5'
    },
    devDependencies: {
      nodemon: '^3.0.1'
    }
  };
  
  fs.writeFileSync(
    path.join(relayDir, 'package.json'),
    JSON.stringify(packageJson, null, 2)
  );
  
  // Criar server.js
  const serverJs = `/**
 * DIOTEC 360 IA - Sovereign GunDB Relay Server
 * 
 * Este é o farol soberano da rede Lattice.
 * Todos os nós DIOTEC 360 se conectam aqui para sincronização P2P.
 */

const express = require('express');
const Gun = require('gun');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 8765;

// CORS - Permitir todos os domínios DIOTEC 360
app.use(cors({
  origin: [
    'https://diotec360.com',
    'https://www.diotec360.com',
    'https://app.diotec360.com',
    'https://aethel.diotec360.com',
    'http://localhost:3000',
    'http://localhost:8000'
  ],
  credentials: true
}));

// Servir arquivos estáticos (opcional)
app.use(express.static('public'));

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'operational',
    service: 'DIOTEC 360 IA Sovereign Relay',
    version: '1.0.0',
    timestamp: Date.now()
  });
});

// Inicializar GunDB
const server = app.listen(port, () => {
  console.log('🏛️ DIOTEC 360 IA Sovereign Relay');
  console.log('================================');
  console.log(\`📡 Listening on port \${port}\`);
  console.log('🌍 Ready to serve the Lattice');
  console.log('⚖️ THE SOVEREIGN JUDGE WATCHES\\n');
});

// Attach Gun to Express server
Gun({ web: server });

console.log('✅ GunDB relay initialized');
console.log('🔗 Peers can connect via: ws://your-domain.com:' + port + '/gun');
`;
  
  fs.writeFileSync(path.join(relayDir, 'server.js'), serverJs);
  
  // Criar .env.example
  const envExample = `# DIOTEC 360 IA - Sovereign Relay Configuration
PORT=8765

# Opcional: Configurar autenticação
# RELAY_AUTH_TOKEN=your-secret-token-here
`;
  
  fs.writeFileSync(path.join(relayDir, '.env.example'), envExample);
  
  // Criar README
  const readme = `# DIOTEC 360 IA - Sovereign GunDB Relay

Este é o relay soberano da rede Lattice DIOTEC 360.

## Instalação

\`\`\`bash
cd relay
npm install
\`\`\`

## Desenvolvimento Local

\`\`\`bash
npm run dev
\`\`\`

## Produção

\`\`\`bash
npm start
\`\`\`

## Deploy em VPS

1. Copie esta pasta para seu servidor
2. Configure o domínio (gun-relay.diotec360.com)
3. Configure SSL/TLS (Let's Encrypt)
4. Execute: \`npm install && npm start\`
5. Configure PM2 para auto-restart:
   \`\`\`bash
   npm install -g pm2
   pm2 start server.js --name diotec360-relay
   pm2 save
   pm2 startup
   \`\`\`

## Configuração no Frontend

Atualize o .env.local:

\`\`\`
NEXT_PUBLIC_GUNDB_RELAY=wss://gun-relay.diotec360.com/gun
\`\`\`

## Soberania Total Alcançada 🏛️

Agora você controla seu próprio farol da rede!
`;
  
  fs.writeFileSync(path.join(relayDir, 'README.md'), readme);
  
  console.log('✅ Estrutura do relay criada com sucesso!\n');
}

console.log('📋 Status do Relay:');
console.log('==================\n');

// Verificar arquivos
const files = ['package.json', 'server.js', '.env.example', 'README.md'];
files.forEach(file => {
  const exists = fs.existsSync(path.join(relayDir, file));
  console.log(`${exists ? '✅' : '❌'} ${file}`);
});

console.log('\n🚀 Próximos Passos:');
console.log('===================\n');
console.log('1. cd relay');
console.log('2. npm install');
console.log('3. npm run dev (para testar localmente)');
console.log('\n📡 Para deploy em produção:');
console.log('   - Configure um VPS (DigitalOcean, AWS, Azure)');
console.log('   - Aponte gun-relay.diotec360.com para o IP do servidor');
console.log('   - Configure SSL com Let\'s Encrypt');
console.log('   - Execute: npm start');
console.log('\n🏛️ SOBERANIA TOTAL AGUARDA\n');
