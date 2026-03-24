import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { X, Target, TrendingUp, Search, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

const API_BASE = 'http://127.0.0.1:5001/api'

interface NavigatorToolsProps {
  projectId: string
  viewType: 'structure' | 'lineage'
  onBlastRadius: (nodePath: string) => void
  onTraceLineage: (nodePath: string) => void
  onClose: () => void
}

export function NavigatorTools({ 
  projectId, 
  viewType, 
  onBlastRadius, 
  onTraceLineage, 
  onClose 
}: NavigatorToolsProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [blastRadiusResult, setBlastRadiusResult] = useState<any>(null)
  const [lineageResult, setLineageResult] = useState<any>(null)

  const blastRadiusMutation = useMutation({
    mutationFn: async (nodePath: string) => {
      const resp = await axios.post(`${API_BASE}/navigator/blast_radius`, {
        project_id: projectId,
        node_path: nodePath
      })
      return resp.data
    },
    onSuccess: (data) => {
      setBlastRadiusResult(data)
      onBlastRadius(data.node_path)
    }
  })

  const traceLineageMutation = useMutation({
    mutationFn: async (nodePath: string) => {
      const resp = await axios.post(`${API_BASE}/navigator/trace_lineage`, {
        project_id: projectId,
        node_path: nodePath
      })
      return resp.data
    },
    onSuccess: (data) => {
      setLineageResult(data)
      onTraceLineage(data.node_path)
    }
  })

  const handleBlastRadius = () => {
    if (searchQuery.trim()) {
      blastRadiusMutation.mutate(searchQuery.trim())
    }
  }

  const handleTraceLineage = () => {
    if (searchQuery.trim()) {
      traceLineageMutation.mutate(searchQuery.trim())
    }
  }

  return (
    <Card className="absolute top-4 left-4 w-[400px] bg-[#0f172a] border-[#1e293b] z-20 animate-in slide-in-from-left duration-300">
      <CardHeader className="border-b border-[#1e293b] pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-black text-white uppercase tracking-wide">
              Navigator Tools
            </h3>
            <p className="text-xs text-[#475569] mt-1">
              Agent-powered graph analysis
            </p>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="hover:bg-[#1e293b]"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-4">
        {/* Search Input */}
        <div className="space-y-2">
          <label className="text-xs font-black text-[#475569] uppercase tracking-wide">
            Node Path or Name
          </label>
          <div className="flex gap-2">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., src/services/user.py"
              className="bg-[#0a0f18] border-[#1e293b] text-white placeholder:text-[#475569] focus-visible:border-[#d4af35]/50"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  if (viewType === 'structure') {
                    handleBlastRadius()
                  } else {
                    handleTraceLineage()
                  }
                }
              }}
            />
            <Button
              size="sm"
              variant="outline"
              className="bg-[#0a0f18] border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40"
            >
              <Search className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tool Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Button
            onClick={handleBlastRadius}
            disabled={!searchQuery.trim() || blastRadiusMutation.isPending}
            className="bg-[#d4af35]/10 border border-[#d4af35]/20 hover:bg-[#d4af35]/20 text-[#d4af35] font-black text-xs uppercase"
          >
            {blastRadiusMutation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Target className="w-4 h-4 mr-2" />
            )}
            Blast Radius
          </Button>
          <Button
            onClick={handleTraceLineage}
            disabled={!searchQuery.trim() || traceLineageMutation.isPending}
            className="bg-blue-500/10 border border-blue-500/20 hover:bg-blue-500/20 text-blue-500 font-black text-xs uppercase"
          >
            {traceLineageMutation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <TrendingUp className="w-4 h-4 mr-2" />
            )}
            Trace Lineage
          </Button>
        </div>

        {/* Blast Radius Results */}
        {blastRadiusResult && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-[#d4af35]" />
              <h4 className="text-xs font-black text-white uppercase tracking-wide">
                Blast Radius Results
              </h4>
            </div>
            <div className="bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#475569] uppercase">Downstream Dependencies</span>
                <Badge className="bg-[#d4af35]/10 text-[#d4af35] border-[#d4af35]/20">
                  {blastRadiusResult.downstream_count || 0}
                </Badge>
              </div>
              <ScrollArea className="h-[150px]">
                <div className="space-y-1">
                  {blastRadiusResult.downstream_nodes?.map((node: string, i: number) => (
                    <div key={i} className="text-xs font-mono text-[#94a3b8] p-2 bg-[#0f172a] rounded">
                      {node}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>
        )}

        {/* Lineage Results */}
        {lineageResult && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <h4 className="text-xs font-black text-white uppercase tracking-wide">
                Lineage Trace Results
              </h4>
            </div>
            <div className="bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#475569] uppercase">Upstream Path</span>
                <Badge className="bg-blue-500/10 text-blue-500 border-blue-500/20">
                  {lineageResult.path_length || 0} hops
                </Badge>
              </div>
              <ScrollArea className="h-[150px]">
                <div className="space-y-2">
                  {lineageResult.upstream_path?.map((node: string, i: number) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                        <span className="text-[9px] font-black text-blue-500">{i + 1}</span>
                      </div>
                      <div className="text-xs font-mono text-[#94a3b8] p-2 bg-[#0f172a] rounded flex-1">
                        {node}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-[#d4af35]/5 border border-[#d4af35]/20 p-3 rounded">
          <p className="text-[10px] text-[#d4af35] font-medium leading-relaxed">
            <strong>Blast Radius:</strong> Highlights all downstream dependencies in orange/red.<br/>
            <strong>Trace Lineage:</strong> Shows upstream path to primary source in blue/cyan.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
