# 🌌 Aethel Apex Dashboard v2.0 - Especificação Completa

**Data**: 8 de Fevereiro de 2026  
**Status**: 🚀 DESIGN PHASE  
**Objetivo**: Transformar o "Núcleo de Prova Puro" em "Centro de Comando Agêntico"

---

## 🎯 Visão Geral

O Aethel Studio v1.0 atual é tecnicamente perfeito, mas visualmente é apenas um "editor com botão de verificar". Para ser uma plataforma comercial, precisamos mostrar **visualmente** as 4 camadas que já existem no backend:

1. **🏛️ Judge (Núcleo)** - O que já temos
2. **🤖 Architect (LLM)** - Escondido no backend
3. **🛡️ Sentinel (Monitor)** - Logs invisíveis
4. **🎭 Ghost Protocol (ZKP)** - Sem visualização
5. **🔮 Oracle Sanctuary** - Dados externos sem mapa

---

## 📐 Layout do Dashboard v2.0

```
┌─────────────────────────────────────────────────────────────────┐
│  🌌 AETHEL APEX                    [⚙️ Settings] [👤 Profile]   │
├──────┬──────────────────────────────────────────────────────────┤
│      │  ┌──────────────────────────────────────────────────┐   │
│  🏛️  │  │  💬 Architect Chat (CMD+K)                       │   │
│ Judge│  │  > "Create a payment system with 2% fee"         │   │
│      │  └──────────────────────────────────────────────────┘   │
│──────│                                                           │
│      │  ┌──────────────────────────────────────────────────┐   │
│  🤖  │  │  📝 Code Editor                                   │   │
│Archit│  │  intent transfer(sender: Account...) {           │   │
│      │  │    guard { ... }                                 │   │
│──────│  │    solve { priority: security; }                 │   │
│      │  │    verify { ... }                                │   │
│  🛡️  │  │  }                                                │   │
│Sentin│  └──────────────────────────────────────────────────┘   │
│      │                                                           │
│──────│  ┌──────────────────────────────────────────────────┐   │
│      │  │  🔍 Proof Viewer                                  │   │
│  🎭  │  │  ✅ PROVED in 0.023s                             │   │
│ Ghost│  │  [View Z3 Proof] [View Execution Log]            │   │
│      │  └──────────────────────────────────────────────────┘   │
│──────│                                                           │
│      │  ┌──────────────────────────────────────────────────┐   │
│  🔮  │  │  📊 Live Metrics (Sentinel)                       │   │
│Oracle│  │  CPU: 12% | Memory: 45MB | Threat: LOW           │   │
│      │  └──────────────────────────────────────────────────┘   │
└──────┴──────────────────────────────────────────────────────────┘
```

---

## 🎨 Componentes Novos

### 1. **Sidebar de Camadas** (Esquerda)

```tsx
// frontend/components/LayerSidebar.tsx
interface Layer {
  id: string;
  name: string;
  icon: string;
  active: boolean;
  badge?: number;
}

const layers: Layer[] = [
  { id: 'judge', name: 'Judge', icon: '🏛️', active: true },
  { id: 'architect', name: 'Architect', icon: '🤖', active: false },
  { id: 'sentinel', name: 'Sentinel', icon: '🛡️', active: false, badge: 3 },
  { id: 'ghost', name: 'Ghost', icon: '🎭', active: false },
  { id: 'oracle', name: 'Oracle', icon: '🔮', active: false }
];
```

**Comportamento**:
- Clique em cada ícone abre um painel lateral com detalhes
- Badge mostra alertas/notificações
- Hover mostra tooltip com status

---

### 2. **Architect Chat** (Topo)

```tsx
// frontend/components/ArchitectChat.tsx
// Estilo: Command Palette (CMD+K)

interface ArchitectMessage {
  role: 'user' | 'architect';
  content: string;
  timestamp: Date;
  codeGenerated?: string;
}
```

**Funcionalidades**:
- **Input Natural**: "Create a DeFi liquidation system"
- **Sugestões Inteligentes**: Autocomplete baseado em stdlib
- **Geração de Código**: LLM traduz para Aethel
- **Explicação**: "I created a liquidation intent with oracle verification"

