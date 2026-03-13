# 🚀 Guia Rápido: Bloco `solve` v1.9.0

## ⚡ TL;DR

**TODOS os `intent` em v1.9.0 DEVEM ter um bloco `solve`.**

```aethel
intent my_transaction(...) {
    guard { ... }
    
    solve {              // ← OBRIGATÓRIO!
        priority: security;
        target: defi_vault;
    }
    
    verify { ... }
}
```

---

## 🎯 Estrutura Obrigatória

```aethel
intent nome_da_transacao(parametros) {
    guard {
        // Pré-condições
    }
    
    solve {
        priority: <prioridade>;
        target: <ambiente>;
    }
    
    verify {
        // Pós-condições
    }
}
```

---

## 🔧 Opções do Bloco `solve`

### Priority (Prioridade)

| Valor | Quando Usar | Exemplo |
|-------|-------------|---------|
| `security` | Transações financeiras, DeFi | Liquidações, transferências |
| `privacy` | Dados sensíveis, HIPAA | Registros médicos, compliance |
| `speed` | Alta performance necessária | Trading de alta frequência |
| `energy` | Otimização de recursos | IoT, dispositivos móveis |

### Target (Ambiente de Execução)

| Valor | Quando Usar | Exemplo |
|-------|-------------|---------|
| `defi_vault` | Finanças descentralizadas | Empréstimos, liquidações |
| `oracle_sanctuary` | Dados externos (oráculos) | Preços, clima, eventos |
| `ghost_protocol` | Privacidade (ZKP) | Dados médicos, compliance |
| `trading_engine` | Operações de trading | Ordens, rebalanceamento |

---

## 📋 Exemplos Práticos

### 1. Transferência Financeira

```aethel
intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        old_sender_balance >= amount;
        amount > 0;
    }
    
    solve {
        priority: security;
        target: defi_vault;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
    }
}
```

### 2. Liquidação com Oráculo

```aethel
intent liquidate(
    borrower: Account,
    external btc_price: Price
) {
    guard {
        btc_price_verified == true;
        btc_price_fresh == true;
    }
    
    solve {
        priority: security;
        target: oracle_sanctuary;  // ← Dados externos
    }
    
    verify {
        collateral_value == collateral_amount * btc_price;
        (debt > collateral_value * 0.75) ==> (liquidation_allowed == true);
    }
}
```

### 3. Verificação Privada (HIPAA)

```aethel
intent verify_treatment(
    patient: Person,
    secret diagnosis: Code
) {
    guard {
        treatment_cost > 0;
    }
    
    solve {
        priority: privacy;
        target: ghost_protocol;  // ← Ativa ZKP
    }
    
    verify {
        diagnosis in covered_conditions;
        coverage_approved == true;
    }
}
```

### 4. Seguro Paramétrico

```aethel
intent crop_payout(
    farmer: Account,
    external rainfall_mm: Measurement
) {
    guard {
        rainfall_verified == true;
        rainfall_fresh == true;
    }
    
    solve {
        priority: security;
        target: oracle_sanctuary;  // ← Dados climáticos
    }
    
    verify {
        (rainfall_mm < threshold) ==> (farmer_balance == old_balance + payout);
    }
}
```

---

## ❌ Erros Comuns

### Erro 1: Bloco `solve` Ausente

```aethel
// ❌ ERRO: Expected 'SOLVE'
intent transfer(...) {
    guard { ... }
    verify { ... }  // ← Pula direto para verify
}
```

**Solução**: Adicione o bloco `solve`:

```aethel
// ✅ CORRETO
intent transfer(...) {
    guard { ... }
    solve {
        priority: security;
        target: defi_vault;
    }
    verify { ... }
}
```

### Erro 2: Usar `if` em vez de `==>`

```aethel
// ❌ ERRO: Sintaxe imperativa
verify {
    if (condition) {
        result == true;
    }
}
```

**Solução**: Use implicação lógica:

```aethel
// ✅ CORRETO: Sintaxe declarativa
verify {
    (condition) ==> (result == true);
}
```

### Erro 3: Target Incorreto

```aethel
// ❌ ERRO: Target errado para dados externos
intent liquidate(external price: Price) {
    solve {
        target: defi_vault;  // ← Deveria ser oracle_sanctuary
    }
}
```

**Solução**: Use o target correto:

```aethel
// ✅ CORRETO
intent liquidate(external price: Price) {
    solve {
        target: oracle_sanctuary;  // ← Correto para dados externos
    }
}
```

---

## 🎓 Regras de Ouro

1. **SEMPRE inclua o bloco `solve`** - É obrigatório em v1.9.0
2. **Escolha a priority correta** - `security` para finanças, `privacy` para dados sensíveis
3. **Escolha o target correto** - `oracle_sanctuary` para dados externos, `ghost_protocol` para ZKP
4. **Use `==>` em vez de `if`** - Sintaxe declarativa para análise determinística
5. **Declare o ambiente explicitamente** - Não deixe o sistema adivinhar

---

## 🔍 Checklist de Validação

Antes de compilar seu código, verifique:

- [ ] Todos os `intent` têm bloco `solve`?
- [ ] A `priority` está correta para o caso de uso?
- [ ] O `target` corresponde ao tipo de dados/operação?
- [ ] Usei `==>` em vez de `if` no `verify`?
- [ ] Declarei `external` para dados de oráculos?
- [ ] Declarei `secret` para dados privados?

---

## 📚 Referências

- **Documentação Completa**: `CANON_DE_PRECISAO_V1_9_0_APLICADO.md`
- **Exemplos Práticos**: `api/main.py` (linha 285+)
- **Casos de Uso**: `aethel/examples/*.ae`
- **Testes**: `test_*.py`

---

## 🆘 Precisa de Ajuda?

**Erro de compilação?**
1. Verifique se o bloco `solve` está presente
2. Confirme que `priority` e `target` estão corretos
3. Substitua `if` por `==>`

**Não sabe qual target usar?**
- Dados externos → `oracle_sanctuary`
- Privacidade → `ghost_protocol`
- Finanças → `defi_vault`
- Trading → `trading_engine`

**Exemplo não funciona?**
- Todos os exemplos em `api/main.py` estão atualizados para v1.9.0
- Use-os como referência

---

**🏛️ Diotec360 v1.9.0 - O Compilador Implacável ⚖️**
