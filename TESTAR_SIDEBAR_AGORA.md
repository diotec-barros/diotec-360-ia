# 🚀 Como Testar o Novo Sidebar - Guia Rápido

## 1. Iniciar o Frontend

```bash
cd frontend
npm run dev
```

Aguarde a mensagem:
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

## 2. Abrir no Navegador

Abra: **http://localhost:3000**

## 3. O Que Você Vai Ver

### Sidebar Esquerdo (80px de largura)
```
┌──────┐
│  Æ   │  ← Logo
├──────┤
│ 🏛️   │  ← Judge (ativo por padrão)
│ 🤖   │  ← Architect
│ 🛡️   │  ← Sentinel
│ 🎭   │  ← Ghost
│ 🔮   │  ← Oracle
├──────┤
│ 📚   │  ← Examples
│      │
│ 🤖   │  ← AI Chat
│ ▶️   │  ← Verify
│ 💻   │  ← GitHub
│ 📖   │  ← Docs
└──────┘
```

### Área Principal
- **Editor de Código** (esquerda)
- **Proof Viewer** (direita)
- **Sem Header no Topo** ✅

## 4. Testes a Fazer

### ✅ Teste 1: Trocar de Layer
1. Clique em 🤖 (Architect)
2. Veja o botão ficar verde
3. Clique em 🛡️ (Sentinel)
4. Veja o botão ficar vermelho

**Resultado Esperado**: Cada layer muda de cor quando ativa

---

### ✅ Teste 2: Abrir Exemplos
1. Clique em 📚 (Examples)
2. Sidebar expande para 384px
3. Veja lista de exemplos:
   - 💰 Transfer
   - 🏦 Banking
   - 🌾 Insurance
   - 🔒 Privacy
   - etc.

**Resultado Esperado**: Painel lateral abre com exemplos

---

### ✅ Teste 3: Selecionar Exemplo
1. Com painel de exemplos aberto
2. Clique em "💰 Transfer"
3. Código carrega no editor
4. Clique novamente em 📚 para fechar

**Resultado Esperado**: Código do exemplo aparece no editor

---

### ✅ Teste 4: Verificar Código
1. Clique em ▶️ (Verify)
2. Botão muda para ⏳
3. Aguarde verificação
4. Veja resultado no Proof Viewer

**Resultado Esperado**: Verificação executa e mostra resultado

---

### ✅ Teste 5: Abrir AI Chat
1. Clique em 🤖 (AI Chat) no sidebar
2. Painel lateral abre à direita
3. Digite uma mensagem
4. Ou use CMD+K (CTRL+K)

**Resultado Esperado**: Chat do Architect abre

---

### ✅ Teste 6: Links Externos
1. Clique em 💻 (GitHub)
2. Nova aba abre com repositório
3. Clique em 📖 (Docs)
4. Nova aba abre com documentação

**Resultado Esperado**: Links abrem em nova aba

---

### ✅ Teste 7: Tooltips
1. Passe o mouse sobre 🏛️
2. Veja tooltip: "Mathematical proof engine"
3. Passe sobre outros ícones
4. Veja descrições aparecerem

**Resultado Esperado**: Tooltips aparecem ao passar o mouse

---

### ✅ Teste 8: Responsividade
1. Redimensione a janela
2. Sidebar mantém largura fixa
3. Editor e Proof Viewer se ajustam
4. Tudo continua funcional

**Resultado Esperado**: Layout se adapta ao tamanho da tela

---

## 5. Checklist de Funcionalidades

Marque conforme testa:

- [ ] Sidebar aparece à esquerda
- [ ] Sem header no topo
- [ ] Logo Æ visível
- [ ] 5 layers clicáveis
- [ ] Botão Examples funciona
- [ ] Painel de exemplos abre/fecha
- [ ] Exemplos carregam no editor
- [ ] Botão Verify funciona
- [ ] Botão AI Chat funciona
- [ ] Links GitHub e Docs funcionam
- [ ] Tooltips aparecem
- [ ] CMD+K abre AI Chat
- [ ] Layout responsivo

## 6. Problemas Comuns

### Problema: Sidebar não aparece
**Solução**: Limpe o cache do navegador (CTRL+SHIFT+R)

### Problema: Exemplos não carregam
**Solução**: Verifique se o backend está rodando

### Problema: Botões não respondem
**Solução**: Abra o console (F12) e veja erros

### Problema: Layout quebrado
**Solução**: Verifique se o build está atualizado:
```bash
npm run build
npm run dev
```

## 7. Comandos Úteis

### Limpar cache e reinstalar
```bash
cd frontend
rm -rf .next
rm -rf node_modules
npm install
npm run dev
```

### Build de produção
```bash
npm run build
npm run start
```

### Ver logs detalhados
```bash
npm run dev -- --debug
```

## 8. Resultado Final Esperado

✅ Interface limpa sem header
✅ Sidebar com todas as funcionalidades
✅ Exemplos em painel lateral
✅ Navegação intuitiva
✅ Mais espaço para código
✅ Todas as funcionalidades preservadas

## 9. Próximos Passos

Após testar tudo:

1. ✅ Confirme que tudo funciona
2. 📸 Tire screenshots se quiser
3. 🚀 Faça commit das mudanças
4. 🎉 Celebre a interface melhorada!

## 10. Suporte

Se encontrar problemas:

1. Verifique os logs no console (F12)
2. Veja os arquivos de documentação:
   - `FRONTEND_SIDEBAR_REFACTOR_COMPLETE.md`
   - `SIDEBAR_VISUAL_GUIDE.txt`
   - `RESUMO_MUDANCAS_SIDEBAR.md`
3. Reverta as mudanças se necessário

---

**Boa sorte com os testes! 🚀**

A nova interface está muito mais limpa e funcional!
