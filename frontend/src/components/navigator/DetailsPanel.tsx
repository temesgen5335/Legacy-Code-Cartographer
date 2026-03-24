import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { X, Code, GitBranch, FileText, Database, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

const API_BASE = 'http://127.0.0.1:5001/api'

interface DetailsPanelProps {
  node: any
  projectId: string
  onClose: () => void
}

export function DetailsPanel({ node, projectId, onClose }: DetailsPanelProps) {
  const { data: nodeDetails } = useQuery({
    queryKey: ['nodeDetails', projectId, node.id],
    queryFn: async () => {
      const resp = await axios.get(`${API_BASE}/discovery/node/${projectId}/${node.id}`)
      return resp.data
    },
    enabled: !!node.id
  })

  const getNodeIcon = () => {
    switch (node.node_type) {
      case 'module':
        return <Code className="w-5 h-5" />
      case 'dataset':
        return <Database className="w-5 h-5" />
      case 'transformation':
        return <Zap className="w-5 h-5" />
      case 'function':
        return <FileText className="w-5 h-5" />
      default:
        return <Code className="w-5 h-5" />
    }
  }

  const getLanguage = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'py':
        return 'python'
      case 'js':
      case 'jsx':
        return 'javascript'
      case 'ts':
      case 'tsx':
        return 'typescript'
      case 'sql':
        return 'sql'
      case 'yml':
      case 'yaml':
        return 'yaml'
      case 'json':
        return 'json'
      default:
        return 'text'
    }
  }

  return (
    <Card className="w-[500px] h-full bg-[#0f172a] border-[#1e293b] flex flex-col animate-in slide-in-from-right duration-300">
      {/* Header */}
      <CardHeader className="border-b border-[#1e293b] pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="bg-[#d4af35]/10 p-2 rounded border border-[#d4af35]/20 flex-shrink-0">
              {getNodeIcon()}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-black text-white uppercase tracking-wide truncate">
                {node.label || node.id}
              </h3>
              <p className="text-xs text-[#475569] font-mono mt-1 truncate">
                {node.path || node.id}
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="flex-shrink-0 hover:bg-[#1e293b]"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Node Type Badge */}
        <div className="flex gap-2 mt-3">
          <Badge 
            variant="outline" 
            className="bg-[#d4af35]/5 text-[#d4af35] border-[#d4af35]/20 font-black text-[9px] uppercase"
          >
            {node.node_type || 'module'}
          </Badge>
          {node.domain_cluster && (
            <Badge 
              variant="outline" 
              className="bg-blue-500/5 text-blue-500 border-blue-500/20 font-black text-[9px] uppercase"
            >
              {node.domain_cluster}
            </Badge>
          )}
        </div>
      </CardHeader>

      {/* Content */}
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="p-6 space-y-6">
            {/* Purpose Statement (Semanticist) */}
            {nodeDetails?.purpose_statement && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="w-4 h-4 text-[#d4af35]" />
                  <h4 className="text-xs font-black text-white uppercase tracking-wide">
                    Purpose Statement
                  </h4>
                </div>
                <p className="text-sm text-[#94a3b8] leading-relaxed italic bg-[#0a0f18] p-4 rounded border border-[#1e293b]">
                  {nodeDetails.purpose_statement}
                </p>
              </div>
            )}

            {/* Git Velocity (Surveyor) */}
            {nodeDetails?.git_velocity !== undefined && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <GitBranch className="w-4 h-4 text-emerald-500" />
                  <h4 className="text-xs font-black text-white uppercase tracking-wide">
                    Git Velocity
                  </h4>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
                    <p className="text-[9px] text-[#475569] uppercase mb-1">Commits (90d)</p>
                    <p className="text-lg font-black text-white">{nodeDetails.git_velocity}</p>
                  </div>
                  <div className="bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
                    <p className="text-[9px] text-[#475569] uppercase mb-1">Complexity</p>
                    <p className="text-lg font-black text-white">{nodeDetails.complexity_score || 'N/A'}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Public API Surface */}
            {nodeDetails?.public_api && nodeDetails.public_api.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Code className="w-4 h-4 text-blue-500" />
                  <h4 className="text-xs font-black text-white uppercase tracking-wide">
                    Public API
                  </h4>
                </div>
                <div className="space-y-2">
                  {nodeDetails.public_api.slice(0, 5).map((api: any, i: number) => (
                    <div key={i} className="bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
                      <p className="text-xs font-mono text-[#d4af35] mb-1">{api.name}</p>
                      {api.signature && (
                        <SyntaxHighlighter
                          language="python"
                          style={vscDarkPlus}
                          customStyle={{
                            margin: 0,
                            padding: '8px',
                            fontSize: '10px',
                            background: '#0a0f18',
                            border: 'none'
                          }}
                        >
                          {api.signature}
                        </SyntaxHighlighter>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* SQL Query (for Transformations) */}
            {nodeDetails?.sql_query && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Database className="w-4 h-4 text-amber-500" />
                  <h4 className="text-xs font-black text-white uppercase tracking-wide">
                    SQL Query
                  </h4>
                </div>
                <SyntaxHighlighter
                  language="sql"
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    padding: '12px',
                    fontSize: '11px',
                    background: '#0a0f18',
                    border: '1px solid #1e293b',
                    borderRadius: '4px'
                  }}
                >
                  {nodeDetails.sql_query}
                </SyntaxHighlighter>
              </div>
            )}

            {/* Dataset Metadata (for Datasets) */}
            {node.node_type === 'dataset' && nodeDetails?.storage_type && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Database className="w-4 h-4 text-purple-500" />
                  <h4 className="text-xs font-black text-white uppercase tracking-wide">
                    Dataset Metadata
                  </h4>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
                    <span className="text-xs text-[#475569] uppercase">Storage Type</span>
                    <span className="text-xs font-mono text-white">{nodeDetails.storage_type}</span>
                  </div>
                  {nodeDetails.freshness_sla && (
                    <div className="flex justify-between items-center bg-[#0a0f18] p-3 rounded border border-[#1e293b]">
                      <span className="text-xs text-[#475569] uppercase">Freshness SLA</span>
                      <span className="text-xs font-mono text-white">{nodeDetails.freshness_sla}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Source File Preview */}
            {nodeDetails?.source_code && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Code className="w-4 h-4 text-cyan-500" />
                  <h4 className="text-xs font-black text-white uppercase tracking-wide">
                    Source Preview
                  </h4>
                </div>
                <SyntaxHighlighter
                  language={getLanguage(node.path || '')}
                  style={vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    padding: '12px',
                    fontSize: '10px',
                    background: '#0a0f18',
                    border: '1px solid #1e293b',
                    borderRadius: '4px',
                    maxHeight: '300px'
                  }}
                  showLineNumbers
                >
                  {nodeDetails.source_code.slice(0, 500)}
                </SyntaxHighlighter>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
