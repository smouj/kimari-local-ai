'use client'

import { useState, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check, Copy } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface MarkdownRendererProps {
  content: string
  className?: string
}

function CodeBlock({ children, className }: { children: string; className?: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [children])

  // Extract language from className like "language-python"
  const language = className?.replace('language-', '') || ''

  return (
    <div className="relative group my-3">
      {language && (
        <div className="absolute top-2 left-3 text-[10px] font-mono text-muted-foreground/60 uppercase tracking-wider z-10">
          {language}
        </div>
      )}
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 z-10 flex items-center justify-center h-7 w-7 rounded-md bg-muted/80 hover:bg-muted border border-border/50 text-muted-foreground hover:text-foreground transition-all opacity-0 group-hover:opacity-100"
        aria-label="Copy code"
      >
        {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
      </button>
      <pre className="bg-muted/50 rounded-lg p-4 overflow-x-auto text-sm leading-relaxed border border-border/30">
        <code className="font-mono text-foreground">{children}</code>
      </pre>
    </div>
  )
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={cn('prose-kimari', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-foreground mt-4 mb-2 first:mt-0">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-foreground mt-3 mb-2 first:mt-0">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold text-foreground mt-3 mb-1.5 first:mt-0">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-semibold text-foreground mt-2 mb-1 first:mt-0">{children}</h4>
          ),
          p: ({ children }) => (
            <p className="text-sm leading-relaxed text-foreground mb-2 last:mb-0">{children}</p>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-foreground/90">{children}</em>
          ),
          code: ({ children, className: codeClassName }) => {
            // Check if this is an inline code or block code
            // In react-markdown, inline code doesn't have a language class
            const isInline = !codeClassName
            if (isInline) {
              return (
                <code className="bg-muted/50 px-1.5 py-0.5 rounded text-sm font-mono text-primary">
                  {children}
                </code>
              )
            }
            // Block code handled by pre below, but code element still rendered
            return (
              <code className={cn('font-mono text-foreground', codeClassName)}>
                {children}
              </code>
            )
          },
          pre: ({ children }) => {
            // Extract text content from the code block
            const codeElement = children as React.ReactElement<{ children?: string; className?: string }>
            const codeContent = typeof codeElement?.props?.children === 'string'
              ? codeElement.props.children
              : ''
            const codeClass = codeElement?.props?.className || ''
            return <CodeBlock className={codeClass}>{codeContent}</CodeBlock>
          },
          ul: ({ children }) => (
            <ul className="text-sm text-foreground space-y-1 mb-2 ml-4 list-disc list-outside">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="text-sm text-foreground space-y-1 mb-2 ml-4 list-decimal list-outside">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-sm leading-relaxed text-foreground pl-1">{children}</li>
          ),
          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline underline-offset-2 hover:text-primary/80 transition-colors"
            >
              {children}
            </a>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary/30 pl-4 py-1 my-3 bg-muted/20 rounded-r-md italic text-muted-foreground">
              {children}
            </blockquote>
          ),
          hr: () => (
            <hr className="my-4 border-border/50" />
          ),
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-lg border border-border/30">
              <table className="w-full text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-muted/30 border-b border-border/30">{children}</thead>
          ),
          tbody: ({ children }) => (
            <tbody>{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr className="border-b border-border/20 last:border-0">{children}</tr>
          ),
          th: ({ children }) => (
            <th className="px-3 py-2 text-left font-semibold text-foreground text-xs uppercase tracking-wider">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 text-foreground">{children}</td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
