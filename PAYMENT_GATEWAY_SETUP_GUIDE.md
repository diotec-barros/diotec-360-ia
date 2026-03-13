# Guia de Configuração - Payment Gateway DIOTEC 360
## PayPal + Multicaixa Express

**Data**: 10 de Fevereiro de 2026  
**Status**: Pronto para Produção  
**Autor**: Dionísio Sebastião Barros

---

## 🎯 Objetivo

Configurar o sistema de pagamentos para receber dinheiro real de clientes via:
1. **PayPal** (clientes internacionais - USD, EUR, etc.)
2. **Multicaixa Express** (clientes angolanos - AOA)

---

## 📋 Pré-requisitos

### Documentos Necessários

- ✅ NIF (Número de Identificação Fiscal)
- ✅ Bilhete de Identidade ou Passaporte
- ✅ Comprovativo de Morada
- ✅ Conta bancária empresarial (recomendado)

### Informações da Empresa

- Nome: DIOTEC 360
- Website: diotec360.com
- Email: payments@diotec360.com
- Telefone: +244 XXX XXX XXX

---

## 1. Configurar PayPal Business

### Passo 1.1: Criar Conta PayPal Business

1. Acesse: https://www.paypal.com/ao/business
2. Clique em "Criar Conta Business"
3. Preencha os dados:
   - Tipo de negócio: Tecnologia/Software
   - Nome da empresa: DIOTEC 360
   - Email: payments@diotec360.com
   - Telefone: +244 XXX XXX XXX

### Passo 1.2: Verificar Conta

1. Confirme email
2. Adicione conta bancária
3. Verifique identidade (envie documentos)
4. Aguarde aprovação (1-3 dias úteis)

### Passo 1.3: Obter Credenciais API

1. Acesse: https://developer.paypal.com
2. Login com sua conta PayPal Business
3. Vá para "Dashboard" → "My Apps & Credentials"
4. Clique em "Create App"
5. Nome da app: "DIOTEC 360 Payment Gateway"
6. Copie as credenciais:
   - **Client ID**: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`
   - **Secret**: `EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`

### Passo 1.4: Configurar Webhooks

1. No PayPal Developer Dashboard
2. Selecione sua app
3. Vá para "Webhooks"
4. Adicione webhook URL: `https://diotec360.com/api/payment/paypal/webhook`
5. Selecione eventos:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `PAYMENT.CAPTURE.REFUNDED`

### Passo 1.5: Testar em Sandbox

```python
# Configuração de teste
config = {
    "paypal": {
        "client_id": "YOUR_SANDBOX_CLIENT_ID",
        "client_secret": "YOUR_SANDBOX_SECRET",
        "sandbox": True  # Modo teste
    }
}
```

Teste com contas sandbox:
- Comprador: sb-buyer@personal.example.com
- Senha: (gerada no PayPal Sandbox)

### Passo 1.6: Ativar Produção

Quando tudo funcionar em sandbox:

```python
config = {
    "paypal": {
        "client_id": "YOUR_LIVE_CLIENT_ID",
        "client_secret": "YOUR_LIVE_SECRET",
        "sandbox": False  # PRODUÇÃO
    }
}
```

---

## 2. Configurar Multicaixa Express

### Passo 2.1: Criar Conta Merchant

1. Contacte Multicaixa:
   - Email: comercial@multicaixa.ao
   - Telefone: +244 222 638 900
   - Website: https://www.multicaixa.ao

2. Solicite abertura de conta Merchant:
   - Tipo: Conta Empresarial
   - Serviço: Multicaixa Express API
   - Finalidade: Pagamentos online

3. Documentos necessários:
   - NIF da empresa
   - Estatutos da empresa
   - BI do representante legal
   - Comprovativo de morada da empresa

### Passo 2.2: Aguardar Aprovação

- Prazo: 5-10 dias úteis
- Multicaixa fará visita técnica
- Aprovação comercial e técnica

### Passo 2.3: Receber Credenciais

