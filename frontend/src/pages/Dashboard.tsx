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
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const mockReport = {
  project_name: "apache_airflow.git",
  summary: "A massive, mature data orchestration platform built on a Directed Acyclic Graph (DAG) architecture. The codebase is highly modular, with clear separation between core execution and provider-level integrations.",
  health_score: {
    maintainability: 82.5,
    blast_radius_avg: 14.8,
    circular_dependencies_count: 0
  },
  risk_cards: [
    {
      title: "Provider Sprawl",
      severity: "medium",
      description: "Over 70% of the codebase is contained in provider packages, leading to potential dependency hell and testing overhead.",
      impact_nodes: ["airflow/providers/*"]
    },
    {
      title: "Complex State Machine",
      severity: "high",
      description: "The TaskInstance state transitions are managed across multiple core modules, creating a high-risk bottleneck for scheduler performance.",
      impact_nodes: ["airflow/models/taskinstance.py", "airflow/jobs/scheduler_job.py"]
    }
  ],
  architectural_hubs: [
    { node_id: "mod:airflow/models/dag.py", path: "airflow/models/dag.py", pagerank_score: 0.045, fan_out: 124, fan_in: 890, purpose: "Core DAG model and lifecycle management." },
    { node_id: "mod:airflow/models/taskinstance.py", path: "airflow/models/taskinstance.py", pagerank_score: 0.042, fan_out: 89, fan_in: 1205, purpose: "Execution state and metadata for individual tasks." },
    { node_id: "mod:airflow/settings.py", path: "airflow/settings.py", pagerank_score: 0.038, fan_out: 15, fan_in: 5402, purpose: "Global configuration and environment initialization." }
  ],
  last_updated: "2026-03-10"
}

export function Dashboard() {
  // In a real app, query the API
  // const { data: report, isLoading } = useQuery(['report', 'apache_airflow.git'], () => fetch('/api/discovery/summary/apache_airflow.git').then(res => res.json()))
  const report = mockReport

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Maintainability" value={`${report.health_score.maintainability}%`} icon={Activity} color="text-green-500" />
        <StatCard title="Blast Radius" value={`${report.health_score.blast_radius_avg}%`} icon={ShieldAlert} color="text-amber-500" />
        <StatCard title="Cycles" value={report.health_score.circular_dependencies_count} icon={Layers} color="text-blue-500" />
        <StatCard title="Last Analyzed" value={report.last_updated} icon={Clock} color="text-slate-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Summary */}
        <div className="lg:col-span-2 space-y-8">
          <Card className="bg-slate-900 border-slate-800 shadow-2xl">
            <CardHeader>
              <CardTitle className="text-xl font-bold flex items-center gap-2">
                <Zap className="text-yellow-500 w-5 h-5" /> Codebase Intel
              </CardTitle>
              <CardDescription className="text-slate-400">Executive executive summary and architectural assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300 leading-relaxed text-lg italic serif">
                "{report.summary}"
              </p>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800 shadow-xl overflow-hidden">
            <CardHeader className="border-b border-slate-800 bg-slate-900/50">
              <CardTitle>Architectural Hubs</CardTitle>
              <CardDescription>Most critical modules by PageRank and Dependency Ingress</CardDescription>
            </CardHeader>
            <Table>
              <TableHeader className="bg-slate-950/50">
                <TableRow className="hover:bg-transparent border-slate-800">
                  <TableHead className="w-[300px]">Module Path</TableHead>
                  <TableHead>Fan-In</TableHead>
                  <TableHead>PageRank</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.architectural_hubs.map((hub) => (
                  <TableRow key={hub.node_id} className="border-slate-800 hover:bg-slate-800/50 transition-colors">
                    <TableCell className="font-mono text-sm py-4">
                      {hub.path}
                      <p className="text-xs text-slate-500 mt-1 font-sans">{hub.purpose}</p>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-blue-600/10 text-blue-400 border-blue-600/30">
                        {hub.fan_in} dependents
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-slate-400">{(hub.pagerank_score * 100).toFixed(2)}%</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" className="hover:bg-blue-600/20 hover:text-blue-400">
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>

        {/* Risk Sidebar */}
        <div className="space-y-6">
          <h3 className="text-sm font-semibold uppercase tracking-widest text-slate-500 px-1">Architectural Risks</h3>
          {report.risk_cards.map((risk, idx) => (
            <Card key={idx} className={cn(
              "bg-slate-900 border-l-4 shadow-lg",
              risk.severity === 'high' ? "border-l-red-500 border-slate-800" : "border-l-amber-500 border-slate-800"
            )}>
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-base font-bold">{risk.title}</CardTitle>
                  {risk.severity === 'high' ? <AlertTriangle className="text-red-500 w-4 h-4" /> : <ShieldAlert className="text-amber-500 w-4 h-4" />}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-slate-400 leading-normal">{risk.description}</p>
                <div className="space-y-2">
                  <p className="text-[10px] uppercase font-bold text-slate-600 tracking-tighter">Impact Radius</p>
                  <div className="flex flex-wrap gap-2">
                    {risk.impact_nodes.map(node => (
                      <code key={node} className="text-[10px] px-2 py-0.5 bg-slate-800 rounded text-slate-300 border border-slate-700">{node}</code>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          <Card className="bg-blue-600/10 border-blue-600/20 shadow-xl overflow-hidden relative">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-blue-600 p-2 rounded-lg">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold">Cartographer Verdict</h3>
              </div>
              <p className="text-sm text-blue-100/80 leading-relaxed">
                Primary data flow follows an acyclic multi-stage pipeline. Recommendations: Decouple provider settings from core models.
              </p>
              <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 rotate-45 translate-x-12 -translate-y-12 blur-2xl rounded-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }: any) {
  return (
    <Card className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-all border-b-2 hover:border-b-blue-600 group">
      <CardContent className="p-6 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 group-hover:text-slate-400 transition-colors">{title}</p>
          <p className="text-2xl font-bold tracking-tight">{value}</p>
        </div>
        <div className={cn("p-2 rounded-lg bg-slate-950/50 border border-slate-800 group-hover:scale-110 transition-transform", color)}>
          <Icon className="w-6 h-6" />
        </div>
      </CardContent>
    </Card>
  )
}
