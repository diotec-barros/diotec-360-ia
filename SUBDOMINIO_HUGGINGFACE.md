# 🚀 SUBDOMÍNIO PARA HUGGING FACE

**Data:** 2026-02-12  
**Objetivo:** Criar subdomínio personalizado para o Hugging Face Space

---

## 🎯 OBJETIVO

Criar um subdomínio `hf.diotec360.com` ou `api.diotec360.com` que aponte para:
- **Hugging Face Space:** https://huggingface.co/spaces/diotec/diotec360-judge
- **URL direta:** https://diotec-diotec360-judge.hf.space

---

## 🌐 OPÇÕES DE SUBDOMÍNIO

### Opção 1: api.diotec360.com (Recomendado)
```
Nome: api
Tipo: CNAME
Valor: diotec-diotec360-judge.hf.space
TTL: 60
```

**Vantagens:**
- URL limpa e profissional
- Fácil de lembrar
- Padrão da indústria

---

### Opção 2: hf.diotec360.com
```
Nome: hf
Tipo: CNAME
Valor: diotec-diotec360-judge.hf.space
TTL: 60
```

**Vantagens:**
- Identifica claramente que é Hugging Face
- Separação clara de outros serviços

---

### Opção 3: judge.diotec360.com
```
Nome: judge
Tipo: CNAME
Valor: diotec-diotec360-judge.hf.space
TTL: 60
```

**Vantagens:**
- Nome descritivo do serviço
- Alinhado com o nome do Space

---

## 📋 PASSO A PASSO - CONFIGURAÇÃO NO VERCEL

### 1. Acessar Dashboard do Vercel

1. Vá para: https://vercel.com/dashboard
2. Selecione o domínio `diotec360.com`
3. Clique em "DNS" ou "Domains"

---

### 2. Adicionar Registro CNAME

**No painel DNS do Vercel:**

```
Type: CNAME
Name: api (ou hf, ou judge)
Value: diotec-diotec360-judge.hf.space
TTL: 60
```

**Importante:**
- Não adicione `.diotec360.com` no campo Name
- Apenas o subdomínio: `api` ou `hf` ou `judge`
- O Vercel adiciona automaticamente o domínio principal

---

### 3. Aguardar Propagação DNS

**Tempo de propagação:**
- TTL 60 segundos: 2-5 minutos
- Propagação global: até 24 horas (raro)

**Verificar propagação:**
```bash
# Windows (CMD)
nslookup api.diotec360.com

# Esperado:
# Name: diotec-diotec360-judge.hf.space
# Address: [IP do Hugging Face]
```

---

### 4. Testar o Subdomínio

```bash
# Teste básico
curl https://api.diotec360.com/health

# Esperado:
{
  "status": "healthy",
  "version": "3.0.5"
}
```

---

## ✅ CONFIGURAÇÃO FINAL ESCOLHIDA

**Subdomínio escolhido:** `hf.diotec360.com`

**Motivo:** `api.diotec360.com` já está em uso por outra plataforma backend

```
┌─────────────────────────────────────────────────────────┐
│         SUBDOMÍNIO HUGGING FACE                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🌐 Subdomínio Personalizado                            │
│  └─ https://hf.diotec360.com                            │
│     └─ DNS: CNAME → diotec-diotec360-judge.hf.space       │
│                                                         │
│  🚀 Hugging Face Space                                  │
│  └─ https://huggingface.co/spaces/diotec/diotec360-judge  │
│     └─ URL direta: diotec-diotec360-judge.hf.space        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 ATUALIZAR CONFIGURAÇÕES

### Frontend (.env.production)
```env
# Usar o novo subdomínio
NEXT_PUBLIC_API_URL=https://hf.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://node2.diotec360.com,https://backup.diotec360.com
```

### Node 2 e Node 3
```env
# Atualizar peers para usar o novo subdomínio
DIOTEC360_LATTICE_NODES=https://hf.diotec360.com,...
```

---

## 🎯 AÇÃO IMEDIATA

**Execute agora no dashboard do Vercel:**

1. Acesse: https://vercel.com/dashboard
2. Selecione `diotec360.com`
3. Vá em "DNS"
4. Clique em "Add Record"
5. Configure:
   - Type: `CNAME`
   - Name: `hf`
   - Value: `diotec-diotec360-judge.hf.space`
   - TTL: `60`
6. Clique em "Save"

**Aguarde 2-5 minutos e teste:**
```bash
curl https://hf.diotec360.com/health
```

---

## 📊 VANTAGENS DO SUBDOMÍNIO PERSONALIZADO

✅ **Profissionalismo:**
- URL limpa e memorável
- Marca própria (diotec360.com)
- Sem referência direta ao Hugging Face

✅ **Flexibilidade:**
- Pode mudar o backend sem alterar a URL
- Fácil de migrar para outro serviço
- Controle total sobre o DNS

✅ **SEO e Marketing:**
- Domínio próprio melhora SEO
- Mais confiável para usuários
- Facilita divulgação

---

## ⚠️ IMPORTANTE

**SSL/HTTPS:**
- O Hugging Face já fornece SSL
- O CNAME mantém o SSL do HF
- Não precisa configurar certificado

**Limitações:**
- O Hugging Face Space deve estar público
- Não pode usar domínio raiz (apenas subdomínio)
- TTL mínimo recomendado: 60 segundos

---

## 🎯 PRÓXIMOS PASSOS

1. **Configurar DNS** no Vercel (5 min)
2. **Aguardar propagação** (2-5 min)
3. **Testar subdomínio** (1 min)
4. **Atualizar configurações** dos outros nós (5 min)
5. **Verificar Triangle** completo (2 min)

---

**🚀 SUBDOMÍNIO PERSONALIZADO PARA HUGGING FACE 🚀**

**Qual subdomínio você prefere?**
- `api.diotec360.com` (Recomendado)
- `hf.diotec360.com`
- `judge.diotec360.com`
- Outro? (Sugira!)

**Aguardando sua escolha! 🌌✨**
