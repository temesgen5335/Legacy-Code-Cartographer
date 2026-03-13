import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Layers, ChevronRight, Database, Search } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface Archive {
  name: string
  description: string
  sector: string
  artifact_count: number
  last_updated: string
}

export function LandingPage({ 
  onSelectProject, 
  onAnalyze 
}: { 
  onSelectProject: (name: string) => void,
  onAnalyze: (target: string) => void
}) {
  const [searchTerm, setSearchTerm] = useState('')
  const { data: archives, isLoading } = useQuery<Archive[]>({
    queryKey: ['archives'],
    queryFn: () => fetch('/api/discovery/archives').then(res => res.json())
  })

  const isIngestTarget = (val: string) => {
    return val.startsWith('http') || val.includes('/') || val.includes('\\') || val.startsWith('.')
  }

  const filteredArchives = archives?.filter(a => 
    a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const handleSearchCommit = () => {
    if (isIngestTarget(searchTerm)) {
      onAnalyze(searchTerm)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0f18] text-[#94a3b8] font-sans selection:bg-[#d4af35]/30 overflow-x-hidden relative">
      {/* Background Grid Accent */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20 pointer-events-none" />

      {/* Nav */}
      <nav className="h-24 border-b border-[#1e293b] flex items-center justify-between px-12 bg-[#0f172a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="bg-[#d4af35] p-2 rounded-sm shadow-[0_0_15px_rgba(212,175,53,0.3)]">
            <Layers className="w-6 h-6 text-[#0f172a]" />
          </div>
          <h1 className="text-xl font-black uppercase tracking-[0.3em] text-[#d4af35]">The Brownfield Cartographer</h1>
        </div>
        <div className="flex items-center gap-8">
          {['Archives', 'Intelligence', 'Methodology', 'Settings'].map(item => (
            <button key={item} className="text-[10px] font-black uppercase tracking-[0.2em] text-[#475569] hover:text-[#d4af35] transition-colors">
              {item}
            </button>
          ))}
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-12 py-24">
        {/* Hero */}
        <section className="text-center mb-32">
          <div className="inline-flex items-center gap-3 px-4 py-2 bg-[#d4af35]/5 border border-[#d4af35]/20 rounded-sm mb-8 animate-pulse">
             <div className="w-1.5 h-1.5 rounded-full bg-[#d4af35]" />
             <span className="text-[10px] font-bold text-[#d4af35] uppercase tracking-[0.3em]">Analysis Node Alpha-01 Online</span>
          </div>
          <h1 className="text-7xl font-black text-white tracking-tighter mb-8 leading-[0.9]">
            Map the Unknown.<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#d4af35] via-[#94a3b8] to-[#475569]">Navigate the Legacy.</span>
          </h1>
          <p className="max-w-2xl mx-auto text-lg text-[#475569] font-medium leading-relaxed uppercase tracking-wide">
            Automated Codebase Cartography & Structural Intelligence for Forward Deployed Engineers.
          </p>
        </section>

        {/* Search/Filter Bar */}
        <div className="mb-12 flex items-center justify-between border-b border-[#1e293b] pb-6">
          <div className="flex flex-col">
             <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">Codebase Archives</h2>
             <p className="text-[10px] font-bold text-[#475569] uppercase tracking-widest mt-1">
               {archives?.length === 0 ? "NO ARCHIVES DETECTED IN LOCAL REGISTRY" : `Reviewing ${archives?.length || 0} registered artifacts`}
             </p>
          </div>
          <div className="relative group w-[450px]">
            <Search className={cn(
              "absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors",
              isIngestTarget(searchTerm) ? "text-[#d4af35]" : "text-[#475569]"
            )} />
            <input 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchCommit()}
              placeholder={archives?.length === 0 ? "INPUT GITHUB URL OR LOCAL PATH TO ANALYZE..." : "INTERROGATE REGISTRY OR INPUT NEW TARGET..."} 
              className={cn(
                "w-full bg-[#0f172a] border rounded-sm py-3 pl-12 pr-32 text-[10px] font-black uppercase tracking-widest outline-none transition-all",
                isIngestTarget(searchTerm) ? "border-[#d4af35]/50 text-[#d4af35]" : "border-[#1e293b] text-[#94a3b8] focus:border-[#d4af35]/50"
              )}
            />
            {isIngestTarget(searchTerm) && (
              <button 
                onClick={handleSearchCommit}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-[#d4af35] text-[#0a0f18] text-[9px] font-black px-4 py-1.5 rounded-sm uppercase tracking-tighter hover:brightness-110 active:scale-95 transition-all"
              >
                Analyze Codebase
              </button>
            )}
          </div>
        </div>

        {/* Archives Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[1,2,3].map(i => <div key={i} className="h-64 bg-[#0f172a]/50 animate-pulse rounded-sm border border-[#1e293b]" />)}
          </div>
        ) : archives?.length === 0 ? (
          <div className="border border-dashed border-[#1e293b] rounded-sm p-32 text-center bg-[#0f172a]/20">
            <div className="bg-[#d4af35]/10 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8 border border-[#d4af35]/20">
               <Database className="w-10 h-10 text-[#d4af35] opacity-50" />
            </div>
            <h3 className="text-xl font-black text-white uppercase tracking-widest mb-4">Registry Empty</h3>
            <p className="max-w-md mx-auto text-sm text-[#475569] font-medium uppercase leading-relaxed mb-8">
              No architectural sectors have been mapped. Input a target path or repository above to initiate first-contact analysis.
            </p>
            <div className="flex justify-center gap-4">
               <div className="px-4 py-2 bg-[#0f172a] border border-[#1e293b] text-[9px] font-black uppercase text-[#475569]">
                 TARGET: NONE IDENTIFIED
               </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {filteredArchives.map((archive) => (
              <Card 
                key={archive.name} 
                className="bg-[#0f172a] border-[#1e293b] rounded-sm group hover:border-[#d4af35]/40 transition-all duration-500 overflow-hidden cursor-pointer shadow-xl"
                onClick={() => onSelectProject(archive.name)}
              >
                <CardHeader className="p-8 border-b border-[#1e293b]">
                  <div className="flex justify-between items-start mb-4">
                    <div className="bg-[#0a0f18] p-3 border border-[#1e293b] group-hover:border-[#d4af35]/30 group-hover:bg-[#d4af35]/5 transition-all">
                      <Database className="w-6 h-6 text-[#475569] group-hover:text-[#d4af35]" />
                    </div>
                    <Badge className="bg-[#d4af35]/5 text-[#d4af35] border-[#d4af35]/20 font-black text-[9px] px-3 py-1 rounded-none uppercase">
                      Sector 0{Math.floor(Math.random() * 9) + 1}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl font-black text-white group-hover:text-[#d4af35] transition-colors uppercase tracking-tighter">
                    {archive.name.replace('.git', '').replace('_', ' ')}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8 space-y-6">
                  <p className="text-xs text-[#475569] leading-relaxed font-bold uppercase tracking-tight line-clamp-2">
                    {archive.description}
                  </p>
                  <div className="flex items-center justify-between pt-4 border-t border-[#1e293b]/50">
                    <div className="flex gap-4">
                       <div className="flex flex-col">
                         <span className="text-[9px] font-black text-[#475569] uppercase tracking-widest">Artifacts</span>
                         <span className="text-xs font-mono text-[#94a3b8]">{archive.artifact_count}</span>
                       </div>
                       <div className="flex flex-col">
                         <span className="text-[9px] font-black text-[#475569] uppercase tracking-widest">Last Ingest</span>
                         <span className="text-xs font-mono text-[#94a3b8]">{archive.last_updated}</span>
                       </div>
                    </div>
                    <Button variant="ghost" size="sm" className="bg-[#0a0f18] border border-[#1e293b] rounded-sm group-hover:bg-[#d4af35] group-hover:text-[#0f172a] group-hover:border-[#d4af35] h-10 w-10 p-0 transition-all">
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      <footer className="h-32 border-t border-[#1e293b] bg-[#0f172a]/50 flex items-center justify-center relative overflow-hidden mt-24">
         <div className="text-center relative z-10">
           <p className="text-[10px] font-black text-[#475569] uppercase tracking-[0.4em]">Integrated Codebase Intelligence Terminal / Build 0.4.2</p>
         </div>
      </footer>
    </div>
  )
}

function Badge({ children, className }: any) {
  return (
    <div className={cn("inline-flex items-center border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-widest transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2", className)}>
      {children}
    </div>
  )
}
