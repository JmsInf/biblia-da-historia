const { app, BrowserWindow, Menu, shell, ipcMain } = require("electron");
const path = require("path");

if (process.platform === "linux") app.commandLine.appendSwitch("no-sandbox");

// Requisições ao Stable Diffusion local feitas pelo processo principal (sem restrição de CORS)
ipcMain.handle("sd", async (_e, url, body) => {
  const r = await fetch(url, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined
  });
  if (!r.ok) throw new Error(r.status + " " + (await r.text()).slice(0, 200));
  return r.json();
});

function createWindow() {
  Menu.setApplicationMenu(null);
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    title: "Bíblia da História",
    backgroundColor: "#14121a",
    autoHideMenuBar: true,
    webPreferences: { contextIsolation: true, nodeIntegration: false, preload: path.join(__dirname, "preload.js") }
  });
  win.loadFile(path.join(__dirname, "app", "index.html"));
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: "deny" }; });
  win.webContents.on("before-input-event", (e, i) => {
    if (i.type === "keyDown" && (i.key === "F11")) win.setFullScreen(!win.isFullScreen());
    if (i.type === "keyDown" && i.control && i.shift && i.key.toLowerCase() === "i") win.webContents.toggleDevTools();
  });
}
app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
