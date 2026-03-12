import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Shell } from './components/layout/Shell'
import { Dashboard } from './pages/Dashboard'
import { GraphView } from './pages/GraphView'
import { LandingPage } from './pages/LandingPage'

const queryClient = new QueryClient()

function App() {
  const [view, setView] = useState<'landing' | 'project'>('landing')
  const [activeProject, setActiveProject] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('dashboard')

  const handleSelectProject = (name: string) => {
    setActiveProject(name)
    setView('project')
  }

  const handleBackToLanding = () => {
    setView('landing')
    setActiveProject(null)
  }

  return (
    <QueryClientProvider client={queryClient}>
      {view === 'landing' ? (
        <LandingPage onSelectProject={handleSelectProject} />
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
