# Hospital Review Frontend - Setup Guide

## Project Structure

This is a **pure JSX React + Vite + Node.js** application for hospital reviews with sentiment analysis.

### Cleaned Structure
```
frontend/
├── public/           # Static assets
│   └── index.html
├── src/
│   ├── components/   # Main React components (JSX)
│   │   ├── EmptyState.jsx
│   │   ├── FilterBar.jsx
│   │   ├── HospitalProfile.jsx
│   │   ├── ReviewCard.jsx
│   │   ├── ReviewDialog.jsx
│   │   └── ui/       # shadcn/ui components (TSX - library components)
│   ├── hooks/        # Custom React hooks
│   │   └── use-mobile.js
│   ├── lib/          # Utility functions
│   │   ├── api.js
│   │   ├── hospital-stats.js
│   │   └── utils.js
│   ├── styles/       # CSS files
│   │   └── theme.css
│   ├── App.jsx       # Main application component
│   ├── ErrorFallback.jsx
│   ├── index.css
│   ├── main.css
│   └── main.jsx      # Application entry point
├── .env.example      # Environment variables template
├── .gitignore
├── index.html        # HTML entry point
├── package.json      # Dependencies and scripts
├── README.md         # Project documentation
├── tailwind.config.js
└── vite.config.js    # Vite configuration
```

## Installation & Setup

### Prerequisites
- **Node.js** version 18.x or higher
- **npm** or **yarn** package manager

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Configure Environment Variables
Create a `.env` file in the frontend root:
```bash
cp .env.example .env
```

Edit `.env` and set your backend API URL:
```
VITE_API_URL=http://localhost:5000
```

### Step 3: Start Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or another port if 5173 is in use).

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build production-ready app |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint to check code quality |

## About TypeScript Remnants

### Why some `.tsx` files remain?

The **UI components** in `src/components/ui/` are from the **shadcn/ui** library and are written in TypeScript (`.tsx`). These are kept because:

1. **Library Components**: They're pre-built UI components (buttons, dialogs, cards, etc.)
2. **Vite Compatibility**: Vite can process `.tsx` files even in a JSX project with the React plugin
3. **No Breaking Changes**: Your main application code is pure JSX and imports these components seamlessly

### What was removed?
- ✅ All duplicate `.tsx` versions of main app components
- ✅ TypeScript configuration files (`tsconfig.json`, `vite.config.ts`)
- ✅ TypeScript dependencies from `package.json`
- ✅ Type definition files (`.d.ts`, `types.ts`)
- ✅ Unnecessary documentation files (PRD.md, DEPLOYMENT_GUIDE.md, etc.)
- ✅ Redundant config files (components.json, theme.json, etc.)

## Architecture

### Technology Stack
- **React 19**: UI framework
- **Vite 7**: Fast build tool and dev server
- **Tailwind CSS 4**: Utility-first CSS framework
- **shadcn/ui**: Pre-built accessible UI components
- **Radix UI**: Headless UI primitives
- **Framer Motion**: Animation library
- **React Error Boundary**: Error handling

### API Integration
The app connects to a Flask backend API for:
- Fetching hospital reviews
- Creating new reviews
- Sentiment analysis

API configuration is in `src/lib/api.js`.

## Backend Integration

Make sure your backend is running before starting the frontend:

```bash
# In the backend directory
cd ../backend
python app.py
```

The backend should be running on `http://localhost:5000`.

## Production Build

To create a production build:

```bash
npm run build
```

This creates an optimized build in the `dist/` directory, ready for deployment.

To test the production build locally:

```bash
npm run preview
```

## Troubleshooting

### Port Already in Use
If port 5173 is already in use, Vite will automatically use the next available port. Check the terminal output for the actual URL.

### API Connection Issues
- Verify the backend is running on the correct port
- Check the `VITE_API_URL` in your `.env` file
- Ensure CORS is properly configured in the backend

### Module Not Found Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

1. **Hot Reload**: Changes to JSX/CSS files will automatically update in the browser
2. **Error Overlay**: Vite shows a helpful error overlay for build/runtime errors
3. **Component Import**: Use the `@/` alias for cleaner imports (e.g., `import { api } from '@/lib/api'`)
4. **Styling**: This project uses Tailwind CSS - check the official docs for utility classes

## License

This project is for educational purposes (HFU - Web Programming course).
