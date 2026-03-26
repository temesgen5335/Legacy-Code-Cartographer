import { useParams } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'
import { 
  Zap, 
  ShieldCheck, 
  AlertTriangle, 
  Activity, 
  Cylinder,
  MoveUpRight,
  FileText,
  BookOpen,
  ScrollText,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import { CacheManager } from '@/utils/cacheManager'
import ReactMarkdown from 'react-markdown'

const API_BASE = 'http://127.0.0.1:5001/api'

export function CodebaseDashboard() {
  const { projectId } = useParams({ from: '/codebase/$projectId/overview' })
  const [selectedArtifact, setSelectedArtifact] = useState<'codebase' | 'brief' | 'day-one'>('codebase')

  const { data: metrics } = useQuery({
    queryKey: ['metrics', projectId],
    queryFn: async () => {
      const resp = await axios.get(`${API_BASE}/discovery/metrics/${projectId}`)
      return resp.data
    }
  })

  const { data: summary } = useQuery({
    queryKey: ['summary', projectId],
    queryFn: async () => {
      const cached = CacheManager.get(`summary_${projectId}`)
      if (cached) return cached
      
      const resp = await axios.get(`${API_BASE}/discovery/summary/${projectId}`)
      CacheManager.set(`summary_${projectId}`, resp.data)
      return resp.data
    }
  })

  // Fetch Archivist artifacts
  const { data: codebaseMd } = useQuery({
    queryKey: ['artifact', projectId, 'CODEBASE.md'],
    queryFn: async () => {
      // Cache busting to prevent loading old 404s
      const resp = await axios.get(`${API_BASE}/projects/${projectId}/artifacts/CODEBASE.md?t=${Date.now()}`)
      return resp.data
    },
    enabled: !!projectId
  })

  const { data: briefMd } = useQuery({
    queryKey: ['artifact', projectId, 'ONBOARDING_BRIEF.md'],
    queryFn: async () => {
      // Cache busting to prevent loading old 404s
      const resp = await axios.get(`${API_BASE}/projects/${projectId}/artifacts/ONBOARDING_BRIEF.md?t=${Date.now()}`)
      return resp.data
    },
    enabled: !!projectId
  })

  const { data: traceData } = useQuery({
    queryKey: ['trace', projectId],
    queryFn: async () => {
      // Cache busting to prevent loading old 404s
      const resp = await axios.get(`${API_BASE}/projects/${projectId}/artifacts/trace.json?t=${Date.now()}`)
      return resp.data
    },
    enabled: !!projectId
  })

  // Enhanced metric cards with proper agent data
  const metricCards = [
    { 
      label: 'Complexity (Surveyor)', 
      value: metrics?.systemComplexity ?? '---',
      subtitle: `Avg LOC: ${summary?.avg_loc ?? 'N/A'}`,
      icon: Zap, 
      color: 'text-amber-500', 
      bg: 'bg-amber-500/10' 
    },
    { 
      label: 'LLM Confidence (Semanticist)', 
      value: metrics ? `${(metrics.confidenceScore * 100).toFixed(1)}%` : '---',
      subtitle: 'Purpose generation',
      icon: ShieldCheck, 
      color: 'text-emerald-500', 
      bg: 'bg-emerald-500/10' 
    },
    { 
      label: 'Risk Index', 
      value: metrics?.riskIndex ?? '---',
      subtitle: `Dead code: ${summary?.dead_code_count ?? 0}`,
      icon: AlertTriangle, 
      color: 'text-rose-500', 
      bg: 'bg-rose-500/10' 
    },
    { 
      label: 'Primary Ingestion (Hydrologist)', 
      value: summary?.sources?.[0] ?? 'N/A',
      subtitle: `${summary?.sources?.length ?? 0} sources`,
      icon: Cylinder, 
      color: 'text-blue-500', 
      bg: 'bg-blue-500/10' 
    }
  ]

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Overview Head */}
      <div className="flex items-start justify-between border-b border-[#1e293b] pb-8">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-black text-white tracking-tighter mb-4 uppercase">
            Codebase Overview: <span className="text-[#d4af35]">{projectId}</span>
          </h1>
          <p className="text-lg text-[#94a3b8] leading-relaxed italic opacity-80">
            {summary?.summary || 'Initializing structural reconnaissance...'}
          </p>
        </div>
        <div className="hidden lg:flex items-center gap-2 px-6 py-3 bg-[#d4af35]/5 border border-[#d4af35]/20 rounded-sm">
          <Activity className="w-4 h-4 text-[#d4af35]" />
          <span className="text-[10px] font-black text-[#d4af35] uppercase tracking-widest">Live Analysis</span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((card, i) => (
          <Card key={i} className="bg-[#0f172a] border-[#1e293b] hover:border-[#d4af35]/30 transition-all group overflow-hidden relative">
            <CardHeader className="pb-2">
              <div className={cn("w-10 h-10 rounded-sm flex items-center justify-center mb-2", card.bg)}>
                <card.icon className={cn("w-5 h-5", card.color)} />
              </div>
              <p className="text-[10px] font-bold text-[#475569] uppercase tracking-widest">{card.label}</p>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-black text-white tracking-tighter truncate">
                {card.value}
              </div>
              <p className="text-[9px] text-[#475569] mt-1 uppercase tracking-wide">{card.subtitle}</p>
              <div className="mt-4 h-1 w-full bg-[#0a0f18] rounded-full overflow-hidden">
                <div 
                  className={cn("h-full rounded-full transition-all duration-1000", card.bg.replace('/10', ''))} 
                  style={{ width: metrics ? '70%' : '0%' }} 
                />
              </div>
            </CardContent>
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/1 rounded-full -mr-12 -mt-12 blur-3xl group-hover:bg-[#d4af35]/5 duration-500" />
          </Card>
        ))}
      </div>

      {/* Archivist Artifacts Viewer */}
      <Card className="bg-[#0f172a] border-[#1e293b]">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="h-6 w-1 bg-[#d4af35]" />
            <h3 className="text-sm font-black text-white uppercase tracking-[0.2em]">Documentation (Archivist)</h3>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedArtifact} onValueChange={(v) => setSelectedArtifact(v as any)}>
            <TabsList className="bg-[#0a0f18] border border-[#1e293b]">
              <TabsTrigger value="codebase" className="data-[state=active]:bg-[#d4af35]/10 data-[state=active]:text-[#d4af35]">
                <FileText className="w-4 h-4 mr-2" />
                CODEBASE.md
              </TabsTrigger>
              <TabsTrigger value="brief" className="data-[state=active]:bg-[#d4af35]/10 data-[state=active]:text-[#d4af35]">
                <BookOpen className="w-4 h-4 mr-2" />
                Onboarding Brief
              </TabsTrigger>
              <TabsTrigger value="day-one" className="data-[state=active]:bg-[#d4af35]/10 data-[state=active]:text-[#d4af35]">
                <ScrollText className="w-4 h-4 mr-2" />
                Day-One Brief
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="codebase" className="mt-4">
              <ScrollArea className="h-[500px] rounded-sm border border-[#1e293b] bg-[#0a0f18] p-6">
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown>{codebaseMd || 'Loading CODEBASE.md...'}</ReactMarkdown>
                </div>
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="brief" className="mt-4">
              <ScrollArea className="h-[500px] rounded-sm border border-[#1e293b] bg-[#0a0f18] p-6">
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown>{briefMd || 'Loading ONBOARDING_BRIEF.md...'}</ReactMarkdown>
                </div>
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="day-one" className="mt-4">
              <ScrollArea className="h-[500px] rounded-sm border border-[#1e293b] bg-[#0a0f18] p-6">
                <div className="space-y-4">
                  {summary?.day_one_questions ? (
                    Object.entries(summary.day_one_questions).map(([key, value]: [string, any], i) => (
                      <div key={i} className="p-4 border border-[#1e293b] rounded-sm">
                        <h4 className="text-sm font-bold text-[#d4af35] mb-2">{key.replace(/_/g, ' ').toUpperCase()}</h4>
                        <p className="text-sm text-[#94a3b8]">{value}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-[#475569] italic">Day-one brief not yet generated...</p>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Audit Feed from trace.json */}
        <div className="xl:col-span-2 space-y-6">
          <div className="flex items-center gap-3">
            <div className="h-6 w-1 bg-[#d4af35]" />
            <h3 className="text-sm font-black text-white uppercase tracking-[0.2em]">Audit Feed (Agent Operations)</h3>
          </div>
          
          <ScrollArea className="h-[400px] rounded-sm border border-[#1e293b] bg-[#0f172a] p-4">
            <div className="space-y-2">
              {traceData?.map((event: any, i: number) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-[#0a0f18] border border-[#1e293b]/50 rounded-sm hover:border-[#d4af35]/30 transition-colors">
                  <Clock className="w-4 h-4 text-[#475569] mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[9px] font-black text-[#d4af35] uppercase">{event.agent}</span>
                      <span className="text-[9px] text-[#475569]">•</span>
                      <span className="text-[9px] text-[#94a3b8]">{event.action}</span>
                    </div>
                    <p className="text-[10px] text-[#475569] font-mono truncate">
                      {JSON.stringify(event.evidence).slice(0, 100)}...
                    </p>
                  </div>
                  <span className={cn(
                    "text-[8px] font-bold uppercase px-2 py-1 rounded",
                    event.confidence === 'high' ? 'bg-emerald-500/10 text-emerald-500' :
                    event.confidence === 'medium' ? 'bg-amber-500/10 text-amber-500' :
                    'bg-rose-500/10 text-rose-500'
                  )}>
                    {event.confidence}
                  </span>
                </div>
              )) || <p className="text-sm text-[#475569] italic text-center py-10">No trace data available</p>}
            </div>
          </ScrollArea>
        </div>

        {/* Day-One Answers - Moved to sidebar */}
        <div className="space-y-6">
          <div className="flex items-center gap-3">
             <div className="h-6 w-1 bg-[#d4af35]" />
             <h3 className="text-sm font-black text-white uppercase tracking-[0.2em]">Five FDE Day-One Questions</h3>
          </div>
          
          <Accordion type="single" collapsible className="w-full space-y-4">
            {[
               { q: "What is the primary data ingestion path?", a: "The ingestion path centered around the source detected above." },
               { q: "What are the 3-5 most critical output endpoints?", a: "Identified via PageRank flow analysis." },
               { q: "What is the blast radius of a core failure?", a: "Average blast radius calculated at " + (summary?.health_score?.blast_radius_avg || "X") + " modules." },
               { q: "Where is business logic concentrated?", a: "Concentrated in the identified architectural hubs." },
               { q: "What has changed most in the last 90 days?", a: "Change velocity metrics are currently being indexed." }
            ].map((item, i) => (
              <AccordionItem key={i} value={`item-${i}`} className="border border-[#1e293b] bg-[#0f172a] rounded-sm px-6">
                <AccordionTrigger className="hover:no-underline py-5 text-left transition-all group">
                  <span className="text-[11px] font-bold text-[#94a3b8] group-hover:text-[#d4af35] uppercase tracking-widest">
                    {item.q}
                  </span>
                </AccordionTrigger>
                <AccordionContent className="text-sm text-[#475569] pb-6 font-medium italic">
                  {item.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        {/* Git Hubs / Activity */}
        <div className="space-y-6">
           <div className="flex items-center gap-3">
             <div className="h-6 w-1 bg-[#d4af35]" />
             <h3 className="text-sm font-black text-white uppercase tracking-[0.2em]">Architectural Hubs</h3>
          </div>
          
          <div className="space-y-3">
            {summary?.architectural_hubs?.slice(0, 5).map((hub: any, i: number) => (
              <div key={i} className="p-4 bg-[#0f172a] border border-[#1e293b] flex items-center justify-between group hover:bg-[#d4af35]/5 transition-all">
                <div className="flex flex-col">
                  <span className="text-[9px] font-black text-[#d4af35] uppercase mb-1 tracking-tighter">PR: {(hub.pagerank_score * 100).toFixed(1)}</span>
                  <span className="text-[11px] font-mono font-bold text-white truncate w-48">{hub.path}</span>
                </div>
                <MoveUpRight className="w-4 h-4 text-[#1e293b] group-hover:text-[#d4af35] transition-colors" />
              </div>
            )) || <div className="text-xs italic text-[#475569] p-10 text-center border border-dashed border-[#1e293b]">Scanning for gravity wells...</div>}
            
            <Button variant="ghost" className="w-full text-[10px] font-black uppercase text-[#475569] hover:text-[#d4af35] tracking-[0.3em]">
              View All Hubs
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
