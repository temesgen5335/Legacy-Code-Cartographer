import { useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Share2, Waves } from 'lucide-react'
import { GraphViewer } from '@/components/navigator/GraphViewer'
import { DetailsPanel } from '@/components/navigator/DetailsPanel'

type ViewType = 'structure' | 'lineage'

export function NavigatorView() {
  const { projectId } = useParams({ from: '/codebase/$projectId' })
  const [activeView, setActiveView] = useState<ViewType>('structure')
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [isPanelOpen, setIsPanelOpen] = useState(false)

  const handleNodeSelect = (node: any) => {
    setSelectedNode(node)
    setIsPanelOpen(true)
  }

  const handleClosePanel = () => {
    setIsPanelOpen(false)
    setSelectedNode(null)
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header with Toggle Tabs */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#1e293b]">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">
            Spatial Navigator
          </h2>
          <p className="text-sm text-[#475569] font-medium uppercase tracking-wide">
            Interactive graph exploration with agent-powered intelligence
          </p>
        </div>

        <Tabs value={activeView} onValueChange={(v) => setActiveView(v as ViewType)}>
          <TabsList className="bg-[#0a0f18] border border-[#1e293b]">
            <TabsTrigger 
              value="structure" 
              className="data-[state=active]:bg-[#d4af35]/10 data-[state=active]:text-[#d4af35]"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Module View
            </TabsTrigger>
            <TabsTrigger 
              value="lineage" 
              className="data-[state=active]:bg-[#d4af35]/10 data-[state=active]:text-[#d4af35]"
            >
              <Waves className="w-4 h-4 mr-2" />
              Lineage View
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Graph Container with Details Panel */}
      <div className="flex-1 flex gap-6 min-h-0">
        {/* Main Graph Area */}
        <div className={`transition-all duration-300 ${isPanelOpen ? 'flex-1' : 'w-full'}`}>
          <Tabs value={activeView}>
            <TabsContent value="structure" className="h-full mt-0">
              <GraphViewer
                projectId={projectId || ''}
                viewType="structure"
                onNodeSelect={handleNodeSelect}
              />
            </TabsContent>
            
            <TabsContent value="lineage" className="h-full mt-0">
              <GraphViewer
                projectId={projectId || ''}
                viewType="lineage"
                onNodeSelect={handleNodeSelect}
              />
            </TabsContent>
          </Tabs>
        </div>

        {/* Details Panel */}
        {isPanelOpen && selectedNode && (
          <DetailsPanel
            node={selectedNode}
            projectId={projectId || ''}
            onClose={handleClosePanel}
          />
        )}
      </div>
    </div>
  )
}
