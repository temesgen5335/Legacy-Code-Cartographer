import { useState, useEffect, useRef } from 'react'
import type { ChangeEvent, KeyboardEvent } from 'react'
import { X, Send, Bot, Ghost } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export function ChatSidebar({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Archival intelligence online. Specify sector for interrogation.' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Connect to WebSocket backend
    ws.current = new WebSocket(`ws://${window.location.host}/api/chat`)
    ws.current.onmessage = (event) => {
      setMessages(prev => [...prev, { role: 'assistant', content: event.data }])
      setIsLoading(false)
    }
    return () => ws.current?.close()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    if (!input.trim() || !ws.current) return;
    
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    ws.current.send(userMsg);
    setInput('');
    setIsLoading(true);
  };

  return (
    <div className={cn(
      "fixed inset-y-0 right-0 w-[420px] bg-[#0f172a] border-l border-[#1e293b] shadow-2xl z-50 transform transition-transform duration-500 ease-out flex flex-col",
      isOpen ? "translate-x-0" : "translate-x-full"
    )}>
      {/* Header */}
      <div className="p-8 border-b border-[#1e293b] flex items-center justify-between bg-[#0a0f18]/80 backdrop-blur-md relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#d4af35]/50 to-transparent" />
        <div className="flex items-center gap-4">
          <div className="bg-[#d4af35]/10 p-2.5 rounded-sm border border-[#d4af35]/20">
            <Bot className="w-5 h-5 text-[#d4af35]" />
          </div>
          <div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-[#d4af35]">Intelligence Terminal</h3>
            <p className="text-[9px] text-[#475569] font-black uppercase tracking-widest mt-0.5">RAG Analysis Active</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="text-[#475569] hover:text-[#d4af35] transition-all hover:bg-white/5 rounded-none">
          <X className="w-5 h-5" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-8">
        <div className="space-y-8">
          {messages.map((m, idx) => (
            <div key={idx} className={cn(
              "flex flex-col max-w-[90%]",
              m.role === 'user' ? "ml-auto items-end" : "items-start"
            )}>
              <div className={cn(
                "p-5 rounded-sm text-[11px] leading-relaxed font-bold transition-all shadow-xl group border relative",
                m.role === 'user' 
                  ? "bg-[#d4af35] text-[#0f172a] border-[#d4af35] uppercase tracking-wider" 
                  : "bg-[#0a0f18] text-[#94a3b8] border-[#1e293b]"
              )}>
                {m.content}
                {m.role === 'assistant' && (
                   <div className="mt-4 pt-4 border-t border-[#1e293b]/50 text-[9px] text-[#475569] flex items-center gap-2 uppercase font-black tracking-tighter">
                     <Ghost className="w-3 h-3 text-[#d4af35]" /> Artifact Trace Identified
                   </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-center gap-4 text-[#d4af35] animate-pulse pl-2">
              <div className="w-2 h-2 bg-[#d4af35] rounded-full shadow-[0_0_8px_#d4af35]" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em]">Synthesizing Context...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-8 border-t border-[#1e293b] bg-[#0a0f18]/90 backdrop-blur-md">
        <div className="relative group">
          <Input 
            value={input}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
            onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && sendMessage()}
            placeholder="INTERROGATE CODEBASE..." 
            className="bg-[#0f172a] border-[#1e293b] text-[#94a3b8] pr-14 h-16 rounded-none focus-visible:ring-0 focus-visible:border-[#d4af35]/50 placeholder:text-[#1e293b] placeholder:text-[10px] placeholder:font-black placeholder:tracking-[0.3em] transition-all font-mono text-xs"
          />
          <Button 
            size="sm" 
            onClick={sendMessage}
            disabled={!input.trim()}
            className="absolute right-2 top-2 bottom-2 bg-[#d4af35] hover:bg-[#d4af35] hover:brightness-110 text-[#0f172a] rounded-none p-2 w-12 h-12 transition-all disabled:opacity-10 disabled:grayscale"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <div className="flex justify-between items-center mt-4">
          <p className="text-[9px] text-[#475569] font-black uppercase tracking-[0.2em] opacity-40">
             Archival Protocol v4.2.1
          </p>
          <div className="flex gap-1.5">
            <div className="w-1 h-1 bg-[#d4af35]/20 rounded-full" />
            <div className="w-1 h-1 bg-[#d4af35]/40 rounded-full" />
            <div className="w-1 h-1 bg-[#d4af35]/60 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  )
}
