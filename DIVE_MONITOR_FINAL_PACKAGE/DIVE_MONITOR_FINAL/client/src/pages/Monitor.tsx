import { useCallback } from 'react';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { TabNavigation, type TabId } from '@/components/dashboard/TabNavigation';
import { DashboardOverview } from '@/components/dashboard/DashboardOverview';
import { ActivityTab } from '@/components/activity/ActivityTab';
import { SettingsTab } from '@/components/settings/SettingsTab';
import { WhyDrawer } from '@/components/activity/WhyDrawer';
import { useRuntimeStore } from '@/stores/runtimeStore';
import { useEventStream } from '@/providers/EventStreamProvider';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';


const Monitor = () => {
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
    // Export functionality will be implemented when real data is available
    console.log('Export clicked');
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardOverview />;
      case 'activity':
        return <ActivityTab />;
      case 'settings':
        return <SettingsTab />;
      default:
        return <DashboardOverview />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      {/* Header */}
      <DashboardHeader
        isConnected={isConnected}
        workspace="dive-monitor"
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

export default Monitor;
