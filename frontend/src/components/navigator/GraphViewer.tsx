import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Loader2, ZoomIn, ZoomOut, Maximize2, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { NavigatorTools } from './NavigatorTools'

const API_BASE = 'http://127.0.0.1:5001/api'

interface GraphViewerProps {
  projectId: string
  viewType: 'structure' | 'lineage'
  onNodeSelect: (node: any) => void
}

export function GraphViewer({ projectId, viewType, onNodeSelect }: GraphViewerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [isToolsOpen, setIsToolsOpen] = useState(false)
  const [graphLoaded, setGraphLoaded] = useState(false)

  const { data: graphUrl, isLoading } = useQuery({
    queryKey: ['graph', projectId, viewType],
    queryFn: async () => {
      const endpoint = viewType === 'structure' 
        ? `/discovery/graph/html/${projectId}`
        : `/discovery/lineage/html/${projectId}`
      
      const resp = await axios.get(`${API_BASE}${endpoint}`)
      return resp.data.url || `${API_BASE}${endpoint}`
    },
    enabled: !!projectId
  })

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'nodeClick') {
        onNodeSelect(event.data.node)
      }
      if (event.data.type === 'graphLoaded') {
        setGraphLoaded(true)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [onNodeSelect])

  const handleZoomIn = () => {
    iframeRef.current?.contentWindow?.postMessage({ action: 'zoomIn' }, '*')
  }

  const handleZoomOut = () => {
    iframeRef.current?.contentWindow?.postMessage({ action: 'zoomOut' }, '*')
  }

  const handleFitView = () => {
    iframeRef.current?.contentWindow?.postMessage({ action: 'fitView' }, '*')
  }

  const handleBlastRadius = (nodePath: string) => {
    iframeRef.current?.contentWindow?.postMessage({ 
      action: 'blastRadius', 
      nodePath 
    }, '*')
  }

  const handleTraceLineage = (nodePath: string) => {
    iframeRef.current?.contentWindow?.postMessage({ 
      action: 'traceLineage', 
      nodePath 
    }, '*')
  }

  if (isLoading) {
    return (
      <Card className="h-full bg-[#0f172a] border-[#1e293b] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-[#d4af35] animate-spin" />
          <p className="text-sm text-[#475569] font-medium uppercase tracking-wide">
            Loading {viewType === 'structure' ? 'Module' : 'Lineage'} Graph...
          </p>
        </div>
      </Card>
    )
  }

  return (
    <div className="relative h-full">
      {/* Graph Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <Button
          size="sm"
          variant="outline"
          className="bg-[#0f172a] border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40"
          onClick={handleZoomIn}
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="bg-[#0f172a] border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40"
          onClick={handleZoomOut}
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="bg-[#0f172a] border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40"
          onClick={handleFitView}
        >
          <Maximize2 className="w-4 h-4" />
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="bg-[#0f172a] border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40"
          onClick={() => setIsToolsOpen(!isToolsOpen)}
        >
          <Filter className="w-4 h-4" />
        </Button>
      </div>

      {/* Navigator Tools Panel */}
      {isToolsOpen && (
        <NavigatorTools
          projectId={projectId}
          viewType={viewType}
          onBlastRadius={handleBlastRadius}
          onTraceLineage={handleTraceLineage}
          onClose={() => setIsToolsOpen(false)}
        />
      )}

      {/* Graph iframe */}
      <Card className="h-full bg-[#0f172a] border-[#1e293b] overflow-hidden">
        {graphUrl ? (
          <iframe
            ref={iframeRef}
            src={graphUrl}
            className="w-full h-full border-0"
            title={`${viewType} graph`}
            onLoad={() => setGraphLoaded(true)}
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-sm text-[#475569] font-medium uppercase tracking-wide mb-2">
                No graph data available
              </p>
              <p className="text-xs text-[#475569]/60">
                Run analysis to generate {viewType} graph
              </p>
            </div>
          </div>
        )}
      </Card>

      {/* Loading Overlay */}
      {!graphLoaded && graphUrl && (
        <div className="absolute inset-0 bg-[#0a0f18]/80 backdrop-blur-sm flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-8 h-8 text-[#d4af35] animate-spin" />
            <p className="text-sm text-[#475569] font-medium uppercase tracking-wide">
              Rendering graph...
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
