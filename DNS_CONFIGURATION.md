# Configuração DNS - DIOTEC 360

## Registros DNS Necessários

Configure os seguintes registros CNAME no seu provedor de DNS (GoDaddy, Namecheap, Cloudflare, etc.):

### Formato Padrão

| Tipo  | Nome/Host | Valor/Destino          | TTL  |
|-------|-----------|------------------------|------|
| CNAME | api       | cname.vercel-dns.com   | 3600 |
| CNAME | app       | cname.vercel-dns.com   | 3600 |

### Formato Completo (alguns provedores)

| Tipo  | Nome/Host             | Valor/Destino          | TTL  |
|-------|-----------------------|------------------------|------|
| CNAME | api.diotec360.com     | cname.vercel-dns.com   | 3600 |
| CNAME | app.diotec360.com     | cname.vercel-dns.com   | 3600 |

## Instruções por Provedor

### GoDaddy

1. Acesse https://dcc.godaddy.com/manage/diotec360.com/dns
2. Clique em "Add" (Adicionar)
3. Selecione "CNAME" no tipo
4. Configure:
   - **Name**: `api`
   - **Value**: `cname.vercel-dns.com`
   - **TTL**: `1 Hour` (3600 segundos)
5. Clique em "Save"
6. Repita para `app`

### Namecheap

1. Acesse https://ap.www.namecheap.com/domains/domaincontrolpanel/diotec360.com/advancedns
2. Clique em "Add New Record"
3. Configure:
   - **Type**: `CNAME Record`
   - **Host**: `api`
   - **Value**: `cname.vercel-dns.com`
   - **TTL**: `Automatic`
4. Clique em "Save"
5. Repita para `app`

### Cloudflare

1. Acesse https://dash.cloudflare.com
2. Selecione o domínio `diotec360.com`
3. Vá para "DNS" → "Records"
4. Clique em "Add record"
5. Configure:
   - **Type**: `CNAME`
   - **Name**: `api`
   - **Target**: `cname.vercel-dns.com`
   - **Proxy status**: 🔴 DNS only (desabilitar proxy)
   - **TTL**: `Auto`
6. Clique em "Save"
7. Repita para `app`

**Importante**: No Cloudflare, desabilite o proxy (ícone laranja) para que o Vercel possa gerenciar o SSL.

### Google Domains

1. Acesse https://domains.google.com/registrar/diotec360.com/dns
2. Role até "Custom resource records"
3. Configure:
   - **Name**: `api`
   - **Type**: `CNAME`
   - **TTL**: `1H`
   - **Data**: `cname.vercel-dns.com`
4. Clique em "Add"
5. Repita para `app`

### Route 53 (AWS)

1. Acesse https://console.aws.amazon.com/route53
2. Selecione a hosted zone `diotec360.com`
3. Clique em "Create record"
4. Configure:
   - **Record name**: `api`
   - **Record type**: `CNAME`
   - **Value**: `cname.vercel-dns.com`
   - **TTL**: `300`
5. Clique em "Create records"
6. Repita para `app`

## Verificação DNS

### Windows (PowerShell)

```powershell
# Verificar CNAME
Resolve-DnsName -Name api.diotec360.com -Type CNAME
Resolve-DnsName -Name app.diotec360.com -Type CNAME

# Verificar propagação
nslookup api.diotec360.com
nslookup app.diotec360.com
```

### Linux/Mac (Terminal)

```bash
# Verificar CNAME
dig api.diotec360.com CNAME
dig app.diotec360.com CNAME

# Verificar propagação
nslookup api.diotec360.com
nslookup app.diotec360.com
```

### Online (Navegador)

Ferramentas úteis para verificar propagação DNS:
- https://dnschecker.org
- https://www.whatsmydns.net
- https://mxtoolbox.com/SuperTool.aspx

## Tempo de Propagação

- **Mínimo**: 5-15 minutos
- **Típico**: 1-2 horas
- **Máximo**: 24-48 horas

**Dica**: Use TTL baixo (300-600 segundos) durante a configuração inicial para facilitar testes.

## Troubleshooting

### Erro: CNAME já existe

**Causa**: Já existe um registro A ou CNAME com o mesmo nome.

**Solução**: 
1. Remova o registro existente
2. Adicione o novo CNAME

### Erro: DNS não propaga

**Causa**: Cache DNS local ou do provedor.

**Solução**:
```powershell
# Windows - Limpar cache DNS
ipconfig /flushdns

# Linux/Mac - Limpar cache DNS
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### Erro: Vercel não reconhece domínio

**Causa**: DNS ainda não propagou ou configuração incorreta.

**Solução**:
1. Aguarde mais tempo (até 48h)
2. Verifique se o CNAME aponta para `cname.vercel-dns.com`
3. Verifique se não há proxy ativo (Cloudflare)

## Configuração Completa

Após configurar o DNS, siga os passos no arquivo `VERCEL_SUBDOMINIOS_GUIA.md`:

1. ✅ Configurar DNS (este documento)
2. 🔄 Criar projetos no Vercel
3. 🔄 Adicionar domínios customizados
4. 🔄 Configurar variáveis de ambiente
5. 🔄 Deploy e teste

## Resultado Esperado

Após a propagação DNS, você deve conseguir acessar:

- **Backend API**: https://api.diotec360.com
- **Frontend App**: https://app.diotec360.com

Ambos com certificado SSL válido (Let's Encrypt via Vercel).

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
