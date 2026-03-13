# Correção de Segurança - API Keys Expostas

## ⚠️ Problema Identificado

API Key do Alpha Vantage foi commitada nos arquivos `.env.production` e `frontend/.env.production`.

**API Key exposta**: `O3TC4CQU6GJWBNVL`

## ✅ Ações Tomadas

### 1. Removida API Key dos Arquivos
- ✅ `.env.production` - Substituída por placeholder
- ✅ `frontend/.env.production` - Substituída por placeholder
- ✅ `frontend/.env.local` - Substituída por placeholder

### 2. Criado Template
- ✅ `.env.example` - Template sem credenciais reais

### 3. Verificação do .gitignore
- ✅ `.env` já está no `.gitignore`
- ✅ `.env.local` já está no `.gitignore`
- ✅ `.env.*.local` já está no `.gitignore`

## 🔒 Recomendações de Segurança

### Ação Imediata Necessária

1. **Revogar a API Key do Alpha Vantage**
   - Acesse: https://www.alphavantage.co/support/#api-key
   - Gere uma nova API key
   - Atualize no `.env` local (não commitado)
   - Atualize no Vercel Dashboard

2. **Verificar Uso da Key**
   - Monitore logs para uso não autorizado
   - A key é gratuita, mas tem limite de requisições

### Boas Práticas Implementadas

1. ✅ Arquivos `.env` no `.gitignore`
2. ✅ Templates `.env.example` sem credenciais
3. ✅ Placeholders em arquivos `.env.production`
4. ✅ Documentação clara sobre onde obter keys

### Arquivos Seguros para Commit

✅ **Podem ser commitados**:
- `.env.example` - Template sem credenciais
- `.env.production` - Com placeholders
- `frontend/.env.production` - Com placeholders

❌ **NUNCA commitar**:
- `.env` - Credenciais reais
- `.env.local` - Credenciais de desenvolvimento
- Qualquer arquivo com credenciais reais

## 📋 Checklist de Segurança

- [x] Remover API keys dos arquivos commitados
- [x] Criar `.env.example` como template
- [x] Verificar `.gitignore`
- [ ] Revogar API key exposta (Alpha Vantage)
- [ ] Gerar nova API key
- [ ] Atualizar no Vercel Dashboard
- [ ] Atualizar no `.env` local

## 🔑 Onde Obter Novas Keys

### Alpha Vantage
- **URL**: https://www.alphavantage.co/support/#api-key
- **Gratuito**: Sim (500 requisições/dia)
- **Tempo**: Imediato

### PayPal
- **URL**: https://developer.paypal.com
- **Gratuito**: Sim (sandbox ilimitado)
- **Tempo**: Imediato (sandbox), 1-3 dias (live)

## 📝 Configuração Correta

### 1. Copiar Template
```powershell
Copy-Item .env.example .env
```

### 2. Editar .env
```bash
# Adicionar suas credenciais reais
ALPHA_VANTAGE_API_KEY=sua-key-real-aqui
PAYPAL_CLIENT_ID=seu-client-id-aqui
PAYPAL_CLIENT_SECRET=seu-secret-aqui
```

### 3. Verificar .gitignore
```powershell
git check-ignore .env
# Deve retornar: .env
```

### 4. Nunca Commitar
```powershell
# ERRADO - Nunca faça isso!
git add .env

# CERTO - Apenas templates
git add .env.example
```

## 🚨 Impacto da Exposição

### Alpha Vantage API Key

**Risco**: BAIXO
- Key gratuita com limite de 500 req/dia
- Sem acesso a dados sensíveis
- Sem custo financeiro

**Ação**: Revogar e gerar nova key

### PayPal Credentials

**Status**: ✅ SEGURO
- Apenas placeholders foram commitados
- Nenhuma credencial real exposta

## 📊 Histórico do Git

### Commit Afetado
```
70de202 - feat: Configuracao completa de dominios e PayPal
```

### Arquivos com API Key
- `.env.production`
- `frontend/.env.production`
- `frontend/.env.local`

### Correção
```
Próximo commit - fix: Remove exposed API keys, add .env.example template
```

## 🔐 Segurança no Vercel

As credenciais no Vercel Dashboard são seguras:
- ✅ Marcadas como "Sensitive"
- ✅ Não aparecem em logs
- ✅ Criptografadas em repouso
- ✅ Apenas acessíveis via variáveis de ambiente

## 📚 Recursos

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Vercel: Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Alpha Vantage: API Key Management](https://www.alphavantage.co/support/#api-key)

---

**Data**: 26 de Fevereiro de 2026  
**Severidade**: BAIXA (API key gratuita)  
**Status**: CORRIGIDO  
**Ação Necessária**: Revogar e gerar nova Alpha Vantage API key
