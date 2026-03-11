import React, { useState } from 'react'
import { LayoutDashboard, Share2, MessageSquare, Layers, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ChatSidebar } from '@/components/chat/ChatSidebar'

interface ShellProps {
  children: React.ReactNode
  activeTab: string
  setActiveTab: (tab: string) => void
}

export function Shell({ children, activeTab, setActiveTab }: ShellProps) {
  const [isChatOpen, setIsChatOpen] = useState(false)

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'graph', label: 'Data Lineage', icon: Share2 },
  ]

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-50 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col z-20">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Layers className="text-blue-500 w-6 h-6" />
            <span>Cartographer</span>
          </h1>
          <p className="text-[10px] text-slate-500 mt-1 uppercase tracking-widest font-bold">DeepWiki Intelligence</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                "flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                activeTab === item.id 
                  ? "bg-blue-600/10 text-blue-400 border border-blue-600/30 shadow-[0_0_15px_rgba(37,99,235,0.1)]" 
                  : "text-slate-500 hover:bg-slate-800/50 hover:text-slate-300"
              )}
            >
              <item.icon className={cn("w-4 h-4", activeTab === item.id ? "text-blue-500" : "text-slate-600")} />
              {item.label}
            </button>
          ))}

          <div className="pt-4 mt-4 border-t border-slate-800/50">
             <button
              onClick={() => setIsChatOpen(true)}
              className={cn(
                "flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium transition-all group hover:bg-slate-800/50",
                isChatOpen ? "text-blue-400" : "text-slate-500"
              )}
            >
              <Sparkles className="w-4 h-4 text-purple-500 group-hover:scale-110 transition-transform" />
              Intelligence Chat
            </button>
          </div>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800 shadow-inner">
            <p className="text-[10px] text-slate-600 mb-1 uppercase tracking-tighter font-bold">Project Snapshot</p>
            <p className="text-xs font-mono text-slate-400 truncate">apache_airflow.git</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-auto bg-[radial-gradient(circle_at_top_right,rgba(30,41,59,0.3),transparent)]">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/40 backdrop-blur-xl sticky top-0 z-10">
          <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">
            {navItems.find(i => i.id === activeTab)?.label}
          </h2>
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              size="sm" 
              className="bg-slate-900 border-slate-800 hover:bg-slate-800 text-slate-300 rounded-lg text-xs h-8"
              onClick={() => setIsChatOpen(!isChatOpen)}
            >
              <MessageSquare className="w-3 h-3 mr-2" />
              Interrogate
            </Button>
          </div>
        </header>
        
        <div className="flex-1 p-8">
          {children}
        </div>
      </main>

      <ChatSidebar isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  )
}
