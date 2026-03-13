# 🚀 Deploy do Backend Aethel no Railway - Passo a Passo

## ✅ Arquivos Atualizados

Acabei de simplificar toda a configuração. Agora está pronto para deploy limpo!

---

## 📋 PASSO 1: LIMPAR DEPLOY ANTIGO NO RAILWAY

### 1.1 Acessar Railway
- Vá para: https://railway.app/dashboard
- Faça login com sua conta GitHub

### 1.2 Deletar Projeto Antigo (se existir)
1. Encontre o projeto "aethel" ou "aethel-api"
2. Clique no projeto
3. Vá em **Settings** (⚙️ no canto superior direito)
4. Role até o final da página
5. Clique em **"Delete Service"** ou **"Delete Project"**
6. Confirme a exclusão

---

## 📋 PASSO 2: COMMIT DAS MUDANÇAS

Antes de fazer o novo deploy, vamos garantir que as mudanças estão no GitHub:

```bash
# Verificar mudanças
git status

# Adicionar arquivos atualizados
git add api/Dockerfile api/start.sh api/railway.json railway.toml

# Commit
git commit -m "fix: simplified Railway deployment configuration"

# Push para GitHub
git push origin main
```

---

## 📋 PASSO 3: CRIAR NOVO DEPLOY NO RAILWAY

### 3.1 Novo Projeto
1. No Railway dashboard, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório **"diotec360-lang"** (ou o nome do seu repo)
4. Railway vai detectar automaticamente o Dockerfile

### 3.2 Configuração Automática
Railway vai:
- ✅ Detectar `railway.toml`
- ✅ Usar `api/Dockerfile`
- ✅ Instalar dependências
- ✅ Iniciar o servidor

### 3.3 Aguardar Build
- Você verá os logs em tempo real
- Deve levar 2-5 minutos
- Procure por: **"🚀 Starting Aethel API"**

### 3.4 Obter URL
1. Quando o deploy terminar, clique em **"Settings"**
2. Vá em **"Networking"** → **"Public Networking"**
3. Clique em **"Generate Domain"**
4. Copie a URL (exemplo: `aethel-api-production.up.railway.app`)

---

## 📋 PASSO 4: TESTAR A API

### 4.1 Teste de Saúde
```bash
# Substitua [SUA-URL] pela URL do Railway
curl https://[SUA-URL].up.railway.app/health
```

**Resposta esperada:**
```json
{"status": "healthy"}
```

### 4.2 Teste de Exemplos
```bash
curl https://[SUA-URL].up.railway.app/api/examples
```

**Resposta esperada:**
```json
{
  "success": true,
  "examples": [...],
  "count": 3
}
```

### 4.3 Teste de Verificação
```bash
curl -X POST https://[SUA-URL].up.railway.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "code": "intent test() { guard { true; } verify { true; } }"
  }'
```

---

## 📋 PASSO 5: ATUALIZAR FRONTEND (VERCEL)

### 5.1 Acessar Vercel
- Vá para: https://vercel.com/dashboard
- Encontre o projeto "diotec360-lang"

### 5.2 Atualizar Variável de Ambiente
1. Clique no projeto
2. Vá em **"Settings"**
3. Clique em **"Environment Variables"**
4. Encontre `NEXT_PUBLIC_API_URL`
5. Clique em **"Edit"**
6. Atualize o valor para: `https://[SUA-URL].up.railway.app`
7. Clique em **"Save"**

### 5.3 Redeploy
1. Vá para a aba **"Deployments"**
2. Clique nos 3 pontinhos (...) no último deploy
3. Clique em **"Redeploy"**
4. Aguarde 1-2 minutos

---

## 📋 PASSO 6: TESTAR TUDO JUNTO

### 6.1 Acessar Frontend
- Vá para: https://diotec360-lang.vercel.app (ou sua URL)

### 6.2 Testar Funcionalidades
1. **Carregar Exemplo**:
   - Clique em "Load Example"
   - Selecione "Financial Transfer"
   - Código deve aparecer no editor

2. **Verificar Código**:
   - Clique no botão "Verify"
   - Aguarde 2-3 segundos
   - Deve aparecer "✅ PROVED" no painel direito

3. **Verificar Console do Browser**:
   - Pressione F12
   - Vá na aba "Console"
   - Não deve ter erros de CORS ou conexão

---

## 🐛 TROUBLESHOOTING

### Problema: Railway não encontra Dockerfile

**Solução:**
1. Verifique se `railway.toml` está na raiz do projeto
2. Verifique se `api/Dockerfile` existe
3. Tente deletar e recriar o projeto no Railway

### Problema: Build falha com erro de dependências

**Solução:**
1. Verifique os logs no Railway
2. Procure por erros de `pip install`
3. Se necessário, adicione dependências em `api/requirements.txt`

### Problema: API inicia mas retorna 502

**Solução:**
1. Verifique se a porta está correta: `$PORT`
2. Verifique logs: procure por "Starting Aethel API"
3. Tente reiniciar o serviço no Railway

### Problema: Frontend não conecta com Backend

**Solução:**
1. Verifique se a URL no Vercel está correta
2. Teste a API diretamente com `curl`
3. Verifique CORS no `api/main.py`
4. Abra console do browser (F12) e veja erros

---

## ✅ CHECKLIST FINAL

- [ ] Projeto antigo deletado no Railway
- [ ] Mudanças commitadas no GitHub
- [ ] Novo projeto criado no Railway
- [ ] Build completado com sucesso
- [ ] URL do Railway obtida
- [ ] API testada com curl (health, examples, verify)
- [ ] Variável de ambiente atualizada no Vercel
- [ ] Frontend redeployado
- [ ] Frontend testado (carregar exemplo + verificar)
- [ ] Sem erros no console do browser

---

## 🎉 SUCESSO!

Se todos os testes passaram, seu deploy está completo!

**URLs:**
- Backend: `https://[sua-url].up.railway.app`
- Frontend: `https://diotec360-lang.vercel.app`

**Próximos passos:**
1. Compartilhar nas redes sociais
2. Adicionar URL no README.md
3. Criar release v1.0.0 no GitHub
4. Monitorar logs e métricas

---

## 📞 PRECISA DE AJUDA?

Se algo não funcionar:
1. Copie os logs de erro do Railway
2. Copie os erros do console do browser (F12)
3. Me mostre e vou te ajudar a resolver!

**Boa sorte com o deploy! 🚀**
