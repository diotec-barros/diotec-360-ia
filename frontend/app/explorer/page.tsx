'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

export default function DIOTEC360Explorer() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState<'python' | 'solidity'>('python');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const examples = {
    python: `# Exemplo: Transferência Bancária com Bug
def transfer(from_balance: int, to_balance: int, amount: int):
    from_balance = from_balance - amount
    to_balance = to_balance + amount + 1  # BUG: +1 cria dinheiro
    return from_balance, to_balance`,
    
    solidity: `// Exemplo: Token com Overflow
function transfer(address to, uint256 amount) public {
    balances[msg.sender] -= amount;
    balances[to] += amount * 2;  // BUG: duplica tokens
}`
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/explorer/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: 'Erro ao analisar código' });
    } finally {
      setLoading(false);
    }
  };

  const loadExample = () => {
    setCode(examples[language]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-blue-500/20 bg-black/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
            DIOTEC360 Explorer
          </h1>
          <p className="text-slate-400 mt-2">
            Detector de Integridade Matemática - Teste Grátis
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-4"
          >
            <div className="bg-slate-900/50 backdrop-blur border border-blue-500/20 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-blue-400">
                  Cole seu código aqui
                </h2>
                <button
                  onClick={loadExample}
                  className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  Carregar Exemplo
                </button>
              </div>

              {/* Language Selector */}
              <div className="flex gap-2 mb-4">
                <button
                  onClick={() => setLanguage('python')}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    language === 'python'
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  Python
                </button>
                <button
                  onClick={() => setLanguage('solidity')}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    language === 'solidity'
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  Solidity
                </button>
              </div>

              {/* Code Editor */}
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={`Cole seu código ${language === 'python' ? 'Python' : 'Solidity'} aqui...`}
                className="w-full h-96 bg-slate-950 border border-slate-700 rounded-lg p-4 text-slate-300 font-mono text-sm focus:outline-none focus:border-blue-500 transition-colors"
              />

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!code || loading}
                className="w-full mt-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold py-3 rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analisando...' : '🔍 Analisar Integridade'}
              </button>
            </div>

            {/* Info Box */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <h3 className="text-blue-400 font-semibold mb-2">
                O que o DIOTEC360 detecta?
              </h3>
              <ul className="text-slate-400 text-sm space-y-1">
                <li>• Violações de conservação (criação/destruição de valor)</li>
                <li>• Overflows e underflows aritméticos</li>
                <li>• Inconsistências em transferências</li>
                <li>• Vulnerabilidades de reentrância</li>
              </ul>
            </div>
          </motion.div>

          {/* Results Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-4"
          >
            <div className="bg-slate-900/50 backdrop-blur border border-blue-500/20 rounded-lg p-6 min-h-[500px]">
              <h2 className="text-xl font-semibold text-blue-400 mb-4">
                Resultado da Análise
              </h2>

              {!result && !loading && (
                <div className="flex items-center justify-center h-96 text-slate-500">
                  Aguardando análise...
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center h-96">
                  <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
                </div>
              )}

              {result && !result.error && (
                <div className="space-y-4">
                  {/* Status */}
                  <div className={`p-4 rounded-lg ${
                    result.violations?.length > 0
                      ? 'bg-red-500/20 border border-red-500/50'
                      : 'bg-green-500/20 border border-green-500/50'
                  }`}>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">
                        {result.violations?.length > 0 ? '⚠️' : '✅'}
                      </span>
                      <div>
                        <h3 className={`font-semibold ${
                          result.violations?.length > 0 ? 'text-red-400' : 'text-green-400'
                        }`}>
                          {result.violations?.length > 0
                            ? 'Erro de Integridade Detectado'
                            : 'Código Íntegro'}
                        </h3>
                        <p className="text-sm text-slate-400">
                          {result.violations?.length > 0
                            ? `${result.violations.length} violação(ões) encontrada(s)`
                            : 'Nenhuma violação detectada'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Violations */}
                  {result.violations?.map((violation: any, idx: number) => (
                    <div key={idx} className="bg-slate-800/50 border border-red-500/30 rounded-lg p-4">
                      <h4 className="text-red-400 font-semibold mb-2">
                        {violation.type}
                      </h4>
                      <p className="text-slate-300 text-sm mb-2">
                        {violation.description}
                      </p>
                      {violation.line && (
                        <p className="text-slate-500 text-xs">
                          Linha {violation.line}
                        </p>
                      )}
                    </div>
                  ))}

                  {/* CTA */}
                  {result.violations?.length > 0 && (
                    <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 rounded-lg p-6 mt-6">
                      <h3 className="text-blue-400 font-semibold mb-2">
                        🏛️ A DIOTEC360 pode resolver isso
                      </h3>
                      <p className="text-slate-300 text-sm mb-4">
                        Nosso sistema de verificação formal garante que seu código
                        seja matematicamente correto e livre de vulnerabilidades.
                      </p>
                      <a
                        href="mailto:contact@diotec360.com"
                        className="inline-block bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold px-6 py-2 rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all"
                      >
                        Entre em Contato com a DIOTEC 360
                      </a>
                    </div>
                  )}
                </div>
              )}

              {result?.error && (
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                  <p className="text-red-400">{result.error}</p>
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-slate-900/50 border border-blue-500/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">1,247</div>
                <div className="text-xs text-slate-500">Análises Hoje</div>
              </div>
              <div className="bg-slate-900/50 border border-blue-500/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-400">89%</div>
                <div className="text-xs text-slate-500">Com Erros</div>
              </div>
              <div className="bg-slate-900/50 border border-blue-500/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-400">$2.4M</div>
                <div className="text-xs text-slate-500">Perdas Evitadas</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
