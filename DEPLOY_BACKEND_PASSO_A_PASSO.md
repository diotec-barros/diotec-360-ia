# Deploy Backend - Passo a Passo

## Preparação Concluída ✅

- ✅ Vercel CLI instalado
- ✅ Autenticação realizada
- ✅ DNS configurado (api.diotec360.com)
- ✅ vercel.json atualizado com CORS e variáveis

## Passo 1: Executar Deploy

Abra o PowerShell na raiz do projeto e execute:

```powershell
vercel --prod
```

## Passo 2: Responder às Perguntas

O Vercel CLI fará as seguintes perguntas. Responda conforme abaixo:

### Pergunta 1: Set up and deploy?
```
? Set up and deploy "~\diotec360"? (Y/n)
```
**Resposta**: `Y` (ou apenas Enter)

### Pergunta 2: Which scope?
```
? Which scope should contain your project?
> diotec-barros' projects
```
**Resposta**: Selecione `diotec-barros` (use setas e Enter)

### Pergunta 3: Link to existing project?
```
? Link to existing project? (y/N)
```
**Resposta**: `N` (ou apenas Enter)

### Pergunta 4: Project name?
```
? What's your project's name? (diotec360)
```
**Resposta**: `diotec360-api` (digite e Enter)

### Pergunta 5: Directory?
```
? In which directory is your code located? (.)
```
**Resposta**: `.` (apenas Enter - raiz do projeto)

### Pergunta 6: Override settings?
```
? Want to override the settings? (y/N)
```
**Resposta**: `N` (ou apenas Enter)

## Passo 3: Aguardar Build

O Vercel fará o build e deploy. Você verá:

```
🔗  Linked to diotec-barros/diotec360-api (created .vercel)
🔍  Inspect: https://vercel.com/diotec-barros/diotec360-api/...
✅  Production: https://diotec360-api-xxx.vercel.app [2m]
```

## Passo 4: Adicionar Domínio Customizado

Após o deploy bem-sucedido, adicione o domínio:

```powershell
vercel domains add api.diotec360.com
```

O Vercel perguntará:

```
? Add api.diotec360.com to diotec360-api? (Y/n)
```
**Resposta**: `Y` (ou apenas Enter)

## Passo 5: Verificar

Aguarde alguns minutos e teste:

```powershell
curl https://api.diotec360.com/
```

Resposta esperada:
```json
{
  "name": "DIOTEC 360 IA API",
  "version": "1.7.0",
  "release": "Oracle Sanctuary",
  "status": "operational"
}
```

## Troubleshooting

### Erro: "Domain is already in use"

Se o domínio já estiver em uso, remova primeiro:
```powershell
vercel domains rm api.diotec360.com
```

Depois adicione novamente:
```powershell
vercel domains add api.diotec360.com
```

### Erro: "Build failed"

Verifique os logs:
```powershell
vercel logs diotec360-api
```

### Erro: "DNS not configured"

Verifique o DNS:
```powershell
nslookup api.diotec360.com
```

Deve retornar um CNAME apontando para `cname.vercel-dns.com`

## Configurações Aplicadas

O arquivo `vercel.json` foi atualizado com:

- ✅ CORS headers para `https://app.diotec360.com`
- ✅ Variáveis de ambiente de produção
- ✅ Node name: `api-production`
- ✅ Node role: `genesis`
- ✅ Lattice nodes incluindo Hugging Face

## Próximo Passo

Após o backend estar online, faremos o deploy do frontend:
- URL: https://app.diotec360.com
- Diretório: `frontend/`

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
