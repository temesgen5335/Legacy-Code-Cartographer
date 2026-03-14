import { 
  createRootRoute, 
  createRoute, 
  createRouter,
  Outlet
} from '@tanstack/react-router'
import { LandingPage } from './pages/LandingPage'
import { AnalyzePage } from './pages/AnalyzePage'
import { SectorShell } from './components/layout/SectorShell'
import { SectorDashboard } from './pages/SectorDashboard'
import { StructureView } from './pages/StructureView'
import { LineageView } from './pages/LineageView'
import { SemanticView } from './pages/SemanticView'
import { ChatView } from './pages/ChatView'

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

// --- Sector Routes ---
const sectorShellRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/sector/$projectId',
  component: SectorShell,
})

const sectorOverviewRoute = createRoute({
  getParentRoute: () => sectorShellRoute,
  path: '/overview',
  component: SectorDashboard,
})

const sectorStructureRoute = createRoute({
  getParentRoute: () => sectorShellRoute,
  path: '/structure',
  component: StructureView,
})

const sectorLineageRoute = createRoute({
  getParentRoute: () => sectorShellRoute,
  path: '/lineage',
  component: LineageView,
})

const sectorSemanticRoute = createRoute({
  getParentRoute: () => sectorShellRoute,
  path: '/semantic',
  component: SemanticView,
})

const sectorChatRoute = createRoute({
  getParentRoute: () => sectorShellRoute,
  path: '/chat',
  component: ChatView,
})

// --- Route Tree ---
const routeTree = rootRoute.addChildren([
  indexRoute,
  analyzeRoute,
  sectorShellRoute.addChildren([
    sectorOverviewRoute,
    sectorStructureRoute,
    sectorLineageRoute,
    sectorSemanticRoute,
    sectorChatRoute,
  ]),
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
