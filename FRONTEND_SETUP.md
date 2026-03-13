# diotec360-studio Frontend Setup

Complete guide to set up and deploy the diotec360-studio frontend.

---

## 🚀 Quick Start

```bash
# Navigate to project root
cd diotec360-lang

# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

# Navigate to frontend
cd frontend

# Install additional dependencies
npm install @monaco-editor/react
npm install lucide-react
npm install @radix-ui/react-tabs
npm install class-variance-authority clsx tailwind-merge

# Run development server
npm run dev
```

Open http://localhost:3000

---

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main playground page
│   └── globals.css          # Global styles
├── components/
│   ├── Editor.tsx           # Monaco code editor
│   ├── ProofViewer.tsx      # Verification results
│   ├── MerkleTree.tsx       # State tree visualization
│   ├── Console.tsx          # Output console
│   └── ExampleSelector.tsx  # Example code selector
├── lib/
│   ├── api.ts               # API client
│   └── utils.ts             # Utility functions
├── public/
│   └── favicon.ico
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

---

## 🎨 Design System

### Colors (Dark Mode)
- **Background**: `#0a0a0a` (near black)
- **Surface**: `#1a1a1a` (dark gray)
- **Border**: `#2a2a2a` (medium gray)
- **Text**: `#ffffff` (white)
- **Accent**: `#3b82f6` (blue)
- **Success**: `#10b981` (green)
- **Error**: `#ef4444` (red)

### Typography
- **Font**: Inter (system font)
- **Mono**: JetBrains Mono (code)

### Layout
- **Split View**: 50/50 editor and viewer
- **Responsive**: Stack on mobile
- **Spacing**: 4px grid system

---

## 🔌 API Integration

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://your-railway-api.up.railway.app
```

### API Client

The API client (`lib/api.ts`) provides:
- `verifyCode(code: string)` - Verify Aethel code
- `compileCode(code: string)` - Compile to implementation
- `getExamples()` - Fetch example code
- `getVaultFunctions()` - List vault functions

---

## 🎯 Features

### Phase 1 (MVP)
- [x] Monaco Editor with Aethel syntax
- [x] Verify button
- [x] Proof result display
- [x] Example code selector
- [x] Dark mode UI

### Phase 2
- [ ] Merkle Tree visualization
- [ ] Share functionality
- [ ] Execution viewer
- [ ] Vault browser

### Phase 3
- [ ] Real-time collaboration
- [ ] AI-powered suggestions
- [ ] Mobile app
- [ ] VS Code extension

---

## 🚀 Deployment to Vercel

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel

# Production deployment
vercel --prod
```

### Option 2: GitHub Integration

1. Go to https://vercel.com
2. Sign in with GitHub
3. "New Project"
4. Import `diotec360-lang` repository
5. Set root directory to `frontend`
6. Add environment variable: `NEXT_PUBLIC_API_URL`
7. Deploy!

---

## 🧪 Testing

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

---

## 📊 Performance

### Optimization
- Code splitting (automatic with Next.js)
- Image optimization (Next.js Image component)
- Font optimization (next/font)
- Monaco Editor lazy loading

### Metrics
- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Lighthouse Score**: > 90

---

## 🐛 Troubleshooting

### Monaco Editor not loading

```bash
# Ensure @monaco-editor/react is installed
npm install @monaco-editor/react

# Check import in Editor.tsx
import Editor from '@monaco-editor/react';
```

### API calls failing

```bash
# Check NEXT_PUBLIC_API_URL in .env.local
echo $NEXT_PUBLIC_API_URL

# Test API directly
curl https://your-api-url.com/health
```

### Build errors

```bash
# Clear cache
rm -rf .next
rm -rf node_modules
npm install
npm run build
```

---

## 📝 Next Steps

1. ✅ Set up Next.js project
2. ✅ Create components
3. ✅ Integrate API
4. ⏳ Deploy to Vercel
5. ⏳ Test end-to-end
6. ⏳ Public launch

---

**Ready to build? Follow the Quick Start guide above!**
