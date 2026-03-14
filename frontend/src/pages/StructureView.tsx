import { useParams } from '@tanstack/react-router'
import { GraphView as RawGraphView } from './GraphView'

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
      <div className="h-[calc(100vh-300px)] border border-[#1e293b] bg-[#0a0f18] relative overflow-hidden">
        <RawGraphView projectName={projectId} />
      </div>
    </div>
  )
}
