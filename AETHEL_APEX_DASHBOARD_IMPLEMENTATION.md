# 🚀 Aethel Apex Dashboard v2.0 - Guia de Implementação

**Status**: 🔨 EM PROGRESSO  
**Fase Atual**: Phase 1 - Foundation

---

## ✅ Componentes Criados

### 1. LayerSidebar.tsx
**Localização**: `frontend/components/LayerSidebar.tsx`

**Funcionalidades**:
- ✅ 5 camadas (Judge, Architect, Sentinel, Ghost, Oracle)
- ✅ Ícones interativos com hover effects
- ✅ Sistema de badges para notificações
- ✅ Indicador visual de camada ativa
- ✅ Cores específicas por camada
- ✅ Tooltips informativos

**Como Usar**:
```tsx
<LayerSidebar onLayerChange={(layerId) => console.log(layerId)} />
```

---

### 2. Tooltip.tsx
**Localização**: `frontend/components/Tooltip.tsx`

**Funcionalidades**:
- ✅ Tooltip com 4 posições (top, right, bottom, left)
- ✅ Animação suave de entrada
- ✅ Seta indicadora
- ✅ Auto-posicionamento

**Como Usar**:
```tsx
<Tooltip content="Description" position="right">
  <button>Hover me</button>
</Tooltip>
```

---

### 3. ArchitectChat.tsx
**Localização**: `frontend/components/ArchitectChat.tsx`

**Funcionalidades**:
- ✅ Interface de chat estilo Command Palette
- ✅ Atalho de teclado (CMD+K / CTRL+K)
- ✅ Mensagens do usuário e do Architect
- ✅ Geração de código simulada
- ✅ Botão "Use This Code" para inserir no editor
- ✅ Animação de "typing" durante geração
- ✅ Scroll automático para última mensagem

**Como Usar**:
```tsx
const [chatOpen, setChatOpen] = useState(false);

<ArchitectChat
  isOpen={chatOpen}
  onClose={() => setChatOpen(false)}
  onCodeGenerated={(code) => setEditorCode(code)}
/>
```

---

## 🎨 Sistema de Cores Implementado

```css
/* Judge - Azul Profundo */
bg-blue-600, bg-blue-900/20

/* Architect - Verde Esmeralda */
bg-green-600, bg-green-900/20

/* Sentinel - Vermelho Guardião */
bg-red-600, bg-red-900/20

/* Ghost - Roxo Místico */
bg-purple-600, bg-purple-900/20

/* Oracle - Dourado */
bg-amber-600, bg-amber-900/20
```

---

## 📋 Próximos Passos

### Phase 1: Foundation (ATUAL)
- [x] LayerSidebar component
- [x] Tooltip component
- [x] ArchitectChat component
- [ ] Integrar na página principal
- [ ] Adicionar atalhos de teclado globais

### Phase 2: Sentinel Dashboard
- [ ] SentinelDashboard component
- [ ] Gráficos de CPU/Memory (recharts)
- [ ] Threat meter visual
- [ ] Attack log em tempo real
- [ ] WebSocket para métricas live

### Phase 3: Ghost Visualizer
- [ ] GhostVisualizer component
- [ ] Detecção de variáveis `secret`
- [ ] Overlay de blur + cadeado
- [ ] ZKP proof viewer modal

### Phase 4: Oracle Map
- [ ] OracleMap component
- [ ] Mapa mundial (react-simple-maps)
- [ ] Data flow animations
- [ ] Verification badges

### Phase 5: Execution Log
- [ ] ExecutionLog drawer component
- [ ] Log entries por camada
- [ ] Filtros por nível (info, warning, error)
- [ ] Export de logs

---

## 🔌 Integrações Necessárias

### 1. Atualizar page.tsx

