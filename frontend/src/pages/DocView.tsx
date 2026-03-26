import { useState, useEffect } from 'react'
import { useParams } from '@tanstack/react-router'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FileText, Download, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

interface DocViewProps {
  type: 'ledger' | 'brief'
}

export default function DocView({ type }: DocViewProps) {
  const { projectId } = useParams({ from: `/codebase/$projectId/overview` }) 
// or whatever the exact path is in your routeTree for the overview
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const fetchDoc = async () => {
      setLoading(true)
      try {
        // In a real app, this would be an API call
        // For now we assume the files are served by the backend
        const fileName = type === 'ledger' ? 'CODEBASE.md' : 'ONBOARDING_BRIEF.md'
        // Add cache busting timestamp to prevent loading cached 404s
        const timestamp = Date.now()
        const response = await fetch(`http://localhost:5001/api/projects/${projectId}/artifacts/${fileName}?t=${timestamp}`)
        if (response.ok) {
          const text = await response.text()
          setContent(text)
        } else {
          setContent(`# Error\nCould not load ${fileName}. Make sure the analysis has been run.`)
        }
      } catch (err) {
        setContent('# Error\nFailed to connect to the intelligence server.')
      } finally {
        setLoading(false)
      }
    }

    fetchDoc()
  }, [projectId, type])

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-[#d4af35]/10 rounded-sm border border-[#d4af35]/30">
            <FileText className="w-6 h-6 text-[#d4af35]" />
          </div>
          <div>
            <h2 className="text-2xl font-black uppercase tracking-widest text-[#d4af35]">
              {type === 'ledger' ? 'Project Ledger' : 'Onboarding Brief'}
            </h2>
            <p className="text-xs font-bold text-[#475569] uppercase tracking-tighter">
              {type === 'ledger' ? 'Comprehensive Codebase Documentation' : 'Strategic Integration Guide'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleCopy}
            className="bg-[#1e293b]/50 border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40 text-[#94a3b8] hover:text-[#d4af35] rounded-none px-4"
          >
            {copied ? <Check className="w-3.5 h-3.5 mr-2" /> : <Copy className="w-3.5 h-3.5 mr-2" />}
            {copied ? 'Copied' : 'Copy MD'}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            className="bg-[#1e293b]/50 border-[#1e293b] hover:bg-[#d4af35]/10 hover:border-[#d4af35]/40 text-[#94a3b8] hover:text-[#d4af35] rounded-none px-4"
          >
            <Download className="w-3.5 h-3.5 mr-2" />
            Download
          </Button>
        </div>
      </div>

      <Card className="bg-[#0f172a]/50 border-[#1e293b] rounded-none overflow-hidden relative group">
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[#d4af35]/0 via-[#d4af35]/40 to-[#d4af35]/0" />
        
        {loading ? (
          <div className="p-20 flex flex-col items-center justify-center space-y-4">
             <div className="w-12 h-12 border-2 border-[#d4af35]/20 border-t-[#d4af35] rounded-full animate-spin" />
             <p className="text-[10px] font-black uppercase tracking-widest text-[#475569] animate-pulse">Decrypting Ledger...</p>
          </div>
        ) : (
          <div className="p-10 prose prose-invert prose-slate max-w-none 
            prose-headings:text-[#d4af35] prose-headings:font-black prose-headings:uppercase prose-headings:tracking-widest
            prose-p:text-[#94a3b8] prose-p:leading-relaxed
            prose-strong:text-[#d4af35] prose-strong:font-bold
            prose-code:text-amber-200 prose-code:bg-amber-950/30 prose-code:px-1 prose-code:py-0.5 prose-code:rounded-sm
            prose-pre:bg-[#0a0f18] prose-pre:border prose-pre:border-[#1e293b] prose-pre:rounded-none
            prose-li:text-[#94a3b8]
            prose-hr:border-[#1e293b]">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        )}
      </Card>

      <div className="bg-[#d4af35]/5 border border-[#d4af35]/20 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
           <div className="w-2 h-2 rounded-full bg-[#d4af35] animate-pulse" />
           <p className="text-[10px] font-bold text-[#d4af35]/80 uppercase tracking-widest">Archive Integrity Verified</p>
        </div>
        <p className="text-[9px] font-mono text-[#475569] uppercase font-black tracking-tighter">Last Synced: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  )
}
