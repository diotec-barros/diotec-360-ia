# 🚀 INSTRUÇÕES DE DEPLOY NO HUGGING FACE

**Versão**: v1.3.1 "The Conservation Guardian"  
**Data**: 3 de Fevereiro de 2026

---

## ✅ ARQUIVOS CRIADOS

Os seguintes arquivos foram criados e estão prontos para upload:

1. ✅ **README.md** - Configuração do Space + Documentação
2. ✅ **requirements.txt** - Dependências Python
3. ✅ **Dockerfile** - Container configuration

---

## 📋 PASSO A PASSO NO HUGGING FACE

### PASSO 1: Upload dos Arquivos de Configuração

1. Vá para seu Space no Hugging Face
2. Clique em **"Files and versions"**
3. Clique em **"Add file"** → **"Upload files"**
4. Arraste e solte os seguintes arquivos:
   - `README.md`
   - `requirements.txt`
   - `Dockerfile`
5. Clique em **"Commit changes to main"**

### PASSO 2: Upload das Pastas de Código

1. Ainda em **"Files and versions"**
2. Clique em **"Add file"** → **"Upload files"**
3. Arraste e solte as seguintes pastas:
   - **Pasta `aethel/`** (inteira, com todas as subpastas)
   - **Pasta `api/`** (inteira, com todos os arquivos)
4. Clique em **"Commit changes to main"**

### PASSO 3: Aguardar Build

1. Após o commit, você verá uma etiqueta **amarela** escrita **"Building"**
2. O build leva aproximadamente **5-10 minutos**
3. Quando a etiqueta ficar **verde** e escrita **"Running"**, está pronto!

### PASSO 4: Obter URL da API

1. Quando o Space estiver **"Running"**
2. Clique no menu de **3 pontinhos** (ao lado de "Settings" no topo)
3. Escolha **"Embed this Space"**
4. Copie o **"Direct URL"**
   - Será algo como: `https://diotec-diotec360-judge.hf.space`

### PASSO 5: Atualizar Frontend na Vercel

1. Vá para o dashboard da Vercel
2. Selecione o projeto do frontend Aethel
3. Vá em **"Settings"** → **"Environment Variables"**
4. Edite a variável **`NEXT_PUBLIC_API_URL`**
5. Cole a URL do Hugging Face (sem barra no final)
6. Clique em **"Save"**
7. Vá em **"Deployments"** e clique em **"Redeploy"**

---

## 🔍 VERIFICAÇÃO

### Testar a API Diretamente

Abra no navegador:
```
https://seu-space.hf.space/docs
```

Você verá a documentação interativa da API (Swagger UI).

### Testar um Exemplo

Use o endpoint `/verify` com este código:

```json
{
  "code": "intent test(sender: Account, receiver: Account, amount: Balance) { guard { old_sender_balance >= amount; amount > 0; } verify { sender_balance == old_sender_balance - amount; receiver_balance == old_receiver_balance + amount; } }"
}
```

**Resultado esperado**: `{"status": "PROVED", ...}`

---

## 📊 ESTRUTURA DE PASTAS NO HUGGING FACE

Após o upload, a estrutura deve ficar assim:

```
/
├── README.md
├── requirements.txt
├── Dockerfile
├── aethel/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── architect.py
│   │   ├── bridge.py
│   │   ├── conservation.py  ← NOVO v1.3!
│   │   ├── ghost.py
│   │   ├── grammar.py
│   │   ├── judge.py
│   │   ├── kernel.py
│   │   ├── lens.py
│   │   ├── mirror.py
│   │   ├── parser.py
│   │   ├── runtime.py
│   │   ├── state.py
│   │   ├── vault.py
│   │   ├── vault_distributed.py
│   │   ├── wasm_compiler.py
│   │   ├── wasm_runtime.py
│   │   └── weaver.py
│   └── examples/
│       ├── finance.ae
│       ├── finance_exploit.ae
│       ├── global_bank.ae
│       ├── README.md
│       └── vote.ae
└── api/
    ├── __init__.py
    ├── main.py
    ├── requirements.txt
    └── Dockerfile
```

---

## ⚠️ TROUBLESHOOTING

### Build Falhou?

**Erro comum**: "No module named 'aethel'"

**Solução**: Verifique se a pasta `aethel/` foi enviada corretamente e contém o arquivo `__init__.py`

### API não responde?

**Erro comum**: "Application startup failed"

**Solução**: 
1. Clique em **"Logs"** no Space
2. Procure por erros de import
3. Verifique se todas as dependências estão em `requirements.txt`

### Port 7860 não funciona?

**Solução**: Verifique se o `README.md` tem a linha:
```yaml
app_port: 7860
```

---

## 🎯 CHECKLIST FINAL

Antes de considerar o deploy completo, verifique:

- [ ] README.md enviado e configurado
- [ ] requirements.txt enviado
- [ ] Dockerfile enviado
- [ ] Pasta `aethel/` enviada (com todas as subpastas)
- [ ] Pasta `api/` enviada
- [ ] Build completou com sucesso (etiqueta verde "Running")
- [ ] API responde em `/docs`
- [ ] Endpoint `/verify` funciona
- [ ] Frontend atualizado com nova URL
- [ ] Frontend consegue se comunicar com a API

---

## 🌟 PRÓXIMOS PASSOS

Após o deploy bem-sucedido:

1. ✅ Testar exemplos em produção
2. ✅ Validar Conservation Checker funcionando
3. ✅ Compartilhar URL pública
4. ✅ Documentar casos de uso
5. ✅ Planejar v1.4

---

## 📞 SUPORTE

Se encontrar problemas:

1. Verifique os **Logs** no Hugging Face Space
2. Teste a API localmente primeiro: `python -m uvicorn api.main:app --reload`
3. Consulte a documentação do Hugging Face: https://huggingface.co/docs/hub/spaces

---

**Versão**: v1.3.1  
**Status**: Pronto para Deploy  
**Tempo Estimado**: 10-15 minutos

🚀 **Boa sorte com o deploy!** 🚀