**Atalhos**:
- `CMD+K` / `CTRL+K`: Abrir chat
- `Enter`: Enviar mensagem
- `ESC`: Fechar chat

---

### 3. **Sentinel Dashboard** (Painel Lateral)

```tsx
// frontend/components/SentinelDashboard.tsx

interface SentinelMetrics {
  cpu: number;
  memory: number;
  threatLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  attacksBlocked: number;
  lastScan: Date;
}
```

**Visualizações**:
- **Gráfico de CPU/Memória**: Line chart em tempo real
- **Threat Meter**: Gauge visual (verde → vermelho)
- **Attack Log**: Lista de ataques bloqueados
- **Quarantine**: Códigos em quarentena

**Exemplo Visual**:
```
┌─────────────────────────────┐
│ 🛡️ SENTINEL MONITOR         │
├─────────────────────────────┤
│ CPU Usage:  ████░░░░░░ 42%  │
│ Memory:     ██████░░░░ 67%  │
│ Threat:     ██░░░░░░░░ LOW  │
├─────────────────────────────┤
│ 🚨 Recent Alerts            │
│ • Overflow attempt blocked  │
│ • Trojan pattern detected   │
│ • Reentrancy prevented      │
└─────────────────────────────┘
```

---

### 4. **Ghost Protocol Visualizer** (Overlay no Editor)

```tsx
// frontend/components/GhostVisualizer.tsx

// Quando detecta "secret" no código:
// 1. Blur o valor da variável
// 2. Mostrar ícone de cadeado
// 3. Tooltip: "Protected by ZKP"
```

**Exemplo Visual**:
```aethel
intent verify_treatment(
    patient: Person,
    secret diagnosis: Code  // 🔒 [HIDDEN BY GHOST PROTOCOL]
) {
    guard {
        diagnosis in covered_conditions;  // ✅ Verified without revealing
    }
}
```

**Comportamento**:
- Variáveis `secret` aparecem com fundo escuro + cadeado
- Hover mostra: "This value is never exposed. Verified via ZKP."
- Botão "View Proof" mostra o commitment hash

---

### 5. **Oracle Map** (Painel Lateral)

```tsx
// frontend/components/OracleMap.tsx

interface OracleSource {
  name: string;
  location: string;
  verified: boolean;
  lastUpdate: Date;
  dataType: 'price' | 'weather' | 'event';
}
```

**Visualização**:
- **Mapa Mundial**: Mostra localização dos nós de oracle
- **Data Flow**: Animação mostrando dados chegando
- **Verification Badge**: Selo criptográfico de autenticidade

**Exemplo Visual**:
```
┌─────────────────────────────┐
│ 🔮 ORACLE SANCTUARY         │
├─────────────────────────────┤
│ [🗺️ World Map]              │
│                             │
│ 📍 Chainlink - NYC          │
│    ✅ Verified              │
│    BTC/USD: $45,230         │
│    Updated: 2s ago          │
│                             │
│ 📍 Weather API - London     │
│    ✅ Verified              │
│    Rainfall: 12mm           │
│    Updated: 5m ago          │
└─────────────────────────────┘
```

---

### 6. **Execution Log Drawer** (Inferior)

```tsx
// frontend/components/ExecutionLog.tsx

interface LogEntry {
  timestamp: Date;
  layer: 'judge' | 'architect' | 'sentinel' | 'ghost' | 'oracle';
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
}
```

**Exemplo de Log**:
```
[00:00.001] 🤖 Architect: Translating natural language to Aethel...
[00:00.045] 🏛️ Judge: Parsing intent 'transfer'...
[00:00.067] 🛡️ Sentinel: Scanning for overflow vulnerabilities...
[00:00.089] 🛡️ Sentinel: ✅ No threats detected
[00:00.112] 🏛️ Judge: Generating Z3 constraints...
[00:00.234] 🏛️ Judge: ✅ PROVED (sat)
[00:00.235] 📊 Execution complete in 234ms
```

---

## 🎨 Design System

### Cores por Camada

