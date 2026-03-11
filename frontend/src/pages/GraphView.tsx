import { useState, useCallback } from 'react';
import { Share2 } from 'lucide-react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from 'reactflow';
import type { Node, Edge, Connection } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes = [
  {
    id: 'mod:airflow/models/dag.py',
    position: { x: 250, y: 5 },
    data: { label: 'dag.py', type: 'module' },
    style: { background: '#1e293b', color: '#fff', border: '1px solid #3b82f6', borderRadius: '8px', padding: '10px' }
  },
  { 
    id: 'mod:airflow/models/taskinstance.py', 
    position: { x: 100, y: 150 }, 
    data: { label: 'taskinstance.py', type: 'module' },
    style: { background: '#1e293b', color: '#fff', border: '1px solid #3b82f6', borderRadius: '8px', padding: '10px' }
  },
  { 
    id: 'ds:postgres_db', 
    position: { x: 400, y: 150 }, 
    data: { label: 'Postgres DB', type: 'dataset' },
    style: { background: '#450a0a', color: '#fff', border: '1px solid #ef4444', borderRadius: '8px', padding: '10px' }
  },
];

const initialEdges = [
  { id: 'e1-2', source: 'mod:airflow/models/dag.py', target: 'mod:airflow/models/taskinstance.py', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-3', source: 'mod:airflow/models/taskinstance.py', target: 'ds:postgres_db', label: 'writes', markerEnd: { type: MarkerType.ArrowClosed } },
];

export function GraphView() {
  const [nodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), []);

  return (
    <div className="h-[calc(100vh-12rem)] w-full bg-[#0a0f18] rounded-sm border border-[#1e293b] overflow-hidden relative shadow-2xl animate-in zoom-in-95 duration-500">
      {/* Legend / Overlay */}
      <div className="absolute top-6 left-6 z-10 space-y-4">
        <div className="bg-[#0f172a]/95 backdrop-blur-md p-5 border border-[#1e293b] rounded-sm shadow-xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#d4af35] mb-3 flex items-center gap-2">
            <Share2 className="w-3 h-3" /> Topology Key
          </h3>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-[#d4af35] shadow-[0_0_8px_#d4af35]" />
              <span className="text-[10px] uppercase font-bold text-[#94a3b8]">Architectural Hub</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              <span className="text-[10px] uppercase font-bold text-[#475569]">Stable Module</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
              <span className="text-[10px] uppercase font-bold text-[#475569]">High Volatility</span>
            </div>
          </div>
        </div>

        <div className="bg-[#0f172a]/80 backdrop-blur-sm p-4 border border-[#1e293b] rounded-sm max-w-[240px]">
          <p className="text-[10px] text-[#475569] leading-relaxed font-medium">
            Visualizing <span className="text-[#94a3b8]">14 active artifacts</span> across the ingestion pipeline. Node size represents PageRank significance.
          </p>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onConnect={onConnect}
        fitView
        className="bg-[#0a0f18]"
      >
        <Background color="#1e293b" gap={24} size={1} />
        <Controls className="bg-[#0f172a] border-[#1e293b] fill-[#94a3b8]" />
        <MiniMap 
          className="bg-[#0f172a] border border-[#1e293b] rounded-sm" 
          maskColor="rgba(10, 15, 24, 0.7)"
          nodeColor={(node) => node.data.isHub ? '#d4af35' : '#1e293b'}
        />
      </ReactFlow>

      {/* Floating Info */}
      <div className="absolute bottom-6 left-6 z-10 bg-[#0f172a]/95 backdrop-blur-md px-4 py-2 border border-[#d4af35]/20 rounded-sm">
        <span className="text-[9px] font-black uppercase tracking-[0.2em] text-[#d4af35]">Graph Projection: Active</span>
      </div>
    </div>
  );
}
