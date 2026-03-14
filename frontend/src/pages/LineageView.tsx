import { useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Waves, Target, AlertCircle, ArrowRight, Table, Database, Cylinder } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const API_BASE = 'http://127.0.0.1:5001/api'

export function LineageView() {
  const { projectId } = useParams({ from: '/sector/$projectId/lineage' })
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const { data: lineageRoot } = useQuery({
    queryKey: ['lineage', projectId],
    queryFn: async () => {
      const resp = await axios.get(`${API_BASE}/discovery/lineage/${projectId}`)
      return resp.data
    }
  })

  const { data: nodeDetail } = useQuery({
    queryKey: ['lineage-detail', projectId, selectedNode],
    queryFn: async () => {
      if (!selectedNode) return null
      const resp = await axios.get(`${API_BASE}/discovery/lineage/${projectId}?node_id=${selectedNode}`)
      return resp.data
    },
    enabled: !!selectedNode
  })

  return (
    <div className="h-full space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Data Lineage</h2>
          <p className="text-[11px] text-[#475569] uppercase font-bold tracking-widest mt-1">Tracing the Flow of Water through structural pipes</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-300px)]">
        {/* Source/Sink Explorer */}
        <div className="bg-[#0f172a] border border-[#1e293b] flex flex-col">
          <div className="p-6 border-b border-[#1e293b] bg-[#1e293b]/20 flex items-center gap-3">
             <Database className="w-4 h-4 text-[#d4af35]" />
             <h3 className="text-xs font-black text-white uppercase tracking-widest">Entry & Exit Points</h3>
          </div>
          <div className="flex-1 overflow-auto p-4 space-y-8 custom-scrollbar">
            <section className="space-y-3">
              <p className="text-[10px] font-black text-[#475569] uppercase tracking-[0.2em] flex items-center gap-2">
                <Cylinder className="w-3 h-3" />
                Data Sources (Entry)
              </p>
              {lineageRoot?.sources?.map((s: string) => (
                <button 
                  key={s}
                  onClick={() => setSelectedNode(s)}
                  className={cn(
                    "w-full text-left p-3 border text-[11px] font-mono font-bold transition-all truncate grayscale hover:grayscale-0",
                    selectedNode === s ? "bg-[#d4af35]/10 border-[#d4af35] text-[#d4af35] grayscale-0" : "bg-[#0a0f18] border-[#1e293b] text-[#94a3b8]"
                  )}
                >
                  {s}
                </button>
              ))}
            </section>

            <section className="space-y-3">
              <p className="text-[10px] font-black text-[#475569] uppercase tracking-[0.2em] flex items-center gap-2">
                <ArrowRight className="w-3 h-3 rotate-45" />
                Data Sinks (Exit)
              </p>
              {lineageRoot?.sinks?.map((s: string) => (
                <button 
                  key={s}
                  onClick={() => setSelectedNode(s)}
                  className={cn(
                    "w-full text-left p-3 border text-[11px] font-mono font-bold transition-all truncate grayscale hover:grayscale-0",
                    selectedNode === s ? "bg-[#d4af35]/10 border-[#d4af35] text-[#d4af35] grayscale-0" : "bg-[#0a0f18] border-[#1e293b] text-[#94a3b8]"
                  )}
                >
                  {s}
                </button>
              ))}
            </section>
          </div>
        </div>

        {/* Lineage Focus Area */}
        <div className="lg:col-span-2 bg-[#0a0f18] border border-[#1e293b] relative overflow-hidden flex flex-col shadow-inner">
           {selectedNode ? (
             <div className="flex-1 flex flex-col p-10 animate-in fade-in zoom-in-95 duration-500">
                <div className="flex items-center gap-4 mb-10">
                   <div className="p-4 bg-[#d4af35]/10 border border-[#d4af35]/30 rounded-full shadow-[0_0_20px_rgba(212,175,53,0.1)]">
                      <Target className="w-8 h-8 text-[#d4af35]" />
                   </div>
                   <div>
                      <h4 className="text-sm font-black text-white uppercase tracking-widest">{selectedNode}</h4>
                      <Badge className="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 text-[9px] uppercase mt-1">Active Trace Target</Badge>
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-10">
                   <div className="space-y-6">
                      <div className="flex items-center gap-3">
                         <div className="h-4 w-1 bg-blue-500" />
                         <span className="text-[10px] font-black text-[#475569] uppercase tracking-widest">Upstream Lineage</span>
                      </div>
                      <div className="space-y-3">
                        {nodeDetail?.upstream?.length > 0 ? nodeDetail.upstream.map((n: string) => (
                           <div key={n} className="flex items-center gap-3 text-xs font-mono py-2 border-b border-[#1e293b] text-[#94a3b8]">
                              <Table className="w-3 h-3 text-blue-500 opacity-50" />
                              <span className="truncate">{n}</span>
                           </div>
                        )) : <p className="text-[10px] text-[#475569] italic font-bold">No upstream producers located.</p>}
                      </div>
                   </div>

                   <div className="space-y-6">
                      <div className="flex items-center gap-3">
                         <div className="h-4 w-1 bg-rose-500" />
                         <span className="text-[10px] font-black text-[#475569] uppercase tracking-widest">Blast Radius (Downstream)</span>
                      </div>
                       <div className="space-y-3">
                        {nodeDetail?.blastRadius?.length > 0 ? nodeDetail.blastRadius.map((n: string) => (
                           <div key={n} className="flex items-center gap-3 text-xs font-mono py-2 border-b border-[#1e293b] text-[#94a3b8] hover:text-rose-500 transition-colors">
                              <AlertCircle className="w-3 h-3 text-rose-500 opacity-50" />
                              <span className="truncate">{n}</span>
                           </div>
                        )) : <p className="text-[10px] text-[#475569] italic font-bold">No downstream consumers impacted.</p>}
                      </div>
                   </div>
                </div>
             </div>
           ) : (
             <div className="flex-1 flex flex-col items-center justify-center space-y-4 opacity-40 grayscale">
                <Waves className="w-16 h-16 text-[#475569] animate-pulse" />
                <p className="text-xs font-black text-[#475569] uppercase tracking-[0.4em]">Select a node to begin tracing</p>
             </div>
           )}

           {/* Grid Background Effect */}
           <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#d4af35 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
        </div>
      </div>
    </div>
  )
}
