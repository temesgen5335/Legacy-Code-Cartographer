import { useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { Search, Database, Cylinder, ArrowRight } from 'lucide-react'

const API_BASE = 'http://127.0.0.1:5001/api'

export function LineageView() {
  const { projectId } = useParams({ from: '/sector/$projectId/lineage' })
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const { data: lineageRoot } = useQuery({
    queryKey: ['lineage', projectId],
    queryFn: async () => {
      const resp = await axios.get(`${API_BASE}/discovery/lineage/${projectId}`)
      return resp.data
    }
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
          <div className="p-6 border-b border-[#1e293b] bg-[#1e293b]/20 flex flex-col gap-4">
             <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-[#d4af35]" />
                <h3 className="text-xs font-black text-white uppercase tracking-widest">Entry & Exit Points</h3>
             </div>
             <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-[#475569]" />
                <Input 
                  placeholder="Filter nodes..." 
                  className="bg-[#0a0f18] border-[#1e293b] h-8 text-[10px] pl-8 rounded-none font-bold text-[#94a3b8]"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
             </div>
          </div>
          <div className="flex-1 overflow-auto p-4 space-y-8 custom-scrollbar">
            <section className="space-y-3">
              <p className="text-[10px] font-black text-[#475569] uppercase tracking-[0.2em] flex items-center gap-2">
                <Cylinder className="w-3 h-3" />
                Data Sources (Entry)
              </p>
              {lineageRoot?.sources?.filter((s: string) => s.toLowerCase().includes(searchQuery.toLowerCase())).map((s: string) => (
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
              {lineageRoot?.sinks?.filter((s: string) => s.toLowerCase().includes(searchQuery.toLowerCase())).map((s: string) => (
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
           <div className="bg-[#0f172a] border-b border-[#1e293b] p-3 flex justify-end">
              <a 
                href={`http://127.0.0.1:5001/api/discovery/lineage/html/${projectId}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-[10px] font-black text-[#d4af35] uppercase tracking-widest hover:underline"
              >
                Open in Full Screen ↗
              </a>
           </div>
           <iframe 
              src={`http://127.0.0.1:5001/api/discovery/lineage/html/${projectId}`}
              className="w-full flex-1 border-none"
              title="Data Lineage"
           />
           
           {/* Grid Background Effect */}
           <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#d4af35 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
        </div>
      </div>
    </div>
  )
}
