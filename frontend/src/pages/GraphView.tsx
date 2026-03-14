import { useState, useCallback, useEffect } from 'react';
import { Share2 } from 'lucide-react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
} from 'reactflow';
import type { Node, Edge, Connection } from 'reactflow';
import 'reactflow/dist/style.css';

import { useQuery } from '@tanstack/react-query';
import { Input } from '@/components/ui/input';
import { Search, X } from 'lucide-react';

export function GraphView({ projectName }: { projectName: string }) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: graphData, isLoading } = useQuery({
    queryKey: ['graph', projectName],
    queryFn: () => fetch(`/api/discovery/graph/${projectName}`).then(res => res.json()),
  });

  useEffect(() => {
    if (graphData) {
      setNodes(graphData.nodes);
      setEdges(graphData.edges);
    }
  }, [graphData]);

  useEffect(() => {
    if (!searchQuery) {
      setNodes(prev => prev.map(n => ({ ...n, style: { ...n.style, opacity: 1 } })));
      return;
    }

    const query = searchQuery.toLowerCase();
    const matches = nodes.filter(n => 
      n.id.toLowerCase().includes(query) || 
      (n.data?.label || '').toLowerCase().includes(query)
    ).map(n => n.id);

    setNodes(prev => prev.map(n => ({
      ...n,
      style: {
        ...n.style,
        opacity: matches.length === 0 || matches.includes(n.id) ? 1 : 0.2,
        border: matches.includes(n.id) ? '2px solid #d4af35' : n.style?.border,
        boxShadow: matches.includes(n.id) ? '0 0 15px rgba(212,175,53,0.5)' : n.style?.boxShadow
      }
    })));
  }, [searchQuery]);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), []);

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
      <div className="w-12 h-12 border-4 border-[#d4af35]/20 border-t-[#d4af35] rounded-full animate-spin" />
      <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#475569]">Mapping Sector Topology...</p>
    </div>
  )

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
            Visualizing <span className="text-[#94a3b8]">{nodes.length} active artifacts</span> across the ingestion pipeline. Node size represents PageRank significance.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative group w-64">
           <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#475569] group-focus-within:text-[#d4af35] transition-colors" />
           <Input 
             placeholder="Search nodes..." 
             className="bg-[#0f172a]/90 border-[#1e293b] focus:border-[#d4af35]/50 text-[11px] pl-9 h-10 rounded-sm font-bold tracking-tight text-[#94a3b8] placeholder:text-[#475569] placeholder:font-black placeholder:uppercase"
             value={searchQuery}
             onChange={(e) => setSearchQuery(e.target.value)}
           />
           {searchQuery && (
             <button 
               onClick={() => setSearchQuery('')}
               className="absolute right-3 top-1/2 -translate-y-1/2 text-[#475569] hover:text-[#d4af35]"
             >
               <X className="w-3 h-3" />
             </button>
           )}
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