Após aprovação, você receberá:
- **Merchant ID**: `MCX_XXXXXXXX`
- **API Key**: `sk_live_XXXXXXXXXXXXXXXX`
- **Webhook Secret**: `whsec_XXXXXXXXXXXXXXXX`

### Passo 2.4: Configurar API

```python
config = {
    "multicaixa": {
        "merchant_id": "MCX_XXXXXXXX",
        "api_key": "sk_live_XXXXXXXXXXXXXXXX",
        "sandbox": False  # Produção
    }
}
```

### Passo 2.5: Configurar Webhooks

URL do webhook: `https://diotec360.com/api/payment/multicaixa/callback`

Eventos:
- `payment.completed`
- `payment.failed`
- `payment.cancelled`

### Passo 2.6: Testar Pagamento

```python
# Teste com número de telefone real
result = gateway.create_payment(
    account_id="test_account",
    package_name="Starter",
    amount=Decimal("8333.30"),
    currency=Currency.AOA,
    payment_method=PaymentMethod.MULTICAIXA_EXPRESS,
    customer_phone="+244923456789"  # Seu número para teste
)

# Você receberá SMS para aprovar
```

---

## 3. Integrar com Backend (FastAPI)

### Passo 3.1: Adicionar Endpoints de Pagamento

```python
# api/main.py
from fastapi import FastAPI, Request, HTTPException
from aethel.core.payment_gateway import (
    initialize_payment_gateway,
    PaymentMethod,
    Currency
)
from aethel.core.billing import get_billing_kernel

app = FastAPI()

# Inicializar gateway
payment_config = {
    "paypal": {
        "client_id": "YOUR_PAYPAL_CLIENT_ID",
        "client_secret": "YOUR_PAYPAL_SECRET",
        "sandbox": False
    },
    "multicaixa": {
        "merchant_id": "YOUR_MULTICAIXA_MERCHANT_ID",
        "api_key": "YOUR_MULTICAIXA_API_KEY",
        "sandbox": False
    }
}

gateway = initialize_payment_gateway(payment_config)
billing = get_billing_kernel()

@app.post("/api/payment/create")
async def create_payment(
    account_id: str,
    package_name: str,
    payment_method: str,
    customer_phone: str = None
):
    """Criar pagamento"""
    
    # Determinar método e moeda
    if payment_method == "paypal":
        method = PaymentMethod.PAYPAL
        currency = Currency.USD
    elif payment_method == "multicaixa":
        method = PaymentMethod.MULTICAIXA_EXPRESS
        currency = Currency.AOA
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    # Obter preço
    price = gateway.get_package_price(package_name, currency)
    
    # Criar pagamento
    result = gateway.create_payment(
        account_id=account_id,
        package_name=package_name,
        amount=price,
        currency=currency,
        payment_method=method,
        customer_phone=customer_phone
    )
    
    return result

@app.post("/api/payment/complete")
async def complete_payment(transaction_id: str, external_id: str = None):
    """Completar pagamento após aprovação do cliente"""
    
    result = gateway.complete_payment(transaction_id, external_id)
    
    if result["success"]:
        # Adicionar créditos
        billing.purchase_credits(
            result["account_id"],
            result["package_name"]
        )
    
    return result

@app.post("/api/payment/paypal/webhook")
async def paypal_webhook(request: Request):
    """Webhook PayPal"""
    payload = await request.json()
    
    # Verificar assinatura (importante para segurança)
    # ... código de verificação ...
    
    if payload["event_type"] == "PAYMENT.CAPTURE.COMPLETED":
        # Processar pagamento completo
        order_id = payload["resource"]["id"]
        # ... completar pagamento ...
    
    return {"status": "success"}

@app.post("/api/payment/multicaixa/callback")
async def multicaixa_callback(request: Request):
    """Callback Multicaixa"""
    payload = await request.json()
    
    # Verificar assinatura
    # ... código de verificação ...
    
    if payload["status"] == "completed":
        # Processar pagamento completo
        payment_id = payload["payment_id"]
        # ... completar pagamento ...
    
    return {"status": "success"}
```

