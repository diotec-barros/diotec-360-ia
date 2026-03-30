/**
 * 🚀 DIOTEC SENTINEL v14.0 - Interface de Pensamento
 * 
 * Mostra o Sentinel decidindo em tempo real:
 * - Análise de prompt
 * - Escolha de modelos (Writer/Critic)
 * - Pipeline execution (RAG → Writer → Critic → Z3)
 * - Auto-correção se necessário
 * 
 * Esta é a "mente visível" do Sentinel.
 */

"use client";

import { useState, useEffect } from 'react';
import { 
  Brain, 
  Zap, 
  Search, 
  Code, 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Loader2,
  TrendingUp,
  Clock,
  DollarSign
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

type PipelineStage = 
  | 'analyzing'
  | 'routing'
  | 'rag'
  | 'writing'
  | 'reviewing'
  | 'verifying'
  | 'healing'
  | 'complete'
  | 'error';

type PromptType = 'frontend' | 'backend' | 'logic' | 'security' | 'unknown';

interface ModelChoice {
  writer: {
    provider: string;
    model: string;
    successRate: number;
    avgTime: number;
  };
  critic: {
    provider: string;
    model: string;
    successRate: number;
    avgTime: number;
  };
  estimatedCost: number;
  estimatedTime: number;
}

interface RAGResult {
  functionsFound: number;
  relevantFiles: string[];
  contextSize: number;
}

interface Z3Result {
  verdict: 'PROVED' | 'UNSAT' | 'TIMEOUT' | 'ERROR';
  proof?: string;
  error?: string;
}

interface SentinelState {
  stage: PipelineStage;
  promptType: PromptType;
  modelChoice?: ModelChoice;
  ragResult?: RAGResult;
  writerOutput?: string;
  criticReview?: string;
  criticRisk?: 'low' | 'medium' | 'high';
  z3Result?: Z3Result;
  healingAttempt?: number;
  startTime: number;
  error?: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

interface SentinelThinkingPanelProps {
  isVisible: boolean;
  prompt: string;
  onComplete?: (code: string) => void;
  onError?: (error: string) => void;
}

export default function SentinelThinkingPanel({
  isVisible,
  prompt,
  onComplete,
  onError
}: SentinelThinkingPanelProps) {
  const [state, setState] = useState<SentinelState>(() => ({
    stage: 'analyzing',
    promptType: 'unknown',
    startTime: Date.now()
  }));
  
  const [elapsedTime, setElapsedTime] = useState(0);

  // Simulate Sentinel thinking process
  useEffect(() => {
    if (!isVisible || !prompt) return;

    executeSentinelPipeline(prompt, setState, onComplete, onError);
  }, [isVisible, prompt, onComplete, onError]);
  
  // Update elapsed time every second
  useEffect(() => {
    if (!isVisible) return;
    
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - state.startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isVisible, state.startTime]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-linear-to-br from-gray-900 via-purple-900/20 to-gray-900 rounded-2xl shadow-2xl border border-purple-500/30 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-purple-500/30 bg-linear-to-r from-purple-900/40 to-pink-900/40">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Brain className="w-8 h-8 text-purple-400" />
                {state.stage !== 'complete' && state.stage !== 'error' && (
                  <div className="absolute -top-1 -right-1">
                    <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                  </div>
                )}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">SENTINEL</h2>
                <p className="text-sm text-purple-300">Interface de Pensamento</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-gray-300">{elapsedTime}s</span>
              </div>
              {state.modelChoice && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300">${state.modelChoice.estimatedCost.toFixed(3)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pipeline Stages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          
          {/* Stage 1: Analyzing Prompt */}
          <StageCard
            icon={<Search className="w-5 h-5" />}
            title="1. Analisando Prompt"
            status={getStageStatus('analyzing', state.stage)}
          >
            {state.promptType !== 'unknown' && (
              <div className="mt-2 text-sm">
                <span className="text-gray-400">Tipo detectado: </span>
                <span className="text-purple-400 font-semibold">
                  {state.promptType.toUpperCase()}
                </span>
              </div>
            )}
          </StageCard>

          {/* Stage 2: Routing (Model Selection) */}
          <StageCard
            icon={<TrendingUp className="w-5 h-5" />}
            title="2. Escolhendo Modelos (Roteamento Dinâmico)"
            status={getStageStatus('routing', state.stage)}
          >
            {state.modelChoice && (
              <div className="mt-3 space-y-3">
                <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-400 font-semibold">✍️ Writer</span>
                    <span className="text-xs text-gray-400">
                      {state.modelChoice.writer.successRate}% success
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">
                    {state.modelChoice.writer.provider} - {state.modelChoice.writer.model}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Avg: {state.modelChoice.writer.avgTime}s
                  </div>
                </div>
                
                <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-purple-400 font-semibold">🔍 Critic</span>
                    <span className="text-xs text-gray-400">
                      {state.modelChoice.critic.successRate}% success
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">
                    {state.modelChoice.critic.provider} - {state.modelChoice.critic.model}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Avg: {state.modelChoice.critic.avgTime}s
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-700">
                  <span>Tempo estimado: {state.modelChoice.estimatedTime}s</span>
                  <span>Custo estimado: ${state.modelChoice.estimatedCost.toFixed(3)}</span>
                </div>
              </div>
            )}
          </StageCard>

          {/* Stage 3: RAG (Grounding) */}
          <StageCard
            icon={<Search className="w-5 h-5" />}
            title="3. RAG - Buscando Contexto Real (87k LOC)"
            status={getStageStatus('rag', state.stage)}
          >
            {state.ragResult && (
              <div className="mt-2 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Funções encontradas:</span>
                  <span className="text-green-400 font-semibold">
                    {state.ragResult.functionsFound}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Arquivos relevantes:</span>
                  <span className="text-green-400 font-semibold">
                    {state.ragResult.relevantFiles.length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Contexto:</span>
                  <span className="text-green-400 font-semibold">
                    {(state.ragResult.contextSize / 1024).toFixed(1)}KB
                  </span>
                </div>
                {state.ragResult.relevantFiles.length > 0 && (
                  <div className="mt-2 text-xs text-gray-500">
                    {state.ragResult.relevantFiles.slice(0, 3).join(', ')}
                    {state.ragResult.relevantFiles.length > 3 && '...'}
                  </div>
                )}
              </div>
            )}
          </StageCard>

          {/* Stage 4: Writer */}
          <StageCard
            icon={<Code className="w-5 h-5" />}
            title="4. Writer - Gerando Código"
            status={getStageStatus('writing', state.stage)}
          >
            {state.writerOutput && (
              <div className="mt-2 text-sm text-gray-400">
                Código gerado: {state.writerOutput.split('\n').length} linhas
              </div>
            )}
          </StageCard>

          {/* Stage 5: Critic */}
          <StageCard
            icon={<Shield className="w-5 h-5" />}
            title="5. Critic - Revisando Código"
            status={getStageStatus('reviewing', state.stage)}
          >
            {state.criticRisk && (
              <div className="mt-2 flex items-center space-x-2">
                <span className="text-gray-400 text-sm">Risk Level:</span>
                <span className={`text-sm font-semibold ${
                  state.criticRisk === 'low' ? 'text-green-400' :
                  state.criticRisk === 'medium' ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {state.criticRisk.toUpperCase()}
                </span>
              </div>
            )}
          </StageCard>

          {/* Stage 6: Z3 Judge */}
          <StageCard
            icon={<Zap className="w-5 h-5" />}
            title="6. Z3 Judge - Verificação Matemática"
            status={getStageStatus('verifying', state.stage)}
          >
            {state.z3Result && (
              <div className="mt-2">
                <div className="flex items-center space-x-2">
                  {state.z3Result.verdict === 'PROVED' ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                  <span className={`text-sm font-semibold ${
                    state.z3Result.verdict === 'PROVED' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {state.z3Result.verdict}
                  </span>
                </div>
                {state.z3Result.error && (
                  <div className="mt-2 text-xs text-red-400">
                    {state.z3Result.error}
                  </div>
                )}
              </div>
            )}
          </StageCard>

          {/* Stage 7: Self-Healing (if needed) */}
          {state.stage === 'healing' && (
            <StageCard
              icon={<AlertTriangle className="w-5 h-5" />}
              title="7. Auto-Correção (Self-Healing)"
              status="active"
            >
              <div className="mt-2 space-y-2">
                <div className="text-sm text-yellow-400">
                  Z3 encontrou erro. Corrigindo automaticamente...
                </div>
                <div className="text-xs text-gray-400">
                  Tentativa {state.healingAttempt || 1} de 3
                </div>
              </div>
            </StageCard>
          )}

          {/* Complete */}
          {state.stage === 'complete' && (
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <div>
                  <div className="text-green-400 font-semibold">
                    ✅ Código Gerado e Verificado!
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    Tempo total: {elapsedTime}s | Selo Z3: PROVED
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {state.stage === 'error' && state.error && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <XCircle className="w-6 h-6 text-red-400" />
                <div>
                  <div className="text-red-400 font-semibold">
                    ❌ Erro na Geração
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    {state.error}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

interface StageCardProps {
  icon: React.ReactNode;
  title: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  children?: React.ReactNode;
}

function StageCard({ icon, title, status, children }: StageCardProps) {
  const borderColor = 
    status === 'complete' ? 'border-green-500/50' :
    status === 'active' ? 'border-purple-500/50' :
    status === 'error' ? 'border-red-500/50' :
    'border-gray-700';

  const bgColor =
    status === 'complete' ? 'bg-green-900/10' :
    status === 'active' ? 'bg-purple-900/20' :
    status === 'error' ? 'bg-red-900/10' :
    'bg-gray-900/50';

  return (
    <div className={`border ${borderColor} ${bgColor} rounded-lg p-4 transition-all duration-300`}>
      <div className="flex items-center space-x-3">
        <div className={`${
          status === 'complete' ? 'text-green-400' :
          status === 'active' ? 'text-purple-400' :
          status === 'error' ? 'text-red-400' :
          'text-gray-600'
        }`}>
          {icon}
        </div>
        <div className="flex-1">
          <h3 className={`font-semibold ${
            status === 'complete' ? 'text-green-400' :
            status === 'active' ? 'text-purple-400' :
            status === 'error' ? 'text-red-400' :
            'text-gray-500'
          }`}>
            {title}
          </h3>
        </div>
        {status === 'active' && (
          <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
        )}
        {status === 'complete' && (
          <CheckCircle className="w-5 h-5 text-green-400" />
        )}
        {status === 'error' && (
          <XCircle className="w-5 h-5 text-red-400" />
        )}
      </div>
      {children && (
        <div className="mt-3">
          {children}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getStageStatus(
  targetStage: PipelineStage,
  currentStage: PipelineStage
): 'pending' | 'active' | 'complete' | 'error' {
  const stageOrder: PipelineStage[] = [
    'analyzing', 'routing', 'rag', 'writing', 'reviewing', 'verifying', 'healing', 'complete'
  ];

  if (currentStage === 'error') return 'error';

  const targetIndex = stageOrder.indexOf(targetStage);
  const currentIndex = stageOrder.indexOf(currentStage);

  if (currentIndex < targetIndex) return 'pending';
  if (currentIndex === targetIndex) return 'active';
  return 'complete';
}

// ============================================================================
// SENTINEL PIPELINE EXECUTION (SIMULATED)
// ============================================================================

async function executeSentinelPipeline(
  prompt: string,
  setState: React.Dispatch<React.SetStateAction<SentinelState>>,
  onComplete?: (code: string) => void,
  onError?: (error: string) => void
) {
  try {
    // Stage 1: Analyzing
    await sleep(800);
    const promptType = analyzePromptType(prompt);
    setState(prev => ({ ...prev, stage: 'routing', promptType }));

    // Stage 2: Routing
    await sleep(600);
    const modelChoice = selectModels(promptType);
    setState(prev => ({ ...prev, stage: 'rag', modelChoice }));

    // Stage 3: RAG
    await sleep(1000);
    const ragResult = await performRAG(prompt);
    setState(prev => ({ ...prev, stage: 'writing', ragResult }));

    // Stage 4: Writing
    await sleep(2000);
    const writerOutput = `// Generated code\nfunction secureDeposit(amount: number) {\n  assert(amount > 0);\n  return amount;\n}`;
    setState(prev => ({ ...prev, stage: 'reviewing', writerOutput }));

    // Stage 5: Reviewing
    await sleep(1500);
    const criticRisk: 'low' | 'medium' | 'high' = 'low';
    setState(prev => ({ ...prev, stage: 'verifying', criticRisk }));

    // Stage 6: Z3 Verification
    await sleep(1200);
    const z3Result: Z3Result = { verdict: 'PROVED', proof: '0xabc123...' };
    setState(prev => ({ ...prev, stage: 'complete', z3Result }));

    // Complete
    if (onComplete) {
      onComplete(writerOutput);
    }

  } catch (error) {
    setState(prev => ({ 
      ...prev, 
      stage: 'error', 
      error: error instanceof Error ? error.message : 'Unknown error'
    }));
    if (onError) {
      onError(error instanceof Error ? error.message : 'Unknown error');
    }
  }
}

function analyzePromptType(prompt: string): PromptType {
  const lower = prompt.toLowerCase();
  if (lower.includes('react') || lower.includes('component') || lower.includes('ui')) {
    return 'frontend';
  }
  if (lower.includes('api') || lower.includes('endpoint') || lower.includes('server')) {
    return 'backend';
  }
  if (lower.includes('z3') || lower.includes('proof') || lower.includes('verify')) {
    return 'logic';
  }
  if (lower.includes('security') || lower.includes('auth') || lower.includes('encrypt')) {
    return 'security';
  }
  return 'unknown';
}

function selectModels(promptType: PromptType): ModelChoice {
  // Simulated benchmark data
  if (promptType === 'frontend') {
    return {
      writer: { provider: 'OpenAI', model: 'gpt-4o', successRate: 95, avgTime: 6 },
      critic: { provider: 'Anthropic', model: 'claude-3.5-sonnet', successRate: 98, avgTime: 4 },
      estimatedCost: 0.04,
      estimatedTime: 10
    };
  }
  if (promptType === 'logic') {
    return {
      writer: { provider: 'Anthropic', model: 'claude-3-opus', successRate: 99, avgTime: 8 },
      critic: { provider: 'OpenAI', model: 'gpt-4', successRate: 97, avgTime: 5 },
      estimatedCost: 0.08,
      estimatedTime: 13
    };
  }
  // Default
  return {
    writer: { provider: 'OpenAI', model: 'gpt-4', successRate: 92, avgTime: 7 },
    critic: { provider: 'Anthropic', model: 'claude-3.5-sonnet', successRate: 95, avgTime: 4 },
    estimatedCost: 0.05,
    estimatedTime: 11
  };
}

async function performRAG(prompt: string): Promise<RAGResult> {
  // Simulated RAG search (prompt parameter reserved for future implementation)
  void prompt;
  return {
    functionsFound: 3,
    relevantFiles: ['treasury.py', 'agent_store.py', 'royalty_splitter.py'],
    contextSize: 4096
  };
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
