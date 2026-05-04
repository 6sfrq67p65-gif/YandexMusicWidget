import SwiftUI

@main
struct YandexMusicWidgetApp: App {
    // Подключаем AppDelegate для настройки плавающего окна
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .edgesIgnoringSafeArea(.all) // Заполняем фон целиком, чтобы не было прозрачной полосы
        }
        .windowStyle(HiddenTitleBarWindowStyle())
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Настраиваем основное окно, чтобы оно было похоже на виджет
        if let window = NSApplication.shared.windows.first {
            // Скрываем стандартный заголовок macOS (кнопки закрыть/свернуть)
            window.titlebarAppearsTransparent = true
            window.titleVisibility = .hidden
            window.standardWindowButton(.zoomButton)?.isHidden = true
            window.standardWindowButton(.miniaturizeButton)?.isHidden = true
            window.standardWindowButton(.closeButton)?.isHidden = true
            
            // Делаем окно "плавающим" поверх остальных
            window.level = .floating
            
            // Делаем фон прозрачным для эффекта стекла
            window.backgroundColor = .clear
            window.isOpaque = false
            window.hasShadow = true
            
            // Фиксируем размер виджета навсегда (чтобы не было багов с отступами)
            window.styleMask.remove(.resizable)
            window.setContentSize(NSSize(width: 250, height: 420))
            
            // Убираем стандартный серый фон
            window.contentView?.wantsLayer = true
            window.contentView?.layer?.backgroundColor = NSColor.clear.cgColor
        }
    }
}
