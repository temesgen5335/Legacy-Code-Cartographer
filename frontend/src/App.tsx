import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Shell } from './components/layout/Shell'
import { Dashboard } from './pages/Dashboard'
import { GraphView } from './pages/GraphView'

const queryClient = new QueryClient()

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <QueryClientProvider client={queryClient}>
      <Shell activeTab={activeTab} setActiveTab={setActiveTab}>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'graph' && <GraphView />}
      </Shell>
    </QueryClientProvider>
  )
}

export default App
