import { 
  createRootRoute, 
  createRoute, 
  createRouter,
  Outlet
} from '@tanstack/react-router'
import { LandingPage } from './pages/LandingPage'
import { AnalyzePage } from './pages/AnalyzePage'
import { CodebaseShell } from './components/layout/CodebaseShell'
import { CodebaseDashboard } from './pages/CodebaseDashboard'
import { NavigatorView } from './pages/NavigatorView'
import { SemanticView } from './pages/SemanticView'
import { ChatView } from './pages/ChatView'
import DocView from './pages/DocView'

// --- Root ---
const rootRoute = createRootRoute({
  component: () => <Outlet />,
})

// --- Standard Routes ---
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: LandingPage,
})

const analyzeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/analyze',
  component: AnalyzePage,
})

// --- Codebase Routes ---
const codebaseShellRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/codebase/$projectId',
  component: CodebaseShell,
})

const codebaseOverviewRoute = createRoute({
  getParentRoute: () => codebaseShellRoute,
  path: '/overview',
  component: CodebaseDashboard,
})

const codebaseNavigatorRoute = createRoute({
  getParentRoute: () => codebaseShellRoute,
  path: '/navigator',
  component: NavigatorView,
})

const codebaseSemanticRoute = createRoute({
  getParentRoute: () => codebaseShellRoute,
  path: '/semantic',
  component: SemanticView,
})

const codebaseChatRoute = createRoute({
  getParentRoute: () => codebaseShellRoute,
  path: '/chat',
  component: ChatView,
})

const codebaseLedgerRoute = createRoute({
  getParentRoute: () => codebaseShellRoute,
  path: '/docs/ledger',
  component: () => <DocView type="ledger" />,
})

const codebaseBriefRoute = createRoute({
  getParentRoute: () => codebaseShellRoute,
  path: '/docs/brief',
  component: () => <DocView type="brief" />,
})

// --- Route Tree ---
const routeTree = rootRoute.addChildren([
  indexRoute,
  analyzeRoute,
  codebaseShellRoute.addChildren([
    codebaseOverviewRoute,
    codebaseNavigatorRoute,
    codebaseSemanticRoute,
    codebaseChatRoute,
    codebaseLedgerRoute,
    codebaseBriefRoute,
  ]),
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
