import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

function CodeBlock({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-lg border border-surface-800 overflow-hidden bg-surface-950">
      <div className="flex items-center justify-between px-3 py-1.5 bg-surface-900 border-b border-surface-800">
        <span className="text-[11px] font-mono text-surface-500">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-[11px] text-surface-500 hover:text-white transition-colors"
        >
          {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="p-3 overflow-x-auto">
        <code className="text-[13px] leading-relaxed font-mono text-surface-200">{code}</code>
      </pre>
    </div>
  );
}

function InlineCode({ children }: { children: string }) {
  return (
    <code className="px-1.5 py-0.5 rounded bg-surface-800 border border-surface-700 text-brand-300 text-[13px] font-mono">
      {children}
    </code>
  );
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="text-sm leading-relaxed text-surface-200 space-y-2">
      {parts.map((part, i) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          const inner = part.slice(3, -3);
          const newlineIdx = inner.indexOf('\n');
          const language = newlineIdx > 0 ? inner.slice(0, newlineIdx).trim() : '';
          const code = newlineIdx > 0 ? inner.slice(newlineIdx + 1) : inner;
          return <CodeBlock key={i} code={code} language={language} />;
        }
        return <TextBlock key={i} text={part} />;
      })}
    </div>
  );
}

function TextBlock({ text }: { text: string }) {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let listItems: string[] = [];
  let orderedItems: string[] = [];

  const flushList = (key: string) => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={key} className="list-disc list-inside space-y-0.5 text-surface-300 ml-1">
          {listItems.map((item, j) => <li key={j}>{renderInline(item)}</li>)}
        </ul>
      );
      listItems = [];
    }
    if (orderedItems.length > 0) {
      elements.push(
        <ol key={key} className="list-decimal list-inside space-y-0.5 text-surface-300 ml-1">
          {orderedItems.map((item, j) => <li key={j}>{renderInline(item)}</li>)}
        </ol>
      );
      orderedItems = [];
    }
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trimStart();

    if (trimmed.startsWith('### ')) {
      flushList(`list-${idx}`);
      elements.push(<h4 key={idx} className="text-sm font-semibold text-white mt-3 mb-1">{renderInline(trimmed.slice(4))}</h4>);
    } else if (trimmed.startsWith('## ')) {
      flushList(`list-${idx}`);
      elements.push(<h3 key={idx} className="text-base font-semibold text-white mt-3 mb-1">{renderInline(trimmed.slice(3))}</h3>);
    } else if (trimmed.startsWith('# ')) {
      flushList(`list-${idx}`);
      elements.push(<h2 key={idx} className="text-lg font-bold text-white mt-3 mb-1">{renderInline(trimmed.slice(2))}</h2>);
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      listItems.push(trimmed.slice(2));
    } else if (/^\d+\.\s/.test(trimmed)) {
      orderedItems.push(trimmed.replace(/^\d+\.\s/, ''));
    } else if (trimmed === '') {
      flushList(`list-${idx}`);
    } else {
      flushList(`list-${idx}`);
      elements.push(<p key={idx} className="text-surface-300">{renderInline(trimmed)}</p>);
    }
  });

  flushList('list-end');
  return <>{elements}</>;
}

function renderInline(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const regex = /(\*\*(.+?)\*\*)|(\*(.+?)\*)|(`([^`]+)`)/g;
  let last = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index));
    }
    if (match[2]) {
      nodes.push(<strong key={match.index} className="font-semibold text-white">{match[2]}</strong>);
    } else if (match[4]) {
      nodes.push(<em key={match.index} className="italic text-surface-300">{match[4]}</em>);
    } else if (match[6]) {
      nodes.push(<InlineCode key={match.index}>{match[6]}</InlineCode>);
    }
    last = match.index + match[0].length;
  }

  if (last < text.length) {
    nodes.push(text.slice(last));
  }

  return nodes.length > 0 ? nodes : [text];
}