```css
/* Judge - Azul Profundo (Autoridade) */
--judge-primary: #1e40af;
--judge-secondary: #3b82f6;

/* Architect - Verde Esmeralda (Criação) */
--architect-primary: #059669;
--architect-secondary: #10b981;

/* Sentinel - Vermelho Guardião (Proteção) */
--sentinel-primary: #dc2626;
--sentinel-secondary: #ef4444;

/* Ghost - Roxo Místico (Privacidade) */
--ghost-primary: #7c3aed;
--ghost-secondary: #8b5cf6;

/* Oracle - Dourado (Sabedoria) */
--oracle-primary: #d97706;
--oracle-secondary: #f59e0b;
```

### Tipografia

```css
/* Headers */
--font-display: 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Tamanhos */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
```

---

## 🔌 API Endpoints Necessários

### 1. Architect Chat
```typescript
POST /api/architect/chat
{
  "message": "Create a payment system with 2% fee",
  "context": { "currentCode": "..." }
}

Response:
{
  "reply": "I'll create a payment intent with a 2% fee...",
  "generatedCode": "intent payment(...) { ... }",
  "explanation": "This intent ensures..."
}
```

### 2. Sentinel Metrics
```typescript
GET /api/sentinel/metrics

Response:
{
  "cpu": 42,
  "memory": 67,
  "threatLevel": "LOW",
  "attacksBlocked": 3,
  "recentAlerts": [...]
}
```

### 3. Ghost Protocol Status
```typescript
GET /api/ghost/status?intentId=abc123

Response:
{
  "secretVariables": ["diagnosis", "patient_balance"],
  "zkpProofs": [...],
  "commitments": [...]
}
```

### 4. Oracle Data
```typescript
GET /api/oracle/sources

Response:
{
  "sources": [
    {
      "name": "Chainlink",
      "location": "NYC",
      "verified": true,
      "data": { "BTC/USD": 45230 }
    }
  ]
}
```

---

## 📱 Responsividade

### Desktop (>1280px)
- Sidebar visível
- 3 colunas: Sidebar | Editor | Painel Lateral

### Tablet (768px - 1280px)
- Sidebar colapsada (apenas ícones)
- 2 colunas: Editor | Painel Lateral

### Mobile (<768px)
- Sidebar em drawer (hamburguer menu)
- 1 coluna: Editor full-width
- Painéis laterais em modal

---

## 🚀 Roadmap de Implementação

### Phase 1: Foundation (Semana 1)
- [ ] Criar LayerSidebar component
- [ ] Implementar sistema de cores por camada
- [ ] Adicionar ícones e badges

### Phase 2: Architect Chat (Semana 2)
- [ ] Command Palette (CMD+K)
- [ ] Integração com LLM backend
- [ ] Geração de código em tempo real

### Phase 3: Sentinel Dashboard (Semana 3)
- [ ] Gráficos de CPU/Memory
- [ ] Threat meter visual
- [ ] Attack log em tempo real

### Phase 4: Ghost Visualizer (Semana 4)
- [ ] Blur de variáveis secret
- [ ] Overlay de cadeados
- [ ] ZKP proof viewer

### Phase 5: Oracle Map (Semana 5)
- [ ] Mapa mundial interativo
- [ ] Data flow animations
- [ ] Verification badges

### Phase 6: Polish & Deploy (Semana 6)
- [ ] Execution log drawer
- [ ] Responsividade mobile
- [ ] Performance optimization
- [ ] Deploy to production

---

## 💰 Impacto Comercial

### Antes (v1.0)
- "É só um editor de código"
- Difícil de entender o valor
- Parece um projeto acadêmico

### Depois (v2.0)
- "É um centro de comando de segurança"
- Valor visual imediato
- Parece uma plataforma enterprise

### Pricing Justificado
- **$500/mês**: Acesso a todas as camadas
- **$1000/mês**: + Sentinel em tempo real
- **$2500/mês**: + Suporte dedicado + Custom oracles

---

## 🎯 Métricas de Sucesso

1. **Engagement**: Tempo médio na plataforma > 15min
2. **Conversão**: Trial → Paid > 25%
3. **Retenção**: Churn < 5% ao mês
4. **NPS**: > 50 (promotores)

---

**[STATUS: DESIGN COMPLETE]**  
**[NEXT: START IMPLEMENTATION]**  
**[GOAL: TRANSFORM AETHEL INTO $500/MONTH PLATFORM]** 🌌✨💻
