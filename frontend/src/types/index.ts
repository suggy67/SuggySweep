export type ViewKey =
  | "dashboard"
  | "scanner"
  | "myfiles"
  | "browsers"
  | "apps"
  | "programs"
  | "backup"
  | "restore"
  | "ai"
  | "system"
  | "settings";

export interface InstalledProgram {
  name: string;
  version?: string;
  publisher?: string;
  install_location?: string;
  uninstall_command?: string;
  estimated_size_bytes?: number | null;
}

export interface FileInfo {
  path: string;
  name: string;
  extension: string;
  size: number;
  modified: string;
  category: string;
}

export interface DriveInfo {
  letter: string;
  path: string;
  label: string;
  type: string;
  free_bytes: number;
  total_bytes: number;
  is_system: boolean;
  is_suitable_for_backup: boolean;
}

export interface QuickScanResult {
  categories: Record<
    string,
    { count: number; size: number; files: FileInfo[] }
  >;
  total_files: number;
  total_size: number;
}

export interface SystemInfo {
  os: string;
  edition: string;
  version: string;
  build: number;
  full: string;
  architecture: string;
  hostname: string;
  username?: string;
}