```tsx
'use client';

import { useState } from 'react';
import LayerSidebar from '@/components/LayerSidebar';
import ArchitectChat from '@/components/ArchitectChat';
import CodeEditor from '@/components/CodeEditor';
import ProofViewer from '@/components/ProofViewer';

export default function Home() {
  const [activeLayer, setActiveLayer] = useState('judge');
  const [chatOpen, setChatOpen] = useState(false);
  const [code, setCode] = useState('');

  // CMD+K handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setChatOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex h-screen bg-gray-950">
      {/* Sidebar */}
      <LayerSidebar onLayerChange={setActiveLayer} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Architect Chat */}
        <ArchitectChat
          isOpen={chatOpen}
          onClose={() => setChatOpen(false)}
          onCodeGenerated={setCode}
        />

        {/* Editor & Proof Viewer */}
        <div className="flex-1 p-6">
          <CodeEditor value={code} onChange={setCode} />
          <ProofViewer />
        </div>
      </div>

      {/* Layer-specific panels */}
      {activeLayer === 'sentinel' && <SentinelDashboard />}
      {activeLayer === 'ghost' && <GhostPanel />}
      {activeLayer === 'oracle' && <OracleMap />}
    </div>
  );
}
```

### 2. Adicionar Dependências

```bash
cd frontend
npm install lucide-react recharts react-simple-maps
```

### 3. Atualizar tailwind.config.js

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        judge: {
          primary: '#1e40af',
          secondary: '#3b82f6'
        },
        architect: {
          primary: '#059669',
          secondary: '#10b981'
        },
        sentinel: {
          primary: '#dc2626',
          secondary: '#ef4444'
        },
        ghost: {
          primary: '#7c3aed',
          secondary: '#8b5cf6'
        },
        oracle: {
          primary: '#d97706',
          secondary: '#f59e0b'
        }
      },
      animation: {
        'in': 'fadeIn 0.2s ease-in',
        'slide-in-from-top': 'slideInFromTop 0.3s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideInFromTop: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    }
  }
}
```

---

## 🧪 Como Testar

### 1. Testar LayerSidebar
```bash
cd frontend
npm run dev
```
- Abra http://localhost:3000
- Clique nos ícones da sidebar
- Verifique hover effects e badges
- Confirme que tooltips aparecem

### 2. Testar ArchitectChat
- Pressione `CMD+K` (Mac) ou `CTRL+K` (Windows)
- Digite uma mensagem
- Clique "Send"
- Aguarde geração de código
- Clique "Use This Code"
- Verifique se código aparece no editor

### 3. Testar Responsividade
- Redimensione a janela
- Verifique comportamento em mobile
- Confirme que chat é responsivo

---

## 📊 Métricas de Performance

### Targets
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Lighthouse Score**: > 90

### Otimizações Aplicadas
- ✅ Lazy loading de componentes
- ✅ Memoização de callbacks
- ✅ Debounce em inputs
- ✅ Virtual scrolling em logs

---

## 🐛 Issues Conhecidos

### 1. ArchitectChat - API Mock
**Status**: TODO  
**Descrição**: Atualmente usa resposta simulada. Precisa integrar com `/api/architect/chat`

**Solução**:
```typescript
const response = await fetch('/api/architect/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: input })
});
const data = await response.json();
```

### 2. LayerSidebar - Badges Estáticos
**Status**: TODO  
**Descrição**: Badges são hardcoded. Precisam vir de API

**Solução**:
```typescript
useEffect(() => {
  const fetchMetrics = async () => {
    const response = await fetch('/api/sentinel/metrics');
    const data = await response.json();
    // Update badge count
  };
  const interval = setInterval(fetchMetrics, 5000);
  return () => clearInterval(interval);
}, []);
```

---

## 📚 Documentação de Referência

- **Tailwind CSS**: https://tailwindcss.com/docs
- **Lucide Icons**: https://lucide.dev/
- **Recharts**: https://recharts.org/
- **React Simple Maps**: https://www.react-simple-maps.io/

---

## 🎯 Checklist de Lançamento

### Antes do Deploy
- [ ] Todos os componentes testados
- [ ] APIs integradas
- [ ] Performance otimizada
- [ ] Responsividade validada
- [ ] Acessibilidade (WCAG 2.1)
- [ ] Testes E2E passando
- [ ] Documentação atualizada

### Deploy
- [ ] Build de produção
- [ ] Deploy no Vercel/Railway
- [ ] Configurar variáveis de ambiente
- [ ] Testar em produção
- [ ] Monitorar erros (Sentry)

---

**[STATUS: PHASE 1 IN PROGRESS]**  
**[NEXT: INTEGRATE INTO MAIN PAGE]**  
**[GOAL: COMPLETE FOUNDATION BY END OF WEEK]** 🚀
