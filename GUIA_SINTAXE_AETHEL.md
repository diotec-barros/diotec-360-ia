# 📖 Guia de Sintaxe Diotec360 v1.1

**Versão**: v1.1 "The Resonance"  
**Status**: Linguagem de Verificação Formal

---

## 🎯 REGRA DE OURO

**Diotec360 é matemática pura. Cada caractere importa.**

Como uma equação matemática, não há espaço para "comentários" ou "explicações" dentro do código. O Parser trata tudo como lógica formal.

---

## ✅ CÓDIGO VÁLIDO (Funciona!)

```aethel
intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > zero;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        sender_balance < old_sender_balance;
        receiver_balance > old_receiver_balance;
    }
}
```

---

## ❌ CÓDIGO INVÁLIDO (Não funciona!)

```aethel
// Este é um comentário - NÃO FUNCIONA!
intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;  // Comentário inline - NÃO FUNCIONA!
        amount > zero;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        sender_balance < old_sender_balance;
        receiver_balance > old_receiver_balance;
    }
}
```

**Erro**: `No terminal matches '/'`

---

## 🚫 O QUE NÃO FUNCIONA NA v1.1

### 1. Comentários de Linha
```aethel
// Isso não funciona
```

### 2. Comentários Inline
```aethel
amount > zero;  // Isso não funciona
```

### 3. Comentários de Bloco
```aethel
/* Isso também não funciona */
```

### 4. Strings com Texto
```aethel
"Texto explicativo"  // Não funciona
```

### 5. Caracteres Especiais
```aethel
@ # $ % ^ & * ( ) - = + [ ] { } | \ : ; " ' < > ? / ~
```

Apenas os caracteres da sintaxe Aethel são permitidos!

---

## ✅ O QUE FUNCIONA

### 1. Palavras-chave Aethel
```aethel
intent
guard
solve
verify
priority
target
old_
```

### 2. Operadores Matemáticos
```aethel
==  !=  <  >  <=  >=
+   -   *   /   %
&&  ||  !
```

### 3. Identificadores
```aethel
sender
receiver
amount
balance
account
```

### 4. Tipos
```aethel
Account
Balance
Address
Uint256
Bool
```

### 5. Literais
```aethel
zero
one
true
false
```

---

## 🎨 ESTRUTURA VÁLIDA

### Intent Completo:
```aethel
intent nome_do_intent(param1: Tipo1, param2: Tipo2) {
    guard {
        condicao1;
        condicao2;
    }
    
    solve {
        priority: valor;
        target: alvo;
    }
    
    verify {
        pos_condicao1;
        pos_condicao2;
    }
}
```

### Intent Mínimo:
```aethel
intent nome(param: Tipo) {
    verify {
        condicao;
    }
}
```

---

## 🔍 POR QUE TÃO RIGOROSO?

### Diotec360 é Matemática, Não Prosa

Imagine tentar resolver esta equação:
```
2 + 2 // isso é uma soma = 4
```

O "// isso é uma soma" confunde o sistema matemático!

Da mesma forma, Aethel trata código como:
```
∀x ∈ Accounts: balance(x) ≥ 0
```

Qualquer caractere extra quebra a lógica formal.

---

## 💡 COMO DOCUMENTAR SEU CÓDIGO

### Opção 1: Documentação Externa
Crie um arquivo separado:
```markdown
# transfer.md

## Descrição
Transfere fundos entre contas com segurança.

## Parâmetros
- sender: Conta de origem
- receiver: Conta de destino
- amount: Valor a transferir

## Garantias
- Saldo suficiente
- Valor positivo

## Verificações
- Conservação de fundos
- Saldo atualizado corretamente
```

### Opção 2: Nomes Descritivos
```aethel
intent secure_transfer_with_balance_check(
    verified_sender: Account,
    verified_receiver: Account,
    positive_amount: Balance
) {
    guard {
        verified_sender_balance >= positive_amount;
        positive_amount > zero;
    }
    
    verify {
        verified_sender_balance == old_verified_sender_balance - positive_amount;
        verified_receiver_balance == old_verified_receiver_balance + positive_amount;
    }
}
```

---

