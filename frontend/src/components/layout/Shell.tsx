import React, { useState } from 'react'
import { LayoutDashboard, Share2, MessageSquare, Layers, Sparkles, ChevronLeft } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ChatSidebar } from '@/components/chat/ChatSidebar'

interface ShellProps {
  children: React.ReactNode
  activeTab: string
  setActiveTab: (tab: string) => void
  onBack: () => void
  projectName: string
}

export function Shell({ children, activeTab, setActiveTab, onBack, projectName }: ShellProps) {
  const [isChatOpen, setIsChatOpen] = useState(false)

  const navItems = [
    { id: 'dashboard', label: 'Archival Summary', icon: LayoutDashboard },
    { id: 'graph', label: 'Structural Map', icon: Share2 },
  ]

  return (
    <div className="flex h-screen w-full bg-[#0a0f18] text-[#94a3b8] overflow-hidden font-sans border-4 border-[#1e293b]/20">
      {/* Sidebar */}
      <aside className="w-72 border-r border-[#1e293b] bg-[#0f172a] flex flex-col z-20 relative">
        <div className="p-8 border-b border-[#1e293b] bg-[#0f172a]/80 backdrop-blur-sm">
          <button 
            onClick={onBack}
            className="mb-6 flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-[#475569] hover:text-[#d4af35] transition-colors group"
          >
            <ChevronLeft className="w-3 h-3 group-hover:-translate-x-1 transition-transform" />
            Sector Archive
          </button>
          <h1 className="text-xl font-black tracking-tighter flex items-center gap-3 text-[#d4af35]">
            <Layers className="w-7 h-7" />
            <span className="uppercase">Cartographer</span>
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <div className="h-1 w-8 bg-[#d4af35]" />
            <p className="text-[9px] text-[#475569] uppercase font-bold tracking-[0.2em]">Archival Unit 01</p>
          </div>
        </div>
        
        <nav className="flex-1 p-6 space-y-2">
          {/* ... existing navItems map ... */}
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                "flex items-center gap-3 w-full px-5 py-3.5 rounded-sm text-xs font-bold uppercase tracking-widest transition-all duration-300 relative group",
                activeTab === item.id 
                  ? "text-[#d4af35] border-l-2 border-[#d4af35] bg-[#d4af35]/5 shadow-[inset_10px_0_15px_rgba(212,175,53,0.05)]" 
                  : "text-[#475569] hover:text-[#94a3b8] hover:bg-white/5"
              )}
            >
              <item.icon className={cn("w-4 h-4", activeTab === item.id ? "text-[#d4af35]" : "text-[#1e293b]")} />
              {item.label}
              {activeTab === item.id && (
                <div className="absolute right-4 w-1.5 h-1.5 rounded-full bg-[#d4af35] shadow-[0_0_8px_#d4af35]" />
              )}
            </button>
          ))}

          <div className="pt-6 mt-6 border-t border-[#1e293b]/50">
             <button
              onClick={() => setIsChatOpen(true)}
              className={cn(
                "flex items-center gap-3 w-full px-5 py-3.5 rounded-sm text-xs font-bold uppercase tracking-widest transition-all group hover:bg-white/5",
                isChatOpen ? "text-[#d4af35]" : "text-[#475569]"
              )}
            >
              <Sparkles className="w-4 h-4 text-[#d4af35] group-hover:animate-pulse" />
              Direct Intelligence
            </button>
          </div>
        </nav>

        <div className="p-6 border-t border-[#1e293b]">
          <div className="bg-[#0a0f18] p-4 rounded-sm border border-[#1e293b] relative overflow-hidden group">
            <p className="text-[9px] text-[#475569] mb-2 uppercase tracking-tighter font-black">Target Registry</p>
            <p className="text-[11px] font-mono text-[#94a3b8] truncate relative z-10">{projectName}</p>
            <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-[#d4af35]/5 rounded-full blur-xl group-hover:scale-150 transition-transform duration-700" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-auto bg-[#0a0f18]">
        <header className="h-20 border-b border-[#1e293b] flex items-center justify-between px-10 bg-[#0f172a]/90 backdrop-blur-2xl sticky top-0 z-10 shadow-lg">
          <div className="flex flex-col">
            <h2 className="text-[10px] font-black text-[#475569] uppercase tracking-[0.3em] mb-1">
              Sector / {navItems.find(i => i.id === activeTab)?.label}
            </h2>
            <p className="text-[11px] text-[#94a3b8] font-medium italic opacity-60">Synthesizing codebase topography...</p>
          </div>
          <div className="flex items-center gap-6">
             <div className="flex items-center gap-3 px-4 py-2 bg-[#0a0f18] border border-[#1e293b] rounded-sm">
               <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
               <span className="text-[10px] font-bold text-[#475569] uppercase tracking-widest">System Online</span>
             </div>
            <Button 
              variant="outline" 
              size="sm" 
              className="bg-[#d4af35]/10 border-[#d4af35]/40 hover:bg-[#d4af35] hover:text-[#0f172a] text-[#d4af35] rounded-sm text-[10px] font-bold uppercase tracking-widest px-6 h-9 transition-all duration-300 shadow-[0_0_15px_rgba(212,175,53,0.1)]"
              onClick={() => setIsChatOpen(!isChatOpen)}
            >
              <MessageSquare className="w-3.5 h-3.5 mr-2" />
              Interrogate
            </Button>
          </div>
        </header>
        
        <div className="flex-1 p-10 max-w-[1600px] mx-auto w-full">
          {children}
        </div>
      </main>

      <ChatSidebar isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} projectName={projectName} />
    </div>
  )
}