---

## 4. Integrar com Frontend

### Passo 4.1: Criar Componente de Pagamento

```typescript
// frontend/components/PaymentSelector.tsx
"use client";

import { useState } from "react";

interface PaymentSelectorProps {
  accountId: string;
  packageName: string;
  priceUSD: number;
  priceAOA: number;
}

export default function PaymentSelector({
  accountId,
  packageName,
  priceUSD,
  priceAOA
}: PaymentSelectorProps) {
  const [paymentMethod, setPaymentMethod] = useState<"paypal" | "multicaixa">("paypal");
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    setLoading(true);

    try {
      const response = await fetch("/api/payment/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          account_id: accountId,
          package_name: packageName,
          payment_method: paymentMethod,
          customer_phone: paymentMethod === "multicaixa" ? phone : null
        })
      });

      const result = await response.json();

      if (result.success) {
        if (paymentMethod === "paypal") {
          // Redirecionar para PayPal
          window.location.href = result.approval_url;
        } else {
          // Mostrar referência Multicaixa
          alert(`Referência: ${result.reference}\nAguarde SMS para aprovar`);
        }
      }
    } catch (error) {
      console.error("Payment error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-xl font-bold mb-4">Escolha o Método de Pagamento</h3>

      {/* PayPal Option */}
      <div className="mb-4">
        <label className="flex items-center p-4 border rounded cursor-pointer">
          <input
            type="radio"
            value="paypal"
            checked={paymentMethod === "paypal"}
            onChange={(e) => setPaymentMethod(e.target.value as "paypal")}
            className="mr-3"
          />
          <div>
            <div className="font-semibold">PayPal</div>
            <div className="text-sm text-gray-600">
              Cartões internacionais - ${priceUSD} USD
            </div>
          </div>
        </label>
      </div>

      {/* Multicaixa Option */}
      <div className="mb-4">
        <label className="flex items-center p-4 border rounded cursor-pointer">
          <input
            type="radio"
            value="multicaixa"
            checked={paymentMethod === "multicaixa"}
            onChange={(e) => setPaymentMethod(e.target.value as "multicaixa")}
            className="mr-3"
          />
          <div>
            <div className="font-semibold">Multicaixa Express</div>
            <div className="text-sm text-gray-600">
              Pagamento via telemóvel - {priceAOA.toLocaleString()} AOA
            </div>
          </div>
        </label>
      </div>

      {/* Phone input for Multicaixa */}
      {paymentMethod === "multicaixa" && (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Número de Telefone
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+244 923 456 789"
            className="w-full p-2 border rounded"
          />
        </div>
      )}

      {/* Pay Button */}
      <button
        onClick={handlePayment}
        disabled={loading || (paymentMethod === "multicaixa" && !phone)}
        className="w-full py-3 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? "Processando..." : "Pagar Agora"}
      </button>
    </div>
  );
}
```

---

## 5. Variáveis de Ambiente

### Passo 5.1: Criar arquivo .env

```bash
# .env.production

# PayPal
PAYPAL_CLIENT_ID=YOUR_LIVE_CLIENT_ID
PAYPAL_CLIENT_SECRET=YOUR_LIVE_SECRET
PAYPAL_SANDBOX=false

# Multicaixa
MULTICAIXA_MERCHANT_ID=MCX_XXXXXXXX
MULTICAIXA_API_KEY=sk_live_XXXXXXXXXXXXXXXX
MULTICAIXA_SANDBOX=false

# Webhooks
PAYPAL_WEBHOOK_ID=WH-XXXXXXXXXXXXXXXX
MULTICAIXA_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXX
```

### Passo 5.2: Carregar no código

