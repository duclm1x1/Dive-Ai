import { ElegantThinkingPanel } from '@/components/thinking/ElegantThinkingPanel';

interface ThinkingPanelProps {
  isLive?: boolean;
}

export function ThinkingPanel({ isLive = true }: ThinkingPanelProps) {
  // Use elegant thinking panel with Manus-inspired design
  return <ElegantThinkingPanel />;
}
