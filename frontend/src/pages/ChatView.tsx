import { useParams } from '@tanstack/react-router'
import { ChatSidebar } from '@/components/chat/ChatSidebar'

export function ChatView() {
  const { projectId } = useParams({ from: '/codebase/$projectId' })
  return (
    <div className="h-full space-y-8 animate-in fade-in duration-500">
       <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Direct Intelligence</h2>
          <p className="text-[11px] text-[#475569] uppercase font-bold tracking-widest mt-1">Interrogating the Archivist via RAG-powered context</p>
        </div>
      </div>
      <div className="h-[calc(100vh-320px)] border border-[#1e293b] bg-[#0f172a] rounded-sm relative overflow-hidden flex flex-col shadow-2xl">
         {/* We'll use a slightly different version of ChatSidebar that's more 'embedded' */}
         <div className="flex-1 flex flex-col">
            <ChatSidebar isOpen={true} onClose={() => {}} projectName={projectId} isEmbedded={true} />
         </div>
      </div>
    </div>
  )
}
