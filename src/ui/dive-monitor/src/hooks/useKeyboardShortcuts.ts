import { useEffect, useCallback } from 'react';
import { useRuntimeStore, TAB_SHORTCUTS } from '@/stores/runtimeStore';

export function useKeyboardShortcuts() {
  const { setActiveTab, activeTab } = useRuntimeStore();

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Ignore if typing in input
    if (
      e.target instanceof HTMLInputElement ||
      e.target instanceof HTMLTextAreaElement ||
      e.target instanceof HTMLSelectElement
    ) {
      return;
    }

    // Global search with /
    if (e.key === '/') {
      e.preventDefault();
      // Focus search input if exists
      const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
      if (searchInput) {
        searchInput.focus();
      }
      return;
    }

    // Tab navigation with g + key
    if (e.key === 'g') {
      // Wait for next key
      const handleNextKey = (nextE: KeyboardEvent) => {
        const tab = TAB_SHORTCUTS[nextE.key];
        if (tab) {
          setActiveTab(tab);
        }
        window.removeEventListener('keydown', handleNextKey);
      };
      
      window.addEventListener('keydown', handleNextKey, { once: true });
      
      // Timeout to remove listener if no second key
      setTimeout(() => {
        window.removeEventListener('keydown', handleNextKey);
      }, 1000);
      return;
    }

    // Quick tab switching with numbers
    if (e.key >= '1' && e.key <= '4' && !e.ctrlKey && !e.metaKey) {
      const tabs = ['activity', 'rag', 'evidence', 'settings'];
      const index = parseInt(e.key) - 1;
      if (tabs[index]) {
        setActiveTab(tabs[index]);
      }
      return;
    }

    // Escape to close drawer
    if (e.key === 'Escape') {
      useRuntimeStore.getState().closeWhyDrawer();
      return;
    }
  }, [setActiveTab]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
