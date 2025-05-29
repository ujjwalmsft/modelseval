new-eval-frontend
├── public/
│   ├── file.svg                  # SVG assets
│   ├── globe.svg                 # SVG assets
│   ├── next.svg                  # Next.js default logo
│   ├── vercel.svg                # Vercel default logo
│   └── window.svg                # SVG assets
│
├── src/
│   └── app/
│       ├── auth/
│       │   ├── authContext.tsx  # Authentication context component
│       │   └── msalConfig.ts     # MSAL (Microsoft Authentication Library) configuration
│       │
│       ├── compare/
│       │   ├── components/
│       │   │   ├── ComparisonModeSelector.tsx  # Component for selecting comparison modes
│       │   │   ├── ComparisonView.tsx          # Main comparison view component
│       │   │   ├── ContextInput.tsx            # Input component for context data
│       │   │   ├── EvaluationMetrics.tsx       # Displays quantitative evaluation metrics
│       │   │   ├── JudgeSummary.tsx            # Summarizes qualitative evaluation results
│       │   │   ├── ModelResponseCard.tsx       # Component to display individual model responses
│       │   │   ├── QueryInput.tsx              # Input component for user queries
│       │   │   ├── RunMetadata.tsx             # Displays run metadata (time, model, etc.)
│       │   │   └── ScoreBreakdown.tsx          # Detailed scoring breakdown component
│       │   │
│       │   ├── layout.tsx                      # Layout specific to compare pages
│       │   └── page.tsx                       # Main compare page component
│       │
│       ├── components/
│       │   ├── FeatureCard.tsx                 # Card component for highlighting features
│       │   ├── FeaturesSection.tsx             # Section to list platform features
│       │   ├── Header.tsx                      # Header component for app
│       │   ├── HeroSection.tsx                 # Hero section on homepage or landing page
│       │   ├── login.tsx                       # Login component for authentication
│       │   ├── ModelComparisonPreview.tsx      # Preview component for model comparison
│       │   └── UserProfile.tsx                # User profile management component
│       │
│       ├── content/
│       │   ├── featureData.tsx                 # Data for feature sections
│       │   └── modelData.ts                   # Data definitions for models
│       │
│       ├── context/
│       │   └── ModelContext.tsx               # Context provider for sharing model data
│       │
│       ├── services/
│       │   ├── apiConfig.ts                    # API configuration settings
│       │   ├── ApiService.ts                   # Generic API service for backend communication
│       │   └── SignalRService.ts              # Real-time communication (if not used, remove explicitly)
│       │
│       ├── favicon.ico                         # App favicon
│       ├── globals.css                         # Global CSS styles
│       ├── layout.tsx                          # Global app layout
│       └── page.tsx                            # Root application page
│
├── theme/
│   └── theme.ts                                # Theme definitions (colors, fonts, styles)
│
├── .gitignore                                  # Git ignore rules
├── eslint.config.mjs                          # ESLint configuration
├── next.config.ts                              # Next.js configuration file
├── package-lock.json                          # Package lock file for npm dependencies
├── package.json                                # Package file for npm dependencies
├── postcss.config.mjs                         # PostCSS configuration
├── README.md                                   # Documentation for frontend
├── Structure.md                                # Directory and project structure notes
└── tsconfig.json                              # TypeScript configuration