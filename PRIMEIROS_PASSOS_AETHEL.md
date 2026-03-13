# 🚀 Primeiros Passos com Aethel

**Bem-vindo ao Diotec360 v1.1 "The Resonance"!**

---

## 🎯 O QUE VOCÊ VAI APRENDER

1. Como escrever seu primeiro código Aethel
2. Como usar o Ghost-Runner
3. Como verificar formalmente
4. Como manifestar realidade com Mirror

**Tempo**: 10 minutos

---

## 📖 PASSO 1: ENTENDA O BÁSICO

### Diotec360 é Diferente

Aethel não é como JavaScript, Python ou Java. É uma **linguagem de verificação formal**.

```
Linguagens Normais:  Código → Testes → Esperança
Aethel:              Código → Prova Matemática → Certeza
```

### Regra de Ouro

**Diotec360 é matemática pura. Sem comentários, sem strings, apenas lógica.**

---

## 🌐 PASSO 2: ACESSE O AETHEL STUDIO

1. Abra: **https://aethel.diotec360.com**
2. Aguarde o editor carregar
3. Você verá:
   - Editor Monaco (esquerda)
   - Painel de controles (direita)
   - Ghost Panel (quando ativo)

---

## 📝 PASSO 3: SEU PRIMEIRO CÓDIGO

### Opção A: Carregar Exemplo

1. Clique em **"Load Example"**
2. Escolha **"Financial Transfer"**
3. O código aparecerá no editor

### Opção B: Digitar Manualmente

Digite exatamente (sem comentários!):

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

---

## 🔮 PASSO 4: ATIVE O GHOST-RUNNER

### O que é Ghost-Runner?

Ghost-Runner **prediz o futuro** do seu código antes de executar!

### Como ativar:

1. Procure o toggle **"🌌 Ghost ON"**
2. Clique para ativar
3. O Ghost Panel aparecerá

### O que observar:

Enquanto você digita, o Ghost-Runner:
- ✨ Manifesta o resultado
- 🔮 Elimina estados impossíveis
- ⚡ Mostra confidence (0-100%)
- 🎯 Indica latência (~0ms)

---

## ✅ PASSO 5: VERIFICAR FORMALMENTE

### O que é Verificação Formal?

É uma **prova matemática** de que seu código está correto.

### Como verificar:

1. Com o código no editor
2. Clique em **"Verify"**
3. Aguarde 1-2 segundos
4. Veja o resultado:
   - ✅ **PROVED**: Código matematicamente correto!
   - ❌ **FAILED**: Há um erro lógico
   - ⚠️ **ERROR**: Erro de sintaxe

### O que acontece:

O Judge (motor Z3) analisa:
- Guards (pré-condições)
- Verify (pós-condições)
- Lógica matemática
- Conservação de propriedades

---

## 🪞 PASSO 6: MANIFESTAR REALIDADE

### O que é Mirror?

Mirror cria um **preview instantâneo** do seu código verificado.

### Como manifestar:

1. Código deve estar **PROVED** (verde)
2. Clique em **"Manifest Reality"**
3. Mirror Frame abre
4. Você verá:
   - Código verificado
   - Merkle Root
   - URL compartilhável
   - Status: LIVE

### Compartilhar:

1. Copie a URL
2. Envie para qualquer pessoa
3. Eles verão o mesmo preview
4. Sem login, sem setup!

---

## 🎨 PASSO 7: EXPERIMENTE MODIFICAÇÕES

### Teste 1: Código Impossível

Tente este código:

```aethel
intent impossible() {
    guard {
        false;
    }
    
    verify {
        true;
    }
}
```

**Resultado esperado**:
- Ghost-Runner: "🚫 IMPOSSIBLE"
- Confidence: 0%
- Verify: FAILED

**Por quê?**: Guard sempre falso = código nunca pode executar!

### Teste 2: Código Contraditório

Tente este código:

```aethel
intent paradox(x: Balance) {
    guard {
        x > 10;
    }
    
    verify {
        x < 5;
    }
}
```

**Resultado esperado**:
- Ghost-Runner: "🔮 UNCERTAIN"
- Verify: FAILED

**Por quê?**: x não pode ser maior que 10 E menor que 5 ao mesmo tempo!

### Teste 3: Código Correto

Volte ao exemplo original:

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

**Resultado esperado**:
- Ghost-Runner: "✨ MANIFESTED"
- Confidence: 100%
- Verify: PROVED

**Por quê?**: Lógica matematicamente correta!

---

## 🚫 ERROS COMUNS

### Erro 1: "No terminal matches '/'"

**Causa**: Você tentou usar comentários (//)

**Solução**: Remova todos os comentários

```aethel
// Isso não funciona!
intent test() {
    verify { true; }
}
```

**Correto**:
```aethel
intent test() {
    verify { true; }
}
```

### Erro 2: "Unexpected token"

**Causa**: Sintaxe incorreta

**Solução**: Verifique:
- Todas as chaves fechadas { }
- Todos os pontos-e-vírgulas ;
- Nomes de variáveis corretos

### Erro 3: "Parse error"

**Causa**: Estrutura inválida

**Solução**: Compare com um exemplo que funciona

---

## 💡 DICAS PRO

### 1. Use os Exemplos

Os exemplos são **garantidos** de funcionar. Use-os como base!

### 2. Modifique aos Poucos

Não mude tudo de uma vez. Mude uma linha, teste, mude outra.

### 3. Observe o Ghost-Runner

Ele te diz se o código é possível ANTES de verificar!

### 4. Leia os Erros

Erros do Parser são específicos. Eles te dizem exatamente o que está errado.

### 5. Pense em Matemática

Diotec360 é matemática. Pense em equações, não em instruções.

---

## 🎯 CHECKLIST DE SUCESSO

Você dominou o básico quando conseguir:

- [ ] Carregar um exemplo
- [ ] Ativar o Ghost-Runner
- [ ] Ver o Ghost Panel aparecer
- [ ] Clicar em "Verify" e ver "PROVED"
- [ ] Manifestar realidade com Mirror
- [ ] Copiar e compartilhar a URL
- [ ] Modificar o código e re-verificar
- [ ] Identificar código impossível
- [ ] Escrever código do zero

---

## 📚 PRÓXIMOS PASSOS

### Nível Intermediário:
1. Leia: **GUIA_SINTAXE_AETHEL.md**
2. Estude: Exemplos mais complexos
3. Experimente: Seus próprios intents

### Nível Avançado:
1. Leia: **WHITEPAPER.md**
2. Entenda: Arquitetura do sistema
3. Contribua: GitHub

---

## 🌟 FILOSOFIA AETHEL

```
"Bugs não são inevitáveis.
São uma escolha.

Aethel escolhe a perfeição matemática."
```

---

## 🆘 PRECISA DE AJUDA?

### Documentação:
- **GUIA_SINTAXE_AETHEL.md**: Sintaxe completa
- **WHITEPAPER.md**: Paper técnico
- **README.md**: Visão geral

### Comunidade:
- **GitHub Issues**: Reporte bugs
- **GitHub Discussions**: Faça perguntas
- **Email**: contact@diotec360.com

---

## ✅ RESUMO

```
1. Acesse: https://aethel.diotec360.com
2. Carregue um exemplo
3. Ative Ghost-Runner
4. Clique em "Verify"
5. Manifeste com Mirror
6. Compartilhe!
```

---

**Bem-vindo ao futuro do software!** 🚀

**Onde bugs são matematicamente impossíveis.** ✨

---

**Versão**: v1.1  
**Última atualização**: 3 de Fevereiro de 2026  
**Status**: Guia Oficial para Iniciantes