```python
import os
from dotenv import load_dotenv

load_dotenv()

payment_config = {
    "paypal": {
        "client_id": os.getenv("PAYPAL_CLIENT_ID"),
        "client_secret": os.getenv("PAYPAL_CLIENT_SECRET"),
        "sandbox": os.getenv("PAYPAL_SANDBOX") == "true"
    },
    "multicaixa": {
        "merchant_id": os.getenv("MULTICAIXA_MERCHANT_ID"),
        "api_key": os.getenv("MULTICAIXA_API_KEY"),
        "sandbox": os.getenv("MULTICAIXA_SANDBOX") == "true"
    }
}
```

---

## 6. Segurança

### 6.1: Verificar Webhooks

```python
import hmac
import hashlib

def verify_paypal_webhook(payload: bytes, signature: str, webhook_id: str) -> bool:
    """Verificar assinatura PayPal"""
    # Implementar verificação conforme documentação PayPal
    pass

def verify_multicaixa_signature(payload: dict, signature: str, api_key: str) -> bool:
    """Verificar assinatura Multicaixa"""
    message = json.dumps(payload, sort_keys=True)
    expected = hmac.new(
        api_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### 6.2: HTTPS Obrigatório

- ✅ Certificado SSL instalado
- ✅ Redirecionar HTTP → HTTPS
- ✅ HSTS habilitado

### 6.3: Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/api/payment/create")
@limiter.limit("10/minute")  # Máximo 10 pagamentos por minuto
async def create_payment(...):
    pass
```

---

## 7. Monitoramento

### 7.1: Logs de Pagamento

```python
import logging

logger = logging.getLogger("payment_gateway")

logger.info(f"Payment created: {transaction_id}")
logger.info(f"Payment completed: {transaction_id}")
logger.error(f"Payment failed: {transaction_id} - {error}")
```

### 7.2: Alertas

Configure alertas para:
- Pagamentos falhados (> 5% taxa de falha)
- Webhooks não recebidos
- Valores suspeitos
- Múltiplas tentativas do mesmo cliente

---

## 8. Checklist de Produção

### Antes de Ativar

- [ ] Conta PayPal Business verificada
- [ ] Credenciais PayPal de produção obtidas
- [ ] Webhooks PayPal configurados
- [ ] Conta Multicaixa Merchant aprovada
- [ ] Credenciais Multicaixa obtidas
- [ ] Webhooks Multicaixa configurados
- [ ] Testes em sandbox completos
- [ ] Certificado SSL instalado
- [ ] Variáveis de ambiente configuradas
- [ ] Logs e monitoramento ativos
- [ ] Backup de transações configurado

### Primeiro Pagamento Real

1. Teste com valor pequeno (Starter - $10)
2. Use seu próprio cartão/telefone
3. Verifique se créditos foram adicionados
4. Confirme recebimento do dinheiro
5. Verifique logs e webhooks

---

## 9. Suporte

### PayPal

- Documentação: https://developer.paypal.com/docs
- Suporte: https://www.paypal.com/ao/smarthelp/contact-us
- Telefone: +244 XXX XXX XXX (Angola)

### Multicaixa

- Email: suporte@multicaixa.ao
- Telefone: +244 222 638 900
- Website: https://www.multicaixa.ao

---

## 10. Custos e Taxas

### PayPal

- Taxa padrão: 2.9% + $0.30 por transação
- Conversão de moeda: +2.5%
- Saque para banco: Grátis (Angola)

### Multicaixa

- Taxa padrão: 1-2% por transação
- Sem taxa de conversão (AOA)
- Saque para banco: Grátis

### Exemplo de Receita Líquida

```
Venda: $100 USD via PayPal
Taxa PayPal: $3.20 (2.9% + $0.30)
Você recebe: $96.80

Venda: 83,333 AOA via Multicaixa
Taxa Multicaixa: 1,250 AOA (1.5%)
Você recebe: 82,083 AOA (≈ $98.50 USD)
```

---

**Status**: ✅ Guia Completo  
**Próximo Passo**: Criar contas e obter credenciais  
**Tempo Estimado**: 1-2 semanas até primeiro pagamento real  

💰🇦🇴🌍🚀
