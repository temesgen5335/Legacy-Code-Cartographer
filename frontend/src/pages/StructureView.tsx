import { useParams } from '@tanstack/react-router'

export function StructureView() {
  const { projectId } = useParams({ from: '/sector/$projectId/structure' })
  return (
    <div className="h-full space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Structural Map</h2>
          <p className="text-[11px] text-[#475569] uppercase font-bold tracking-widest mt-1">Projective topology of the codebase hierarchy</p>
        </div>
      </div>
      <div className="h-[calc(100vh-300px)] border border-[#1e293b] bg-[#0a0f18] relative overflow-hidden flex flex-col">
        <div className="bg-[#0f172a] border-b border-[#1e293b] p-3 flex justify-end">
          <a 
            href={`http://127.0.0.1:5001/api/discovery/graph/html/${projectId}`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-[10px] font-black text-[#d4af35] uppercase tracking-widest hover:underline"
          >
            Open in Full Screen ↗
          </a>
        </div>
        <iframe 
          src={`http://127.0.0.1:5001/api/discovery/graph/html/${projectId}`}
          className="w-full flex-1 border-none"
          title="Structural Map"
        />
      </div>
    </div>
  )
}