## 🐛 ERROS COMUNS

### Erro 1: Comentários
```aethel
// Comentário
```
**Solução**: Remova todos os comentários

### Erro 2: Strings
```aethel
"texto"
```
**Solução**: Remova strings de texto

### Erro 3: Caracteres Especiais
```aethel
@deprecated
```
**Solução**: Use apenas sintaxe Aethel

### Erro 4: Espaços Extras
```aethel
amount    >    zero;
```
**Solução**: Use espaços normais (funciona, mas evite)

---

## 🎯 CHECKLIST PRÉ-VERIFICAÇÃO

Antes de clicar em "Verify", verifique:

- [ ] Sem comentários (//)
- [ ] Sem strings ("texto")
- [ ] Sem caracteres especiais (@, #, etc.)
- [ ] Apenas sintaxe Diotec360 válida
- [ ] Todas as chaves fechadas { }
- [ ] Todos os pontos-e-vírgulas presentes ;
- [ ] Nomes de variáveis consistentes

---

## 🚀 ROADMAP: COMENTÁRIOS NO FUTURO

### v1.2 (Planejado)
```aethel
# Comentário estilo Python
intent transfer(...) {
    # Comentário inline
    guard {
        amount > zero;  # Comentário no final
    }
}
```

### v2.0 (Futuro)
```aethel
/** 
 * Documentação estilo JavaDoc
 * @param sender Conta de origem
 * @param receiver Conta de destino
 */
intent transfer(...) {
    // Comentários de linha
    guard {
        amount > zero;  // Comentários inline
    }
}
```

---

## 📚 EXEMPLOS VÁLIDOS

### Exemplo 1: Transfer Simples
```aethel
intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > zero;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
    }
}
```

### Exemplo 2: Mint
```aethel
intent mint(account: Account, amount: Balance) {
    guard {
        amount > zero;
        caller == owner;
    }
    
    verify {
        account_balance == old_account_balance + amount;
        total_supply == old_total_supply + amount;
    }
}
```

### Exemplo 3: Burn
```aethel
intent burn(account: Account, amount: Balance) {
    guard {
        amount > zero;
        account_balance >= amount;
    }
    
    verify {
        account_balance == old_account_balance - amount;
        total_supply == old_total_supply - amount;
    }
}
```

---

## 🎓 DICAS PRO

### 1. Use o Editor com Cuidado
- Digite devagar
- Verifique cada linha
- Não copie de fontes externas (pode ter caracteres invisíveis)

### 2. Teste Incrementalmente
- Comece com código mínimo
- Adicione uma linha por vez
- Verifique após cada adição

### 3. Use os Exemplos
- Clique em "Load Example"
- Modifique aos poucos
- Aprenda com código que funciona

### 4. Entenda os Erros
- "No terminal matches" = caractere inválido
- "Unexpected token" = sintaxe incorreta
- "Parse error" = estrutura inválida

---

## 🌟 FILOSOFIA AETHEL

```
"Código não é prosa.
Código é matemática.
Matemática não tem comentários.
Matemática é pura verdade."
```

Aethel força você a pensar em termos matemáticos puros. Isso pode parecer restritivo, mas é exatamente isso que garante que seu código seja **provadamente correto**.

---

## 📞 SUPORTE

### Se você encontrar um erro:
1. Remova todos os comentários
2. Remova todas as strings
3. Verifique a sintaxe
4. Tente novamente

### Se ainda não funcionar:
1. Copie um exemplo que funciona
2. Modifique aos poucos
3. Identifique onde quebra
4. Reporte no GitHub

---

## ✅ RESUMO

```
✅ Código puro, sem comentários
✅ Apenas sintaxe Diotec360 válida
✅ Matemática, não prosa
✅ Cada caractere importa
✅ Verificação formal rigorosa
```

---

**Lembre-se**: A rigidez do Parser é o que garante que seu código seja **matematicamente perfeito**. Sem comentários, sem ambiguidade, sem bugs.

**Bem-vindo à pureza matemática do Aethel!** ✨

---

**Versão**: v1.1  
**Última atualização**: 3 de Fevereiro de 2026  
**Status**: Documentação Oficial
