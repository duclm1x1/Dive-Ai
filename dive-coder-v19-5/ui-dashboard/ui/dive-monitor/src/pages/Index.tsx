import { useEffect, useCallback } from 'react';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { TabNavigation, type TabId } from '@/components/dashboard/TabNavigation';
import { ActivityTab } from '@/components/activity/ActivityTab';
import { RAGInspectorTab } from '@/components/rag/RAGInspectorTab';
import { EvidenceClaimsTab } from '@/components/evidence/EvidenceClaimsTab';
import { SettingsTab } from '@/components/settings/SettingsTab';
import { WhyDrawer } from '@/components/activity/WhyDrawer';
import { useRuntimeStore } from '@/stores/runtimeStore';
import { useEventStream } from '@/providers/EventStreamProvider';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { mockEvidencePack } from '@/data/mockData';

const Index = () => {
  const { activeTab, setActiveTab, isConnected } = useRuntimeStore();
  const { sendCommand } = useEventStream();
  
  // Enable keyboard shortcuts
  useKeyboardShortcuts();

  const handlePause = useCallback(() => {
    sendCommand('pause');
  }, [sendCommand]);

  const handleResume = useCallback(() => {
    sendCommand('resume');
  }, [sendCommand]);

  const handleCancel = useCallback(() => {
    sendCommand('cancel');
  }, [sendCommand]);

  const handleRerun = useCallback(() => {
    sendCommand('rerun');
  }, [sendCommand]);

  const handleExport = useCallback(() => {
    const blob = new Blob([JSON.stringify(mockEvidencePack, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evidence_pack_${mockEvidencePack.pack_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'activity':
        return <ActivityTab />;
      case 'rag':
        return <RAGInspectorTab />;
      case 'evidence':
        return <EvidenceClaimsTab />;
      case 'settings':
        return <SettingsTab />;
      default:
        return <ActivityTab />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      {/* Header */}
      <DashboardHeader
        isConnected={isConnected}
        workspace="my-project"
        onPause={handlePause}
        onResume={handleResume}
        onCancel={handleCancel}
        onRerun={handleRerun}
        onExport={handleExport}
      />

      {/* Tab Navigation */}
      <TabNavigation 
        activeTab={activeTab as TabId} 
        onTabChange={(tab) => setActiveTab(tab)} 
      />

      {/* Tab Content */}
      <main className="flex-1 overflow-hidden">
        {renderTabContent()}
      </main>

      {/* Why Drawer */}
      <WhyDrawer />
    </div>
  );
};

export default Index;
