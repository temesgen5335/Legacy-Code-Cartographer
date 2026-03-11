import { useState, useEffect, useRef } from 'react'
import type { ChangeEvent, KeyboardEvent } from 'react'
import { Send, Bot, User, Loader2, Sparkles, X } from 'lucide-react'
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
    { role: 'assistant', content: "I've indexed 'apache_airflow.git'. How can I help you navigate this codebase?" }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Connect to WebSocket backend
    const socket = new WebSocket(`ws://${window.location.host}/ws/chat/apache_airflow.git`)
    ws.current = socket

    socket.onmessage = (event) => {
      setMessages(prev => [...prev, { role: 'assistant', content: event.data }])
      setIsLoading(false)
    }

    return () => {
      socket.close()
    }
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = () => {
    if (!input.trim() || !ws.current) return
    
    const userMsg = input.trim()
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    ws.current.send(userMsg)
    setInput('')
    setIsLoading(true)
  }

  if (!isOpen) return null

  return (
    <div className="fixed top-0 right-0 h-full w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-300">
      <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
        <div className="flex items-center gap-2">
          <Sparkles className="text-blue-500 w-5 h-5" />
          <h3 className="font-bold">Cartographer AI</h3>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="text-slate-500 hover:text-slate-300">
          <X className="w-4 h-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="space-y-6">
          {messages.map((msg, i) => (
            <div key={i} className={cn(
              "flex gap-4",
              msg.role === 'user' ? "flex-row-reverse text-right" : ""
            )}>
              <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
                msg.role === 'user' ? "bg-blue-600" : "bg-slate-800 border border-slate-700"
              )}>
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-blue-400" />}
              </div>
              <div className={cn(
                "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                msg.role === 'user' ? "bg-blue-600/10 text-blue-100 rounded-tr-none" : "bg-slate-800/50 text-slate-300 rounded-tl-none border border-slate-800"
              )}>
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
              </div>
              <div className="bg-slate-800/50 rounded-2xl rounded-tl-none px-4 py-2.5 border border-slate-800">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce"></span>
                </span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="p-6 border-t border-slate-800 bg-slate-900/80 backdrop-blur-md">
        <div className="relative">
          <Input 
            value={input}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
            onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && sendMessage()}
            placeholder="Interrogate the codebase..." 
            className="bg-slate-950 border-slate-800 pr-12 h-12 rounded-xl focus-visible:ring-blue-600"
          />
          <Button 
            size="sm" 
            onClick={sendMessage}
            className="absolute right-1 top-1 bottom-1 bg-blue-600 hover:bg-blue-500 rounded-lg p-2 h-10 w-10"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-[10px] text-slate-500 mt-3 text-center italic">
          AI may hallucinate module purposes. Always verify critical paths.
        </p>
      </div>
    </div>
  )
}
