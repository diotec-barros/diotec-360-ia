# Aethel Studio - Frontend

Interactive web playground for the Aethel programming language.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 🏗️ Tech Stack

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Monaco Editor** - Code editor (VS Code in browser)
- **Lucide React** - Icons

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main playground page
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── Editor.tsx        # Monaco code editor
│   ├── ProofViewer.tsx   # Verification results
│   └── ExampleSelector.tsx # Example code selector
├── lib/
│   ├── api.ts            # API client
│   └── utils.ts          # Utility functions
└── public/
```

## 🔌 API Integration

The frontend connects to the Aethel backend API. Configure the API URL in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, use your Railway/Render deployment URL:

```env
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
```

## 🎨 Features

- **Monaco Editor** - Full-featured code editor with syntax highlighting
- **Real-time Verification** - Verify code with Z3 theorem prover
- **Proof Viewer** - See verification results and audit trails
- **Example Code** - Load example Aethel programs
- **Dark Mode** - Cyber-minimalist design
- **Responsive** - Works on desktop and mobile

## 🚀 Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

Or use the Vercel dashboard:
1. Go to https://vercel.com
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy!

## 🧪 Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 📝 Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (required)

## 🐛 Troubleshooting

### Monaco Editor not loading
Ensure `@monaco-editor/react` is installed and the Editor component is dynamically imported.

### API calls failing
Check that the backend API is running and `NEXT_PUBLIC_API_URL` is set correctly.

### Build errors
Clear cache and reinstall:
```bash
rm -rf .next node_modules
npm install
npm run build
```

## 📚 Learn More

- [Aethel Documentation](https://github.com/diotec-barros/diotec360-lang)
- [Next.js Documentation](https://nextjs.org/docs)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)

## 🎯 Roadmap

- [x] Monaco Editor integration
- [x] Verification with Judge
- [x] Proof viewer
- [x] Example code selector
- [ ] Merkle Tree visualization
- [ ] Share functionality
- [ ] Real-time collaboration
- [ ] Mobile app

---

**Genesis Merkle Root**: `1e994337bc48d0b2c293f9ac28b883ae68c0739e24307a32e28c625f19912642`

The future is not written in code. It is proved in theorems.
