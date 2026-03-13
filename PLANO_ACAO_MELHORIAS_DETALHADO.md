# Plano de Ação Detalhado - Melhorias do Diotec360 v3.0

**Data**: 11 de Fevereiro de 2026  
**Prioridade**: ALTA - Lançamento Comercial em 7 dias

---

## 🎯 OBJETIVO PRINCIPAL

**Gerar a primeira receita dentro de 7 dias** através do lançamento comercial do Diotec360 v3.0.

---

## 📋 CHECKLIST DE AÇÕES PRIORITÁRIAS

### ✅ FASE 1: DEPLOYMENT DE PRODUÇÃO (Dia 1 - 30 minutos)

#### 1.1 Deploy do Frontend (Vercel)
```bash
# Passos:
1. Acessar vercel.com
2. Conectar repositório GitHub
3. Selecionar pasta `frontend/`
4. Configurar build settings:
   - Framework: Next.js
   - Build Command: npm run build
   - Output Directory: .next
5. Configurar domínio: diotec360-lang.org
6. Deploy automático
```

**Arquivos a verificar**:
- `frontend/package.json` - Dependências corretas
- `frontend/next.config.js` - Configuração Next.js
- `frontend/.env.production` - Variáveis de ambiente

#### 1.2 Deploy do Backend (Railway)
```bash
# Passos:
1. Acessar railway.app
2. Criar novo projeto
3. Conectar repositório GitHub
4. Selecionar pasta `api/`
5. Configurar:
   - Runtime: Python 3.11
   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   - Environment Variables:
     - DATABASE_URL
     - STRIPE_SECRET_KEY
     - PAYPAL_CLIENT_ID
6. Configurar domínio: api.diotec360-lang.org
```

**Arquivos a verificar**:
- `api/main.py` - Aplicação FastAPI
- `api/requirements.txt` - Dependências Python
- `api/Dockerfile` (se existir)

#### 1.3 Configuração de Domínio
```bash
# Passos:
1. Registrar domínio: diotec360-lang.org (se não registrado)
2. Configurar DNS:
   - A record: @ → IP do Vercel
   - CNAME: api → URL do Railway
   - CNAME: www → URL do Vercel
3. Configurar SSL automático
4. Testar acesso: https://diotec360-lang.org
```

---

### ✅ FASE 2: SISTEMA DE PAGAMENTO (Dia 2 - 2 horas)

#### 2.1 Criar Página de Pricing
**Arquivo**: `frontend/app/pricing/page.tsx`

```typescript
// Estrutura básica:
export default function PricingPage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-8">Pricing Plans</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Plano Starter */}
        <PricingCard
          title="Starter"
          price="$10/month"
          description="For developers exploring Aethel"
          features={[
            "100 credits included",
            "Basic proof verification",
            "Community support",
            "Up to 10 proofs/day"
          ]}
          ctaText="Start Free Trial"
          ctaLink="/signup?plan=starter"
        />
        
        {/* Plano Professional */}
        <PricingCard
          title="Professional"
          price="$80/month"
          description="For small teams and projects"
          features={[
            "1,000 credits included",
            "Batch verification",
            "Priority support",
            "Up to 100 proofs/day",
            "Basic monitoring"
          ]}
          ctaText="Start Free Trial"
          ctaLink="/signup?plan=professional"
          highlighted={true}
        />
        
        {/* Plano Enterprise */}
        <PricingCard
          title="Enterprise"
          price="$700/month"
          description="For production systems"
          features={[
            "10,000 credits included",
            "Unlimited verification",
            "24/7 support",
            "Advanced monitoring",
            "Custom integrations",
            "SLA guarantee"
          ]}
          ctaText="Contact Sales"
          ctaLink="/contact"
        />
      </div>
    </div>
  )
}
```

#### 2.2 Integrar Stripe Checkout
**Arquivo**: `frontend/lib/stripe.ts`

```typescript
import { loadStripe } from '@stripe/stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY!)

export async function createCheckoutSession(planId: string, accountId: string) {
  const response = await fetch('/api/stripe/create-checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ planId, accountId })
  })
  
  const { sessionId } = await response.json()
  const stripe = await stripePromise
  
  const { error } = await stripe!.redirectToCheckout({ sessionId })
  
  if (error) {
    console.error('Stripe checkout error:', error)
  }
}
```

**Arquivo**: `api/routes/stripe.py`

