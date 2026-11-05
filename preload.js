const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("native", { sd: (url, body) => ipcRenderer.invoke("sd", url, body) });
