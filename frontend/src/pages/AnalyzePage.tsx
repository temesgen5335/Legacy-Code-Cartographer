import { useState, useEffect, useRef } from 'react'
import { 
  Rocket, 
  Terminal, 
  ShieldCheck, 
  AlertCircle, 
  ChevronRight,
  Loader2,
  CheckCircle2,
  Database,
  Layers,
  Cpu,
  BrainCircuit,
  FileCode
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface IngestStatus {
  phase: 'INITIALIZING' | 'CLONING' | 'SURVEYOR' | 'HYDROLOGIST' | 'SEMANTICIST' | 'ARCHIVIST' | 'VISUALIZER' | 'COMPLETE' | 'ERROR'
  message: string
  progress: number
}

interface LogEntry {
  timestamp: string
  phase: string
  message: string
  type: 'info' | 'success' | 'error'
}

export function AnalyzePage({ 
  target, 
  onComplete, 
  onBack 
}: { 
  target: string, 
  onComplete: (name: string) => void,
  onBack: () => void 
}) {
  const [status, setStatus] = useState<IngestStatus>({
    phase: 'INITIALIZING',
    message: 'Awaiting system handshake...',
    progress: 0
  })
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isConfirmed, setIsConfirmed] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  const startAnalysis = () => {
    setIsConfirmed(true)
    const projectName = target.split('/').pop()?.replace('.git', '') || 'unknown_sector'
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/ingest/ws/${projectName}`
    
    ws.current = new WebSocket(wsUrl)
    
    ws.current.onopen = () => {
      ws.current?.send(JSON.stringify({ target }))
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.error) {
        setStatus(prev => ({ ...prev, phase: 'ERROR', message: data.error }))
        addLog('ERROR', data.error, 'error')
        return
      }

      setStatus(data)
      addLog(data.phase, data.message, data.phase === 'ERROR' ? 'error' : (data.phase === 'COMPLETE' ? 'success' : 'info'))
      
      if (data.phase === 'COMPLETE') {
        // Project name might have changed based on cloning, but let's assume it matches target
        // Production logic should probably return the final project_name in the COMPLETE message
      }
    }

    ws.current.onerror = () => {
      setStatus(prev => ({ ...prev, phase: 'ERROR', message: 'WebSocket connection failed' }))
      addLog('SYSTEM', 'Connection lost. Sector uplink unstable.', 'error')
    }
  }

  const addLog = (phase: string, message: string, type: 'info' | 'success' | 'error') => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      phase,
      message,
      type
    }])
  }

  const phaseIcons = {
    INITIALIZING: Cpu,
    CLONING: Database,
    SURVEYOR: Layers,
    HYDROLOGIST: BrainCircuit,
    SEMANTICIST: BrainCircuit,
    ARCHIVIST: FileCode,
    VISUALIZER: ShieldCheck,
    COMPLETE: CheckCircle2,
    ERROR: AlertCircle
  }

  const Icon = phaseIcons[status.phase] || Loader2

  return (
    <div className="min-h-screen bg-[#0a0f18] text-[#94a3b8] font-sans selection:bg-[#d4af35]/30 overflow-hidden relative">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20 pointer-events-none" />

      <main className="relative z-10 max-w-5xl mx-auto px-12 py-24 min-h-screen flex flex-col">
        {/* Header */}
        <div className="mb-16 flex items-center justify-between">
          <div className="flex flex-col">
            <h1 className="text-4xl font-black text-white uppercase tracking-tighter italic flex items-center gap-4">
              <Rocket className="w-8 h-8 text-[#d4af35]" />
              Analysis Initialization
            </h1>
            <p className="text-[10px] font-black text-[#475569] uppercase tracking-[0.4em] mt-2">
              Target Identification: <span className="text-[#94a3b8]">{target}</span>
            </p>
          </div>
          <Button variant="ghost" onClick={onBack} className="text-[10px] font-black uppercase tracking-widest text-[#475569] hover:text-[#d4af35]">
            Abort Mission
          </Button>
        </div>

        {!isConfirmed ? (
          <div className="flex-1 flex flex-col items-center justify-center animate-in fade-in zoom-in-95 duration-700">
            <Card className="bg-[#0f172a] border-[#1e293b] rounded-sm p-12 text-center max-w-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-[#d4af35]/20" />
              <div className="bg-[#d4af35]/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-8 border border-[#d4af35]/20">
                <ShieldCheck className="w-10 h-10 text-[#d4af35]" />
              </div>
              <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-4">Deep Reconnaissance Required</h2>
              <p className="text-sm text-[#475569] font-medium leading-relaxed mb-12 uppercase tracking-wide">
                You are about to initiate a multi-agent architectural excavation of the specified sector. 
                Full structural mapping, data lineage extraction, and semantic interrogation will be performed.
              </p>
              <Button 
                onClick={startAnalysis} 
                className="bg-[#d4af35] text-[#0a0f18] font-black uppercase tracking-[0.2em] px-12 h-16 text-xs hover:bg-[#d4af35] hover:brightness-110 shadow-[0_0_30px_rgba(212,175,53,0.3)] transition-all"
              >
                Execute Analysis <ChevronRight className="ml-2 w-4 h-4" />
              </Button>
            </Card>
          </div>
        ) : (
          <div className="flex-1 flex flex-col gap-12 animate-in fade-in duration-1000">
            {/* Progress Section */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                 <div className="flex items-center gap-4">
                    <div className={cn(
                      "p-3 rounded-sm border",
                      status.phase === 'ERROR' ? "bg-red-500/10 border-red-500/20" : "bg-[#d4af35]/10 border-[#d4af35]/20"
                    )}>
                      <Icon className={cn("w-6 h-6", status.phase === 'ERROR' ? "text-red-500" : "text-[#d4af35]", status.phase !== 'COMPLETE' && status.phase !== 'ERROR' && "animate-pulse")} />
                    </div>
                    <div>
                      <h3 className="text-xs font-black uppercase tracking-[0.2em] text-[#d4af35]">{status.phase} PHASE</h3>
                      <p className="text-sm text-white font-black tracking-tight mt-0.5 uppercase">{status.message}</p>
                    </div>
                 </div>
                 <div className="text-right">
                    <span className="text-3xl font-black text-[#d4af35] tracking-tighter italic">{status.progress}%</span>
                 </div>
              </div>
              <Progress value={status.progress} className="h-2 bg-[#0a0f18] border border-[#1e293b]" indicatorClassName="bg-[#d4af35] shadow-[0_0_15px_rgba(212,175,53,0.5)]" />
            </div>

            {/* Tactical Console */}
            <div className="flex-1 bg-[#0a0f18]/80 border border-[#1e293b] rounded-sm flex flex-col overflow-hidden shadow-2xl">
              <div className="h-10 border-b border-[#1e293b] flex items-center px-4 justify-between bg-[#0f172a]">
                <div className="flex items-center gap-2">
                  <Terminal className="w-3 h-3 text-[#475569]" />
                  <span className="text-[9px] font-black uppercase tracking-[0.2em] text-[#475569]">Analysis Console Node-Alpha</span>
                </div>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/20" />
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                </div>
              </div>
              <div ref={scrollRef} className="flex-1 p-6 font-mono text-[11px] overflow-y-auto space-y-2 selection:bg-[#d4af35]/20">
                {logs.map((log, i) => (
                  <div key={i} className="flex gap-4 group">
                    <span className="text-[#475569] whitespace-nowrap">[{log.timestamp}]</span>
                    <span className={cn(
                      "font-black uppercase tracking-widest whitespace-nowrap w-24",
                      log.type === 'error' ? "text-red-500" : (log.type === 'success' ? "text-emerald-500" : "text-[#d4af35]")
                    )}>
                      {log.phase}
                    </span>
                    <span className={cn(
                      log.type === 'error' ? "text-red-400" : "text-[#94a3b8]"
                    )}>
                      {log.message}
                    </span>
                  </div>
                ))}
                {status.phase !== 'COMPLETE' && status.phase !== 'ERROR' && (
                   <div className="flex gap-4 animate-pulse">
                     <span className="text-[#475569]">[{new Date().toLocaleTimeString()}]</span>
                     <span className="text-[#d4af35] w-24 font-black uppercase tracking-widest">{">>>"}</span>
                     <span className="text-[#475569]">Awaiting next artifact...</span>
                   </div>
                )}
              </div>
            </div>

            {/* Completion View */}
            {status.phase === 'COMPLETE' && (
              <div className="flex justify-center pt-8 animate-in slide-in-from-bottom-4 duration-500">
                <Button 
                  onClick={() => onComplete(target.split('/').pop()?.replace('.git', '') || '')}
                  className="bg-emerald-500 text-[#0a0f18] font-black uppercase tracking-[0.2em] px-12 h-16 text-xs hover:bg-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.3)] transition-all"
                >
                  Enter Sector Dashboard <ChevronRight className="ml-2 w-4 h-4" />
                </Button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
