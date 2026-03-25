import React, { useState, useMemo } from 'react'
import { useParams } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useVirtualizer } from '@tanstack/react-virtual'
import { Search, FileCode2, Command, Tag, Code2, Globe, AlertTriangle } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

const API_BASE = 'http://127.0.0.1:5001/api'

export function SemanticView() {
  const { projectId } = useParams({ from: '/codebase/$projectId' })
  const [filter, setFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [domainFilter, setDomainFilter] = useState<string>('all')
  const [showDriftOnly, setShowDriftOnly] = useState(false)
  const parentRef = React.useRef<HTMLDivElement>(null)

  const { data: modules = [] } = useQuery({
    queryKey: ['semantic', projectId],
    queryFn: async () => {
      const resp = await axios.get(`${API_BASE}/discovery/semantic/${projectId}`)
      return resp.data
    }
  })

  // Categorize modules by file extension
  const categorizedModules = useMemo(() => {
    const categories: Record<string, any[]> = {}
    modules.forEach((m: any) => {
      const ext = m.path.split('.').pop()?.toLowerCase() || 'unknown'
      if (!categories[ext]) categories[ext] = []
      categories[ext].push(m)
    })
    return categories
  }, [modules])

  // Get unique domains
  const domains = useMemo(() => {
    const domainSet = new Set<string>()
    modules.forEach((m: any) => {
      if (m.domain_cluster) domainSet.add(m.domain_cluster)
    })
    return ['all', ...Array.from(domainSet).sort()]
  }, [modules])

  // Detect drift (modules with high complexity but low purpose clarity)
  const modulesWithDrift = useMemo(() => {
    return modules.filter((m: any) => {
      const hasDrift = m.complexity > 50 && (!m.purpose || m.purpose.length < 50)
      return hasDrift
    })
  }, [modules])

  const filteredModules = useMemo(() => {
    let filtered = modules

    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter((m: any) => {
        const ext = m.path.split('.').pop()?.toLowerCase()
        return ext === categoryFilter
      })
    }

    // Domain filter
    if (domainFilter !== 'all') {
      filtered = filtered.filter((m: any) => m.domain_cluster === domainFilter)
    }

    // Drift filter
    if (showDriftOnly) {
      const driftIds = new Set(modulesWithDrift.map((m: any) => m.id))
      filtered = filtered.filter((m: any) => driftIds.has(m.id))
    }

    // Text search
    if (filter) {
      filtered = filtered.filter((m: any) => 
        m.path.toLowerCase().includes(filter.toLowerCase()) || 
        (m.purpose && m.purpose.toLowerCase().includes(filter.toLowerCase()))
      )
    }

    return filtered
  }, [modules, filter, categoryFilter, domainFilter, showDriftOnly, modulesWithDrift])

  const rowVirtualizer = useVirtualizer({
    count: filteredModules.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 140,
    overscan: 5,
  })

  return (
    <div className="h-full flex flex-col space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Semantic Index</h2>
          <p className="text-[11px] text-[#475569] uppercase font-bold tracking-widest mt-1">
            LLM-derived purpose statements • {modules.length} modules • {modulesWithDrift.length} drift warnings
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#475569]" />
          <Input 
            placeholder="SEARCH BY MODULE NAME OR PURPOSE..." 
            className="pl-10 bg-[#0f172a] border-[#1e293b] text-white font-mono text-xs rounded-none h-10 focus-visible:ring-[#d4af35]/50"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        
        <select 
          value={categoryFilter} 
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="w-[180px] bg-[#0f172a] border border-[#1e293b] text-white h-10 rounded-none px-3 text-xs font-mono"
        >
          <option value="all">All Types</option>
          {Object.keys(categorizedModules).sort().map(ext => (
            <option key={ext} value={ext}>
              .{ext} ({categorizedModules[ext].length})
            </option>
          ))}
        </select>

        <select 
          value={domainFilter} 
          onChange={(e) => setDomainFilter(e.target.value)}
          className="w-[180px] bg-[#0f172a] border border-[#1e293b] text-white h-10 rounded-none px-3 text-xs font-mono"
        >
          {domains.map(domain => (
            <option key={domain} value={domain}>
              {domain === 'all' ? 'All Domains' : domain}
            </option>
          ))}
        </select>

        <button
          onClick={() => setShowDriftOnly(!showDriftOnly)}
          className={`px-4 h-10 border rounded-none font-black text-xs uppercase tracking-wide transition-all ${
            showDriftOnly 
              ? 'bg-amber-500/10 border-amber-500/40 text-amber-500' 
              : 'bg-[#0f172a] border-[#1e293b] text-[#475569] hover:border-[#d4af35]/40'
          }`}
        >
          <AlertTriangle className="w-4 h-4 mr-2 inline" />
          Drift Only
        </button>
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
                        {modulesWithDrift.some((m: any) => m.id === module.id) && (
                          <Badge className="text-[9px] uppercase tracking-tighter font-black bg-amber-500/10 text-amber-500 border-amber-500/20">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            Drift
                          </Badge>
                        )}
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
                       <div className={`flex items-center gap-1.5 text-[9px] font-black uppercase ${
                         module.complexity > 50 ? 'text-amber-500' : 'text-[#475569]'
                       }`}>
                          <Code2 className="w-3 h-3" />
                          Complexity: {module.complexity?.toFixed(2) || 'N/A'}
                       </div>
                       {module.domain_cluster && (
                         <div className="flex items-center gap-1.5 text-[9px] font-black text-[#475569] uppercase">
                            <Globe className="w-3 h-3" />
                            {module.domain_cluster}
                         </div>
                       )}
                       <div className="flex items-center gap-1.5 text-[9px] font-black text-[#475569] uppercase">
                          Purpose Length: {module.purpose?.length || 0} chars
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
