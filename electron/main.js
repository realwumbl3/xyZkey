const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')

const ipcEvents = {
    'send': (_, event, data) => {
        windowsGlobal[0].webContents.openDevTools()
    }
}

for (let [ev, fn] of Object.entries(ipcEvents)) ipcMain.on(ev, fn)

const windowsGlobal = []

const createWindow = () => {
    const mainWindow = new BrowserWindow({
        width: 777,
        height: 333,
        frame: false,
        alwaysOnTop: true,
        transparent: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })
    mainWindow.setSkipTaskbar(true);
    mainWindow.setIgnoreMouseEvents(true);
    mainWindow.loadFile('./main.html')
    windowsGlobal.push(mainWindow)
    // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
    createWindow()

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})
