import { useState, useCallback } from 'react';
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
    <div className="h-[calc(100vh-12rem)] w-full bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden relative shadow-2xl">
      <div className="absolute top-4 left-4 z-10 space-y-2">
        <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 backdrop-blur-md">
          <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Graph Legend</h3>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-xs">
              <div className="w-3 h-3 rounded bg-blue-500" /> <span>Module / Logic</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <div className="w-3 h-3 rounded bg-red-500" /> <span>Dataset / Sink</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <div className="w-3 h-3 rounded bg-purple-500" /> <span>Transformation</span>
            </div>
          </div>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onConnect={onConnect}
        fitView
        className="bg-slate-900"
      >
        <Background color="#1e293b" gap={20} />
        <Controls showInteractive={false} className="bg-slate-800 border-slate-700 fill-slate-200" />
        <MiniMap 
          nodeColor={(n: any) => n.data.type === 'dataset' ? '#ef4444' : '#3b82f6'} 
          maskColor="rgba(15, 23, 42, 0.8)"
          className="bg-slate-950 border border-slate-800 rounded-lg"
        />
      </ReactFlow>
      
      <div className="absolute bottom-4 right-4 z-10">
        <p className="text-[10px] text-slate-500 italic">Structural Graph optimized via PageRank and In-Degree Centricity</p>
      </div>
    </div>
  );
}
