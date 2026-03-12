import { 
  ShieldAlert, 
  Zap, 
  Activity, 
  Clock, 
  Layers, 
  ChevronRight,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

import { useQuery } from '@tanstack/react-query'

export function Dashboard({ projectName }: { projectName: string }) {
  const { data: report, isLoading, error } = useQuery({
    queryKey: ['summary', projectName],
    queryFn: () => fetch(`/api/discovery/summary/${projectName}`).then(res => {
      if (!res.ok) throw new Error('Analysis not found')
      return res.json()
    })
  })

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
      <div className="w-12 h-12 border-4 border-[#d4af35]/20 border-t-[#d4af35] rounded-full animate-spin" />
      <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#475569]">Synthesizing Archival Knowledge...</p>
    </div>
  )

  if (error || !report) return (
    <div className="bg-red-500/10 border border-red-500/50 p-8 rounded-sm text-center">
      <p className="text-red-500 font-bold uppercase tracking-widest text-sm">Failed to retrieve sector intelligence</p>
      <p className="text-red-400/60 text-xs mt-2 font-mono">Ensure "{projectName}" analysis exists in the registry.</p>
    </div>
  )

  return (
    <div className="space-y-6 animate-in fade-in duration-700">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Maintainability" value={`${report.health_score.maintainability}%`} icon={Activity} color="text-[#d4af35]" />
        <StatCard title="Blast Radius" value={`${report.health_score.blast_radius_avg}%`} icon={ShieldAlert} color="text-red-500" />
        <StatCard title="Cycles" value={report.health_score.circular_dependencies_count} icon={Layers} color="text-amber-600" />
        <StatCard title="Last Analysis" value={report.last_updated} icon={Clock} color="text-slate-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Summary */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="bg-[#0f172a] border-[#1e293b] rounded-sm shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-[#d4af35]" />
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-[#475569] flex items-center gap-2">
                <Zap className="text-[#d4af35] w-3 h-3" /> Intelligence Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#94a3b8] leading-relaxed text-sm font-medium tracking-tight">
                {report.summary}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-[#0f172a] border-[#1e293b] rounded-sm shadow-xl overflow-hidden">
            <CardHeader className="border-b border-[#1e293b] bg-[#0a0f18]/50 py-4">
              <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-[#475569]">Architectural Hubs</CardTitle>
            </CardHeader>
            <Table>
              <TableHeader className="bg-[#0a0f18]">
                <TableRow className="hover:bg-transparent border-[#1e293b]">
                  <TableHead className="text-[10px] uppercase font-bold text-[#475569] py-3">Path</TableHead>
                  <TableHead className="text-[10px] uppercase font-bold text-[#475569]">Ingress</TableHead>
                  <TableHead className="text-[10px] uppercase font-bold text-[#475569]">Significance</TableHead>
                  <TableHead className="text-right"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.architectural_hubs.map((hub: any) => (
                  <TableRow key={hub.node_id} className="border-[#1e293b] hover:bg-white/[0.02] transition-colors group">
                    <TableCell className="py-4">
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-[11px] text-[#94a3b8]">{hub.path}</span>
                        <span className="text-[10px] text-[#475569] font-medium italic">{hub.purpose}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-[#d4af35]/5 text-[#d4af35] border-[#d4af35]/20 font-bold text-[9px] rounded-none px-2 py-0">
                        {hub.fan_in} DEPENDENTS
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-[10px] text-[#475569]">{(hub.pagerank_score * 100).toFixed(2)}%</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" className="h-7 w-7 p-0 hover:bg-[#d4af35]/10 hover:text-[#d4af35]">
                        <ChevronRight className="w-3 h-3" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>

        {/* Risk Sidebar ... remains the same but uses dynamic data ... */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 px-1">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#475569]">Structural Integrity Risks</h3>
            <div className="h-[1px] flex-1 bg-[#1e293b]" />
          </div>
          
          {report.risk_cards.map((risk: any, idx: number) => (
            <Card key={idx} className={cn(
              "bg-[#0f172a] border-[#1e293b] rounded-sm shadow-lg group hover:border-[#d4af35]/30 transition-colors",
              risk.severity === 'high' ? "border-l-2 border-l-red-500" : "border-l-2 border-l-[#d4af35]"
            )}>
              <CardHeader className="pb-2 pt-4">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-xs font-black uppercase tracking-wider text-[#94a3b8] group-hover:text-[#d4af35] transition-colors">{risk.title}</CardTitle>
                  {risk.severity === 'high' ? <AlertTriangle className="text-red-500 w-3 h-3" /> : <ShieldAlert className="text-[#d4af35] w-3 h-3" />}
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pb-4">
                <p className="text-[11px] text-[#475569] leading-relaxed font-medium">{risk.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  {risk.impact_nodes.map((node: string) => (
                    <code key={node} className="text-[9px] px-1.5 py-0.5 bg-[#0a0f18] text-[#94a3b8] border border-[#1e293b] font-mono">{node}</code>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}

          <Card className="bg-[#d4af35]/5 border border-[#d4af35]/20 rounded-sm relative overflow-hidden group">
            <CardContent className="p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="bg-[#d4af35] p-1.5 rounded-sm">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#0f172a]" />
                </div>
                <h3 className="text-[10px] font-black uppercase tracking-widest text-[#d4af35]">Verdict</h3>
              </div>
              <p className="text-[11px] text-[#94a3b8] leading-relaxed font-medium">
                {report.data_lineage_summary}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }: any) {
  return (
    <Card className="bg-[#0f172a] border-[#1e293b] rounded-sm hover:border-[#d4af35]/50 transition-all duration-300 relative group overflow-hidden shadow-xl">
      <div className="absolute top-0 right-0 p-2 opacity-5 group-hover:opacity-10 transition-opacity">
        <Icon className="w-12 h-12" />
      </div>
      <CardContent className="p-5 flex items-center justify-between relative z-10">
        <div>
          <p className="text-[9px] font-black text-[#475569] uppercase tracking-[0.2em] mb-1">{title}</p>
          <p className="text-xl font-black tracking-tighter text-[#94a3b8] group-hover:text-[#d4af35] transition-colors">{value}</p>
        </div>
        <div className={cn("p-2 rounded-sm bg-[#0a0f18] border border-[#1e293b] group-hover:scale-105 transition-transform", color)}>
          <Icon className="w-4 h-4" />
        </div>
      </CardContent>
    </Card>
  )
}
