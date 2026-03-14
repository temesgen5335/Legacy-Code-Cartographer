import React, { useState, useMemo } from 'react'
import { useParams } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useVirtualizer } from '@tanstack/react-virtual'
import { Search, FileCode2, Command, Tag, Code2, Globe } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

const API_BASE = 'http://127.0.0.1:5001/api'

export function SemanticView() {
  const { projectId } = useParams({ from: '/sector/$projectId/semantic' })
  const [filter, setFilter] = useState('')
  const parentRef = React.useRef<HTMLDivElement>(null)

  const { data: modules = [] } = useQuery({
    queryKey: ['semantic', projectId],
    queryFn: async () => {
      const resp = await axios.get(`${API_BASE}/discovery/semantic/${projectId}`)
      return resp.data
    }
  })

  const filteredModules = useMemo(() => {
    return modules.filter((m: any) => 
      m.path.toLowerCase().includes(filter.toLowerCase()) || 
      m.purpose.toLowerCase().includes(filter.toLowerCase())
    )
  }, [modules, filter])

  const rowVirtualizer = useVirtualizer({
    count: filteredModules.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 140,
    overscan: 5,
  })

  return (
    <div className="h-full flex flex-col space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Semantic Index</h2>
          <p className="text-[11px] text-[#475569] uppercase font-bold tracking-widest mt-1">Interrogating business purposes via LLM synthesis</p>
        </div>
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#475569]" />
          <Input 
            placeholder="FILTER BY MODULE OR PURPOSE..." 
            className="pl-10 bg-[#0f172a] border-[#1e293b] text-white font-mono text-xs rounded-none h-12 focus-visible:ring-[#d4af35]/50 uppercase tracking-widest"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
      </div>

      <div 
        ref={parentRef}
        className="flex-1 overflow-auto border border-[#1e293b] bg-[#0f172a]/30 custom-scrollbar"
        style={{ height: 'calc(100vh - 300px)' }}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const module = filteredModules[virtualRow.index]
            return (
              <div
                key={virtualRow.index}
                className="absolute top-0 left-0 w-full p-4 border-b border-[#1e293b] hover:bg-[#d4af35]/5 transition-colors group cursor-pointer"
                style={{
                  height: `${virtualRow.size}px`,
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                <div className="flex items-start gap-6">
                  <div className="mt-1">
                    <div className="w-10 h-10 bg-[#0a0f18] border border-[#1e293b] flex items-center justify-center rounded-sm text-[#475569] group-hover:text-[#d4af35] group-hover:border-[#d4af35]/50 transition-all">
                      <FileCode2 className="w-5 h-5" />
                    </div>
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono font-bold text-white uppercase">{module.path}</span>
                        <Badge variant="outline" className="text-[9px] uppercase tracking-tighter font-black bg-[#0a0f18] text-[#475569] border-[#1e293b]">
                          {module.language}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                         <button className="flex items-center gap-1.5 text-[10px] font-black text-[#d4af35] uppercase tracking-widest">
                            <Command className="w-3 h-3" />
                            Structure
                         </button>
                         <button className="flex items-center gap-1.5 text-[10px] font-black text-[#d4af35] uppercase tracking-widest">
                            <Tag className="w-3 h-3" />
                            Lineage
                         </button>
                      </div>
                    </div>
                    <p className="text-sm text-[#94a3b8] font-medium leading-relaxed italic line-clamp-2">
                       {module.purpose}
                    </p>
                    <div className="flex items-center gap-4 pt-1">
                       <div className="flex items-center gap-1.5 text-[9px] font-black text-[#475569] uppercase">
                          <Code2 className="w-3 h-3" />
                          Complexity: {module.complexity.toFixed(2)}
                       </div>
                       <div className="flex items-center gap-1.5 text-[9px] font-black text-[#475569] uppercase">
                          <Globe className="w-3 h-3" />
                          Domain: Core Services
                       </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
