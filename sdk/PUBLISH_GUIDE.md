# 📦 DIOTEC 360 SDK - Guia de Publicação

**Como publicar o SDK no NPM**

---

## 🔐 Pré-requisitos

1. Conta no NPM: https://www.npmjs.com/signup
2. Organização `@diotec360` criada no NPM
3. Token de autenticação configurado

---

## 📝 Passo a Passo

### 1. Login no NPM

```bash
npm login
```

### 2. Criar Organização (primeira vez)

```bash
npm org create diotec360
```

### 3. Verificar package.json

Certifique-se que o `package.json` está correto:
- ✅ Nome: `@diotec360/sdk`
- ✅ Versão: `1.0.0`
- ✅ Arquivos incluídos no `files` array

### 4. Testar Localmente

```bash
cd diotec360/sdk
npm pack
```

Isso cria um arquivo `.tgz` que você pode testar:

```bash
npm install ./diotec360-sdk-1.0.0.tgz
```

### 5. Publicar

```bash
npm publish --access public
```

---

## 🎯 Após Publicação

### Verificar no NPM
https://www.npmjs.com/package/@diotec360/sdk

### Instalar em Qualquer Projeto
```bash
npm install @diotec360/sdk
```

### Atualizar Versão (futuras releases)

```bash
# Patch (1.0.0 -> 1.0.1)
npm version patch

# Minor (1.0.0 -> 1.1.0)
npm version minor

# Major (1.0.0 -> 2.0.0)
npm version major

# Publicar nova versão
npm publish
```

---

## 📊 Estatísticas

Após publicar, monitore:
- Downloads: https://npm-stat.com/charts.html?package=@diotec360/sdk
- Dependentes: https://www.npmjs.com/package/@diotec360/sdk?activeTab=dependents

---

## 🔗 Links Importantes

- NPM Package: https://www.npmjs.com/package/@diotec360/sdk
- GitHub Repo: https://github.com/diotec-barros/diotec-360-ia-extension
- Documentation: https://diotec360.com/docs
- API Status: https://status.diotec360.com

---

🏛️ **DIOTEC 360 IA** - The TCP/IP of Honesty  
📦 **NPM Package** - `@diotec360/sdk`  
🛡️ **"DIOTEC Inside"** - Every App, Everywhere
