import { useCallback } from "react";
import { api } from "../services/api";
import { useScanStore } from "../stores/scanStore";

export function useScanner() {
  const setQuickResult = useScanStore((s) => s.setQuickResult);
  const addLiveFile = useScanStore((s) => s.addLiveFile);
  const clearLive = useScanStore((s) => s.clearLive);
  const setProgress = useScanStore((s) => s.setProgress);

  const runQuickScan = useCallback(async () => {
    const result = await api.quickScan();
    setQuickResult(result);
    return result;
  }, [setQuickResult]);

  const startLiveScan = useCallback(() => {
    clearLive();
    return api.startScan(
      (file) => addLiveFile(file),
      (p) =>
        setProgress({
          count: p.count,
          totalSize: p.total_size,
          currentPath: p.current_file,
        }),
      () => {}
    );
  }, [addLiveFile, clearLive, setProgress]);

  return { runQuickScan, startLiveScan, clearLive };
}
