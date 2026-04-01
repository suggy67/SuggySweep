import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("suggy", {
  version: "1.0.0",
});
