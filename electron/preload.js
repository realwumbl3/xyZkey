const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld('electron', {
    send: (...data) => ipcRenderer.send("send", ...data)
})