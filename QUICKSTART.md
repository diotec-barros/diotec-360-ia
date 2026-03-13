# Aethel - Guia Rápido

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/your-org/aethel-core
cd aethel-core

# Instalar dependências
pip install -r requirements.txt

# Configurar API (opcional, para geração real)
export ANTHROPIC_API_KEY="sua-chave-aqui"
# ou
export OPENAI_API_KEY="sua-chave-aqui"
# ou usar Ollama local (sem chave necessária)
```

## Seu Primeiro Programa Aethel

Crie um arquivo `hello.ae`:

```aethel
intent transfer_funds(sender: Account, receiver: Account, amount: Gold) {
    guard {
        sender_balance >= amount;
        amount > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        sender_balance < old_balance;
    }
}
```

## Compilar e Executar

```python
from DIOTEC360_kernel import AethelKernel

# Ler código Aethel
with open('hello.ae', 'r') as f:
    code = f.read()

# Criar kernel
kernel = AethelKernel(ai_provider="anthropic")

# Compilar com verificação formal
result = kernel.compile(
    code,
    max_attempts=3,
    output_file="output/hello.rs"
)

# Verificar resultado
if result['status'] == 'SUCCESS':
    print(f"✅ Código verificado e salvo!")
    print(f"🔐 Hash no cofre: {result['vault_hash']}")
else:
    print(f"❌ Falha: {result['message']}")
```

## Testes Disponíveis

```bash
# Teste do Parser
python test_parser.py

# Teste do Verificador Formal
python test_judge.py

# Teste do Kernel (recomendado)
python test_kernel.py

# Teste do Vault
python test_vault.py

# Teste do Weaver
python test_weaver.py

# Teste do Feedback Loop
python test_feedback_loop.py
```

## Estrutura de um Programa Aethel

```aethel
intent nome_da_funcao(param1: Tipo1, param2: Tipo2) {
    guard {
        // Pré-condições (DEVEM ser verdadeiras antes)
        condicao1;
        condicao2;
    }
    solve {
        // Instruções para a IA
        priority: speed;  // ou security, memory, etc.
        target: blockchain;  // ou embedded, cloud, etc.
    }
    verify {
        // Pós-condições (DEVEM ser verdadeiras depois)
        resultado1;
        resultado2;
    }
}
```

## Conceitos Chave

### 1. Guard (Pré-condições)
Condições que DEVEM ser verdadeiras antes da execução. O Judge verifica matematicamente.

### 2. Solve (Instruções)
Diretrizes para a IA sobre como implementar. Não é código, é intenção.

### 3. Verify (Pós-condições)
Condições que DEVEM ser verdadeiras após execução. Provadas formalmente.

### 4. Vault (Cofre)
Funções provadas são armazenadas com hash SHA-256. Imutáveis e eternas.

### 5. Weaver (Tecelão)
Adapta a execução ao hardware em tempo real (bateria, CPU, GPU).

## Modos de Execução do Weaver

- **CRITICAL_BATTERY** (<10%): Mínimo consumo
- **ECONOMY** (<20%): Otimizado para bateria
- **BALANCED**: Equilíbrio padrão
- **PERFORMANCE**: CPU livre, paralelização
- **ULTRA_PERFORMANCE**: CPU + GPU, máxima velocidade

## Exemplos Avançados

### Sistema de Pagamento Seguro
```aethel
intent secure_payment(user: Account, merchant: Account, amount: Gold) {
    guard {
        user_balance >= amount;
        amount > 0;
        amount <= 10000;
        merchant_verified == true;
    }
    solve {
        priority: security;
        target: blockchain;
        encryption: aes256;
    }
    verify {
        user_balance < old_user_balance;
        merchant_balance > old_merchant_balance;
        transaction_logged == true;
    }
}
```

### Controle de Drone
```aethel
intent adjust_altitude(drone: Aircraft, target_meters: Int) {
    guard {
        battery_percent > 20;
        target_meters >= 0;
        target_meters <= max_altitude;
        weather_safe == true;
    }
    solve {
        priority: safety;
        target: embedded;
        realtime: true;
    }
    verify {
        altitude_error < 1;
        battery_percent > 15;
    }
}
```

## Troubleshooting

### Erro: "Verificação formal falhou"
O Judge encontrou contradições nas constraints. Revise suas condições guard e verify.

### Erro: "API key não encontrada"
Configure a variável de ambiente ou use Ollama local.

### Erro: "Função não encontrada no cofre"
O hash especificado não existe. Compile a função primeiro.

## Próximos Passos

1. Explore os testes em `test_*.py`
2. Leia o MANIFESTO.md para entender a filosofia
3. Contribua com funções provadas ao Vault
4. Experimente diferentes modos do Weaver

## Suporte

- GitHub Issues: [link]
- Documentação: [link]
- Discord: [link]

---

**Bem-vindo à era da Computação de Confiança Determinística.**
