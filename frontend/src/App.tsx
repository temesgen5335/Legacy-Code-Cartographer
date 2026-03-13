import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Shell } from './components/layout/Shell'
import { Dashboard } from './pages/Dashboard'
import { GraphView } from './pages/GraphView'
import { LandingPage } from './pages/LandingPage'

const queryClient = new QueryClient()

import { AnalyzePage } from './pages/AnalyzePage'

function App() {
  const [view, setView] = useState<'landing' | 'project' | 'analyze'>('landing')
  const [activeProject, setActiveProject] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [ingestTarget, setIngestTarget] = useState<string | null>(null)

  const handleSelectProject = (name: string) => {
    setActiveProject(name)
    setView('project')
  }

  const handleStartAnalyze = (target: string) => {
    setIngestTarget(target)
    setView('analyze')
  }

  const handleBackToLanding = () => {
    setView('landing')
    setActiveProject(null)
    setIngestTarget(null)
  }

  return (
    <QueryClientProvider client={queryClient}>
      {view === 'landing' ? (
        <LandingPage onSelectProject={handleSelectProject} onAnalyze={handleStartAnalyze} />
      ) : view === 'analyze' ? (
        <AnalyzePage target={ingestTarget || ''} onComplete={handleSelectProject} onBack={handleBackToLanding} />
      ) : (
        <Shell 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          onBack={handleBackToLanding}
          projectName={activeProject || ''}
        >
          {activeTab === 'dashboard' && <Dashboard projectName={activeProject || ''} />}
          {activeTab === 'graph' && <GraphView projectName={activeProject || ''} />}
        </Shell>
      )}
    </QueryClientProvider>
  )
}

export default App
