import { useState } from 'react'
import { 
  LayoutDashboard, 
  Share2, 
  MessageSquare, 
  Layers, 
  Sparkles, 
  ChevronLeft,
  Waves,
  BookOpen,
  MoveUpRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ChatSidebar } from '@/components/chat/ChatSidebar'
import { Link, Outlet, useRouterState, useParams } from '@tanstack/react-router'

interface NavItem {
  id: string
  label: string
  subLabel: string
  icon: any
  to: string
}

export function SectorShell() {
  const { projectId } = useParams({ from: '/sector/$projectId' })
  const [isChatOpen, setIsChatOpen] = useState(false)
  const router = useRouterState()
  
  const navItems: NavItem[] = [
    { 
      id: 'overview', 
      label: 'Sector Overview', 
      subLabel: 'The Master Thinker', 
      icon: LayoutDashboard,
      to: `/sector/${projectId}/overview`
    },
    { 
      id: 'structure', 
      label: 'Structural Map', 
      subLabel: 'The Surveyor', 
      icon: Share2,
      to: `/sector/${projectId}/structure`
    },
    { 
      id: 'lineage', 
      label: 'Data Lineage', 
      subLabel: 'The Hydrologist', 
      icon: Waves,
      to: `/sector/${projectId}/lineage`
    },
    { 
      id: 'semantic', 
      label: 'Semantic Index', 
      subLabel: 'The Semanticist', 
      icon: BookOpen,
      to: `/sector/${projectId}/semantic`
    },
    { 
      id: 'chat', 
      label: 'Direct Intelligence', 
      subLabel: 'The Archivist', 
      icon: Sparkles,
      to: `/sector/${projectId}/chat`
    },
  ]

  const activeItem = navItems.find(item => router.location.pathname.includes(item.id)) || navItems[0]

  return (
    <div className="flex h-screen w-full bg-[#0a0f18] text-[#94a3b8] overflow-hidden font-sans border-4 border-[#1e293b]/20">
      {/* Sidebar */}
      <aside className="w-80 border-r border-[#1e293b] bg-[#0f172a] flex flex-col z-20 relative">
        <div className="p-8 border-b border-[#1e293b] bg-[#0f172a]/80 backdrop-blur-sm">
          <Link 
            to="/"
            className="mb-6 flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-[#475569] hover:text-[#d4af35] transition-colors group"
          >
            <ChevronLeft className="w-3 h-3 group-hover:-translate-x-1 transition-transform" />
            Sector Archive
          </Link>
          <h1 className="text-xl font-black tracking-tighter flex items-center gap-3 text-[#d4af35]">
            <Layers className="w-7 h-7" />
            <span className="uppercase tracking-widest">Cartographer</span>
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <div className="h-1 w-8 bg-[#d4af35]" />
            <p className="text-[9px] text-[#475569] uppercase font-bold tracking-[0.2em]">Nav Suite v2.0</p>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          {navItems.map((item) => (
            <Link
              key={item.id}
              to={item.to}
              className="flex flex-col gap-0.5 w-full px-5 py-4 rounded-sm transition-all duration-300 relative group border-l-2 border-transparent"
              activeProps={{
                className: "text-[#d4af35] bg-[#d4af35]/5 shadow-[inset_10px_0_15px_rgba(212,175,53,0.05)] border-l-2 border-[#d4af35]",
              }}
              inactiveProps={{
                className: "text-[#475569] hover:text-[#94a3b8] hover:bg-white/5",
              }}
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <item.icon className={cn("w-4 h-4", isActive ? "text-[#d4af35]" : "text-[#1e293b]")} />
                    <span className="text-[11px] font-black uppercase tracking-widest">{item.label}</span>
                  </div>
                  <span className="ml-7 text-[9px] font-bold opacity-40 uppercase tracking-tighter italic">{item.subLabel}</span>
                  
                  {isActive && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-[#d4af35] shadow-[0_0_8px_#d4af35]" />
                  )}
                </>
              )}
            </Link>
          ))}
        </nav>

        <div className="p-6 border-t border-[#1e293b]">
          <div className="bg-[#0a0f18] p-4 rounded-sm border border-[#1e293b] relative overflow-hidden group">
            <p className="text-[9px] text-[#475569] mb-2 uppercase tracking-tighter font-black">Active Registry</p>
            <p className="text-[12px] font-mono font-bold text-[#94a3b8] truncate relative z-10 uppercase tracking-widest">{projectId}</p>
            <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-[#d4af35]/5 rounded-full blur-xl group-hover:scale-150 transition-transform duration-700" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[#0a0f18]">
        <header className="h-24 border-b border-[#1e293b] flex items-center justify-between px-10 bg-[#0f172a]/90 backdrop-blur-2xl sticky top-0 z-10 shadow-lg">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-black text-[#475569] uppercase tracking-[0.3em]">Sector Intelligence</span>
              <MoveUpRight className="w-2.5 h-2.5 text-[#475569]" />
              <span className="text-[10px] font-black text-[#d4af35] uppercase tracking-[0.3em]">{activeItem.label}</span>
            </div>
            <p className="text-[11px] text-[#94a3b8] font-medium italic opacity-60">Synchronizing with node artifacts...</p>
          </div>
          <div className="flex items-center gap-6">
             <div className="flex items-center gap-6 pr-6 border-r border-[#1e293b]">
                <div className="flex flex-col items-end">
                  <span className="text-[8px] font-black text-[#475569] uppercase tracking-widest">Confidence</span>
                  <span className="text-xs font-mono font-bold text-emerald-500">92.4%</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[8px] font-black text-[#475569] uppercase tracking-widest">Risk Index</span>
                  <span className="text-xs font-mono font-bold text-amber-500">02</span>
                </div>
             </div>
            <Button 
              variant="outline" 
              size="sm" 
              className="bg-[#d4af35]/10 border-[#d4af35]/40 hover:bg-[#d4af35] hover:text-[#0f172a] text-[#d4af35] rounded-none text-[10px] font-bold uppercase tracking-widest px-6 h-10 transition-all duration-300 shadow-[0_0_15px_rgba(212,175,53,0.1)]"
              onClick={() => setIsChatOpen(!isChatOpen)}
            >
              <MessageSquare className="w-3.5 h-3.5 mr-2" />
              Interrogate
            </Button>
          </div>
        </header>
        
        <div className="flex-1 p-8 overflow-auto custom-scrollbar">
          <div className="max-w-[1600px] mx-auto w-full">
            <Outlet />
          </div>
        </div>
      </main>

      <ChatSidebar isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} projectName={projectId || ''} />
      
      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
          height: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.1);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #1e293b;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #d4af35;
        }
      `}} />
    </div>
  )
}
