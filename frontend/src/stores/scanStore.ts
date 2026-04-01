import { create } from "zustand";
import type { FileInfo, QuickScanResult } from "../types";

interface ScanState {
  quickResult: QuickScanResult | null;
  liveFiles: FileInfo[];
  progress: { count: number; totalSize: number; currentPath: string };
  setQuickResult: (r: QuickScanResult | null) => void;
  addLiveFile: (f: FileInfo) => void;
  clearLive: () => void;
  setProgress: (p: { count: number; totalSize: number; currentPath: string }) => void;
}

export const useScanStore = create<ScanState>((set) => ({
  quickResult: null,
  liveFiles: [],
  progress: { count: 0, totalSize: 0, currentPath: "" },
  setQuickResult: (quickResult) => set({ quickResult }),
  addLiveFile: (f) =>
    set((s) => ({
      liveFiles: s.liveFiles.length > 200 ? s.liveFiles : [...s.liveFiles, f],
    })),
  clearLive: () => set({ liveFiles: [], progress: { count: 0, totalSize: 0, currentPath: "" } }),
  setProgress: (progress) => set({ progress }),
}));