```python
from fastapi import APIRouter, HTTPException
import stripe

router = APIRouter(prefix="/stripe")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-checkout")
async def create_checkout_session(plan_id: str, account_id: str):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://diotec360-lang.org/dashboard?success=true',
            cancel_url='https://diotec360-lang.org/pricing?canceled=true',
            metadata={
                'account_id': account_id,
                'plan_id': plan_id
            }
        )
        
        return {"sessionId": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3 Criar Portal do Cliente
**Arquivo**: `frontend/app/dashboard/page.tsx`

```typescript
export default function DashboardPage() {
  const [account, setAccount] = useState(null)
  const [usage, setUsage] = useState(null)
  
  useEffect(() => {
    // Fetch account data
    fetch('/api/billing/account')
      .then(res => res.json())
      .then(setAccount)
    
    // Fetch usage data
    fetch('/api/billing/usage')
      .then(res => res.json())
      .then(setUsage)
  }, [])
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      {/* Credit Balance */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Credit Balance</h2>
        <div className="text-4xl font-bold text-green-400">
          {account?.credits || 0} credits
        </div>
        <p className="text-gray-400 mt-2">
          ${((account?.credits || 0) * 0.10).toFixed(2)} value
        </p>
      </div>
      
      {/* Usage Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Proofs Verified"
          value={usage?.proofs || 0}
          change="+12%"
        />
        <StatCard
          title="Credits Used"
          value={usage?.credits_used || 0}
          change="+8%"
        />
        <StatCard
          title="Cost This Month"
          value={`$${usage?.cost || 0}`}
          change="+5%"
        />
      </div>
      
      {/* Recent Transactions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
        <TransactionTable transactions={account?.transactions || []} />
      </div>
    </div>
  )
}
```

---

### ✅ FASE 3: CORREÇÃO DA GRAMÁTICA (Dia 2 - 1 hora)

#### 3.1 Atualizar Gramática
**Arquivo**: `aethel/core/grammar.py`

```python
# ATUALIZAR PARA:
DIOTEC360_grammar = """
    start: (intent_def | atomic_batch)+
    
    intent_def: "intent" NAME "(" params ")" "{" guard_block solve_block verify_block "}"
    atomic_batch: "atomic_batch" NAME "{" intent_def* "}"
    
    params: (param ("," param)*)?
    param: ["secret"] ["external"] NAME ":" NAME
    
    guard_block: "guard" "{" (condition ";")+ "}"
    solve_block: "solve" "{" (setting ";")+ "}"
    verify_block: "verify" "{" (condition ";")+ "}"
    
    condition: ["secret"] ["external"] expr OPERATOR expr
    setting: NAME ":" NAME
    
    ?expr: term
         | expr "+" term    -> add
         | expr "-" term    -> subtract
    
    ?term: factor
         | term "*" factor  -> multiply
         | term "/" factor  -> divide
         | term "%" factor  -> modulo
    
    ?factor: atom
           | "(" expr ")"
    
    ?atom: NAME
         | NUMBER
    
    OPERATOR: ">=" | "<=" | "==" | "!=" | ">" | "<"
    NUMBER: /-?[0-9]+(\.[0-9]+)?/  # ✅ ATUALIZADO: Suporte a decimais
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    COMMENT: /#[^\\n]*/
    
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
```

#### 3.2 Testar Literais Numéricos
**Arquivo**: `test_grammar_numbers.py`

```python
import sys
sys.path.append('.')
from aethel.core.parser import Parser

def test_number_literals():
    """Testar suporte a literais numéricos"""
    
    test_cases = [
        # Código com números literais
        """
        intent test() {
            guard {
                amount == 100;
                rate == 0.05;
            }
            
            solve {
                priority: security;
            }
            
            verify {
                total == amount * (1 + rate);
            }
        }
        """,
        
        # Código com expressões complexas
        """
        intent calculate() {
            guard {
                base == 1000;
                percentage == 15;
            }
            
            solve {
                target: result;
            }
            
            verify {
                result == base + (base * percentage / 100);
            }
        }
        """
    ]
    
    parser = Parser()
    
    for i, code in enumerate(test_cases, 1):
        try:
            result = parser.parse(code)
            print(f"✅ Teste {i} passou: Números literais funcionando")
            print(f"   AST: {result}")
        except Exception as e:
            print(f"❌ Teste {i} falhou: {e}")
    
    print("\n" + "="*50)
    print("Teste de gramática completo")

if __name__ == "__main__":
    test_number_literals()
```

---

### ✅ FASE 4: INTEGRAÇÃO BILLING-JUDGE (Dia 3 - 1 hora)

#### 4.1 Modificar Judge para Cobrança
**Arquivo**: `aethel/core/judge.py`

```python
# ADICIONAR NO INÍCIO DO ARQUIVO:
from aethel.core.billing import get_billing_kernel, OperationType

# MODIFICAR O MÉTODO verify():
class Judge:
    def verify(self, code: str, account_id: Optional[str] = None):
        """
        Verifica código Aethel com cobrança automática.
        
        Args:
            code: Código Aethel para verificar
            account_id: ID da conta para cobrança (opcional)
        
        Returns:
            Resultado da verificação
        """
        # Se account_id fornecido, cobrar pela verificação
        if account_id:
            billing = get_billing_kernel()
            
            # Calcular complexidade do código (simplificado)
            complexity = self._calculate_complexity(code)
            
            # Cobrar operação
            success, message = billing.charge_operation(
                account_id=account_id,
                operation=OperationType.PROOF_VERIFICATION,
                quantity=complexity,
                metadata={
                    "code_hash": hashlib.sha256(code.encode()).hexdigest(),
                    "lines": len(code.split('\n')),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            if not success:
                return {
                    "status": "BILLING_ERROR",
                    "message": f"Falha na cobrança: {message}",
                    "proof": None
                }
        
        # ... resto da verificação normal ...
```

#### 4.2 Criar Middleware de Cobrança
**Arquivo**: `api/middleware/billing_middleware.py`

```python
from fastapi import Request, HTTPException
from aethel.core.billing import get_billing_kernel

async def billing_middleware(request: Request, call_next):
    """
    Middleware para cobrança automática de API calls.
    """
    # Verificar se é endpoint pago
    if request.url.path.startswith("/api/verify"):
        # Extrair account_id do header ou query param
        account_id = request.headers.get("X-Account-ID") or \
                    request.query_params.get("account_id")
        
        if account_id:
            billing = get_billing_kernel()
            
            # Verificar saldo
            balance = billing.get_account_balance(account_id)
            if balance is None or balance <= 0:
                raise HTTPException(
                    status_code=402,  # Payment Required
                    detail="Insufficient credits. Please purchase more credits."
                )
    
    # Continuar com a requisição
    response = await call_next(request)
    return response
```

---

## 📊 MÉTRICAS DE IMPLEMENTAÇÃO

### Checkpoints Diários

#### Dia 1 - Deployment
- [ ] Frontend deployado em Vercel
- [ ] Backend deployado em Railway
- [ ] Domínio diotec360-lang.org funcionando
- [ ] SSL configurado

#### Dia 2 - Pagamento
- [ ] Página de pricing criada
- [ ] Stripe Checkout integrado
- [ ] Portal do cliente básico
- [ ] Gramática corrigida

#### Dia 3 - Integração
- [ ] Judge integrado com billing
- [ ] Middleware de cobrança funcionando
- [ ] Testes de cobrança passando

#### Dia 4-7 - Polimento
- [ ] Documentação básica
- [ ] Testes end-to-end
- [ ] Monitoramento básico
- [ ] Primeiros testes com clientes

---

## 🚀 COMANDOS PARA EXECUTAR

### Comandos de Deployment
```bash
# 1. Deploy frontend (Vercel)
cd frontend
vercel --prod

# 2. Deploy backend (Railway)
cd api
railway up

# 3. Testar deployment
curl https://diotec360-lang.org/health
curl https://api.diotec360-lang.org/health
```

### Comandos de Teste
```bash
# Testar gramática
python test_grammar_numbers.py

# Testar billing
python demo_billing.py

# Testar integração
python test_billing_integration.py

# Testar end-to-end
python test_e2e.py
```

### Comandos de Monitoramento
```bash
# Iniciar monitor
python scripts/monitor_network.py --nodes node_1,node_2,node_3

# Verificar logs
railway logs
vercel logs
```

---

## 🆘 SOLUÇÃO DE PROBLEMAS COMUNS

### Problema 1: Deployment falha no Vercel
**Solução**:
```bash
# Verificar build localmente
cd frontend
npm run build

# Verificar erros
npm run lint

# Verificar dependências
npm ci
```

### Problema 2: Stripe Checkout não funciona
**Solução**:
```bash
# Verificar chaves Stripe
echo $STRIPE_SECRET_KEY
echo $NEXT_PUBLIC_STRIPE_PUBLIC_KEY

# Testar API localmente
curl -X POST http://localhost:8000/api/stripe/create-checkout \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "price_123", "account_id": "test"}'
```

### Problema 3: Gramática não reconhece números
**Solução**:
```python
# Verificar parser
from aethel.core.parser import Parser
parser = Parser()
result = parser.parse("intent test() { guard { x == 100; } }")
print(result)
```

---

## 📞 SUPORTE E CONTATOS

### Equipe Técnica
- **Dionísio**: Fundador/Arquiteto
- **Kiro**: Assistente de Desenvolvimento AI

### Serviços Externos
- **Vercel**: suporte@vercel.com
- **Railway**: support@railway.app
- **Stripe**: support@stripe.com
- **PayPal**: support@paypal.com

### Monitoramento
- **Status Page**: status.diotec360-lang.org
- **Alertas**: Slack #alerts
- **Métricas**: Grafana dashboard

---

## 🎉 CELEBRAÇÃO DE SUCESSO

### Marcos a Celebrar
1. **Primeiro Deploy**: 🥳 Frontend + Backend online
2. **Primeira Página de Pricing**: 💰 Sistema de preços visível
3. **Primeiro Checkout**: 🛒 Cliente pode pagar
4. **Primeira Verificação Paga**: 🔐 Proof com cobrança
5. **Primeira Receita**: 🏦 Dinheiro na conta

### Métricas de Sucesso
- ✅ Uptime > 99.9%
- ✅ Tempo de resposta < 200ms
- ✅ 0 erros de cobrança
- ✅ 100% testes passando
- ✅ Primeiro pagamento em 7 dias

---

**Documento**: Plano de Ação Detalhado  
**Versão**: 1.0  
**Data**: 11 de Fevereiro de 2026  
**Status**: ✅ Pronto para Execução

**Próximo Passo**: Executar Fase 1 (Deployment) hoje.