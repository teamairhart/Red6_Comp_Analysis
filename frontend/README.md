# Red 6 Competitive Intelligence Platform - Frontend

A modern Next.js 14 frontend for the Red 6 Competitive Intelligence Platform, built with React, TypeScript, Tailwind CSS, and shadcn/ui.

## Prerequisites

- Node.js 18.x or higher
- npm or yarn
- Backend API running on `http://localhost:8000`

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx            # Dashboard
│   │   ├── research/           # Research workflow
│   │   │   ├── page.tsx        # New research form
│   │   │   └── [jobId]/        # Research progress & results
│   │   ├── reports/            # Report history
│   │   ├── prompts/            # Prompt library
│   │   ├── sources/            # Source library
│   │   ├── briefing/           # Intelligence briefing
│   │   ├── schedules/          # Scheduled research
│   │   ├── loading.tsx         # Global loading skeleton
│   │   ├── error.tsx           # Error boundary
│   │   ├── not-found.tsx       # 404 page
│   │   └── layout.tsx          # Root layout
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── navigation.tsx      # Main navigation
│   │   ├── animations.tsx      # Framer Motion animations
│   │   ├── theme-provider.tsx  # Dark mode provider
│   │   ├── theme-toggle.tsx    # Dark mode toggle
│   │   ├── error-state.tsx     # Error display component
│   │   └── empty-state.tsx     # Empty state component
│   └── lib/
│       └── utils.ts            # Utility functions
├── public/                     # Static assets
├── package.json
└── README.md
```

## Features

### Core Features
- **Dashboard** - Overview with quick actions and tracked competitors
- **Research Workflow** - Execute competitive intelligence research with multiple AI providers
- **Reports** - Browse, view, and download research reports
- **Prompt Library** - View and manage research prompts by category
- **Source Library** - Curated sources for competitive intelligence

### Advanced Features
- **Intelligence Briefing** - Delta analysis showing what's new across all research
- **Company Timeline** - Chronological view of findings per company
- **Scheduled Research** - Automated recurring research with notifications
- **In-App Notifications** - Real-time updates for completed research and critical findings

### UI/UX Features
- **Dark Mode** - System-aware theme with manual toggle
- **Responsive Design** - Mobile-first design with collapsible navigation
- **Loading Skeletons** - Smooth loading states for all pages
- **Micro-Animations** - Subtle animations using Framer Motion
- **Error Boundaries** - Graceful error handling with retry options

## Available Scripts

```bash
# Development
npm run dev          # Start development server

# Production
npm run build        # Build for production
npm run start        # Start production server

# Linting
npm run lint         # Run ESLint
```

## Environment Configuration

The frontend connects to the backend API at `http://localhost:8000` by default. This is configured in the page components and `navigation.tsx`.

For production, update the `API_BASE` constant in relevant files or set up environment variables.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI Components**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Theme**: next-themes
- **Markdown**: react-markdown + remark-gfm
- **Icons**: Lucide React

## Pages Overview

| Route | Description |
|-------|-------------|
| `/` | Dashboard with quick actions |
| `/research` | Start new research |
| `/research/[jobId]` | Research progress tracking |
| `/research/[jobId]/results` | View research results |
| `/reports` | Browse all reports |
| `/reports/[id]` | View single report |
| `/prompts` | Prompt library |
| `/sources` | Source library |
| `/briefing` | Intelligence briefing |
| `/briefing/company/[company]` | Company timeline |
| `/schedules` | Manage scheduled research |

## API Integration

The frontend communicates with the FastAPI backend through REST endpoints:

- `GET /api/prompts` - List all prompts
- `POST /api/research` - Start new research
- `GET /api/research/{job_id}` - Get research status
- `GET /api/reports` - List all reports
- `GET /api/sources` - List all sources
- `GET /api/delta/briefing` - Get intelligence briefing
- `GET /api/schedules` - List all schedules
- `GET /api/schedules/notifications/all` - Get notifications

## Development Notes

### Adding New Pages
1. Create page file in `src/app/[route]/page.tsx`
2. Add loading skeleton in `src/app/[route]/loading.tsx`
3. Add error boundary in `src/app/[route]/error.tsx` (optional)
4. Add to navigation in `src/components/navigation.tsx`

### Using Animations
```tsx
import { FadeIn, StaggerChildren, StaggerItem } from "@/components/animations";

// Wrap content with animation components
<FadeIn delay={0.1}>
  <YourComponent />
</FadeIn>

// For lists
<StaggerChildren>
  {items.map(item => (
    <StaggerItem key={item.id}>
      <ItemComponent item={item} />
    </StaggerItem>
  ))}
</StaggerChildren>
```

### Theme Support
The app uses `next-themes` for dark mode. Use Tailwind's `dark:` variant for dark mode styles:

```tsx
<div className="bg-white dark:bg-gray-900">
  Content
</div>
```

## Troubleshooting

### API Connection Issues
- Ensure the backend is running on port 8000
- Check CORS configuration in backend
- Verify network connectivity

### Build Errors
- Clear `.next` folder and node_modules
- Run `npm install` again
- Check for TypeScript errors with `npx tsc --noEmit`

### Styling Issues
- Clear browser cache
- Check Tailwind config
- Verify CSS imports in `globals.css`
