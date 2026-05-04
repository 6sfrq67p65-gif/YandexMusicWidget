import SwiftUI
import WebKit
import Combine

class WebViewModel: ObservableObject {
    static let shared = WebViewModel()
    
    @Published var trackTitle: String = "Не играет"
    @Published var artist: String = "Загрузка..."
    @Published var coverURL: String = ""
    @Published var isPlaying: Bool = false
    @Published var progress: Double = 0.0
    @Published var positionText: String = "0:00"
    @Published var remainingText: String = "0:00"
    
    var webView: WKWebView?
    
    func playPause() {
        let js = """
        if (typeof externalAPI !== 'undefined') { externalAPI.togglePause(); }
        else {
            var pauseBtn = document.querySelector('[aria-label*="Пауза"], [title*="Пауза"]');
            if (pauseBtn) {
                pauseBtn.click();
            } else {
                var playBtn = document.querySelector('[aria-label*="Играть"], [aria-label*="Воспроизвести"], [title*="Играть"], [title*="Воспроизвести"], [class*="playButton" i]');
                if (playBtn) {
                    playBtn.click();
                } else {
                    var media = document.querySelector('video, audio');
                    if (media) {
                        if (media.paused) media.play();
                        else media.pause();
                    }
                }
            }
        }
        """
        webView?.evaluateJavaScript(js, completionHandler: nil)
    }
    
    func nextTrack() {
        let js = """
        if (typeof externalAPI !== 'undefined') { externalAPI.next(); }
        else {
            var btn = document.querySelector('[aria-label*="Следующ"], [aria-label*="Вперед"], [class*="next" i], [class*="skipForward" i]');
            if (btn) btn.click();
        }
        """
        webView?.evaluateJavaScript(js, completionHandler: nil)
    }
    
    func prevTrack() {
        let js = """
        if (typeof externalAPI !== 'undefined') { externalAPI.prev(); }
        else {
            var btn = document.querySelector('[aria-label*="Предыдущ"], [aria-label*="Назад"], [class*="prev" i], [class*="skipBack" i]');
            if (btn) btn.click();
        }
        """
        webView?.evaluateJavaScript(js, completionHandler: nil)
    }
    
    func seek(to progress: Double) {
        let js = """
        if (typeof externalAPI !== 'undefined') {
            var track = externalAPI.getCurrentTrack();
            var dur = track ? track.duration : 0;
            if (dur > 0) externalAPI.setPosition(\(progress) * dur);
        } else {
            var media = document.querySelector('video, audio');
            if (media && media.duration && media.duration !== Infinity) {
                media.currentTime = \(progress) * media.duration;
            } else {
                var bar = document.querySelector('[class*="progress" i], [class*="timeline" i]');
                if (bar) {
                    var rect = bar.getBoundingClientRect();
                    var x = rect.left + rect.width * \(progress);
                    var y = rect.top + rect.height / 2;
                    var clickEvent = new MouseEvent('click', {
                        view: window, bubbles: true, cancelable: true, clientX: x, clientY: y
                    });
                    bar.dispatchEvent(clickEvent);
                }
            }
        }
        """
        webView?.evaluateJavaScript(js, completionHandler: nil)
    }
    
    func checkMetadata() {
        let js = """
        (function() {
            try {
                var title = 'Не играет';
                var artist = '';
                var cover = '';
                var isPlaying = false;
                var position = 0;
                var duration = 0;
                
                // 1. Попытка через Yandex externalAPI
                if (typeof externalAPI !== 'undefined') {
                    try {
                        var track = externalAPI.getCurrentTrack();
                        if (track) {
                            title = track.title || title;
                            artist = track.artists ? track.artists.map(a => a.title).join(', ') : artist;
                            cover = track.cover ? 'https://' + track.cover.replace('%%', '400x400') : cover;
                        }
                        if (externalAPI.isPlaying()) isPlaying = true;
                        var p = externalAPI.getProgress();
                        if (p && p.duration > 0) {
                            position = p.position;
                            duration = p.duration;
                        }
                    } catch(e) {}
                }
                
                // 2. Универсальный Media Session API
                if (navigator.mediaSession) {
                    if (navigator.mediaSession.metadata) {
                        title = navigator.mediaSession.metadata.title || title;
                        artist = navigator.mediaSession.metadata.artist || artist;
                        var artwork = navigator.mediaSession.metadata.artwork;
                        if (artwork && artwork.length > 0) {
                            var src = artwork[artwork.length - 1].src;
                            if (src.includes('avatars.yandex.net')) {
                                cover = src.replace(/\\d+x\\d+/, '400x400');
                            } else {
                                cover = src;
                            }
                        }
                    }
                    if (navigator.mediaSession.playbackState === 'playing') isPlaying = true;
                    if (navigator.mediaSession.positionState && navigator.mediaSession.positionState.duration > 0) {
                        position = navigator.mediaSession.positionState.position;
                        duration = navigator.mediaSession.positionState.duration;
                    }
                }
                
                // 3. Прямой опрос DOM-тегов audio/video
                var mediaList = document.querySelectorAll('audio, video');
                var isDOMPlaying = false;
                for (var i = 0; i < mediaList.length; i++) {
                    var m = mediaList[i];
                    if (!m.paused) {
                        isDOMPlaying = true;
                        if (duration === 0 && m.duration > 0 && m.duration !== Infinity) {
                            position = m.currentTime;
                            duration = m.duration;
                        }
                    }
                }
                if (isDOMPlaying) isPlaying = true;
                
                // 4. Поиск ползунка прогресса в React UI (как запасной вариант для времени)
                if (duration === 0 || isNaN(duration)) {
                    var slider = document.querySelector('[role="slider"][aria-valuemax]');
                    if (slider) {
                        var val = parseFloat(slider.getAttribute('aria-valuenow'));
                        var max = parseFloat(slider.getAttribute('aria-valuemax'));
                        if (!isNaN(val) && !isNaN(max) && max > 0) {
                            position = val;
                            duration = max;
                        }
                    }
                }
                
                // 5. Проверка кнопок Play/Pause в интерфейсе
                if (!isPlaying) {
                    var pauseBtn = document.querySelector('[aria-label*="Пауза"], [title*="Пауза"]');
                    if (pauseBtn) isPlaying = true;
                }
                
                // Резервный поиск обложки
                if (cover === '' || cover === 'Не играет') {
                    var images = document.querySelectorAll('img');
                    for (var i = 0; i < images.length; i++) {
                        var imgsrc = images[i].src;
                        if (imgsrc && imgsrc.includes('avatars.yandex.net/get-music-content')) {
                            cover = imgsrc.replace(/\\d+x\\d+/, '400x400');
                        }
                    }
                }
                
                // Итоги
                var progress = 0.0;
                if (duration > 0) progress = position / duration;
                progress = Math.max(0.0, Math.min(1.0, progress));
                
                function formatTime(sec) {
                    if (!sec || isNaN(sec) || sec === Infinity) return "0:00";
                    var m = Math.floor(sec / 60);
                    var s = Math.floor(sec % 60);
                    return m + ":" + (s < 10 ? "0" : "") + s;
                }
                
                var posText = formatTime(position);
                var remText = formatTime(Math.max(0, duration - position));
                
                return {
                    title: title,
                    artist: artist,
                    cover: cover,
                    isPlaying: isPlaying,
                    progress: progress,
                    positionText: posText || "0:00",
                    remainingText: remText || "0:00"
                };
            } catch (e) {
                return {
                    title: 'Ошибка JS: ' + e.toString(),
                    artist: '',
                    cover: '',
                    isPlaying: false,
                    progress: 0.0,
                    positionText: "0:00",
                    remainingText: "0:00"
                };
            }
        })();
        """
        
        webView?.evaluateJavaScript(js) { (result, error) in
            if let dict = result as? [String: Any] {
                DispatchQueue.main.async {
                    let newTitle = dict["title"] as? String ?? "Не играет"
                    let newArtist = dict["artist"] as? String ?? ""
                    let newCover = dict["cover"] as? String ?? ""
                    let newIsPlaying = dict["isPlaying"] as? Bool ?? false
                    let newProgress = dict["progress"] as? Double ?? 0.0
                    let newPosText = dict["positionText"] as? String ?? "0:00"
                    let newRemText = dict["remainingText"] as? String ?? "0:00"
                    
                    self.trackTitle = newTitle
                    self.artist = newArtist
                    self.isPlaying = newIsPlaying
                    self.progress = newProgress.isNaN ? 0.0 : newProgress
                    self.positionText = newPosText
                    self.remainingText = newRemText
                    
                    if newCover != "" && newCover != self.coverURL {
                        // Яндекс музыка часто дает обложки 50x50, меняем на 400x400 для виджета
                        self.coverURL = newCover.replacingOccurrences(of: "50x50", with: "400x400")
                    }
                }
            }
        }
    }
}

class BrowserWindowManager: NSObject, NSWindowDelegate {
    static let shared = BrowserWindowManager()
    var window: NSWindow?
    var webView: WKWebView?
    
    func setup() {
        if window == nil {
            let config = WKWebViewConfiguration()
            
            // ВАЖНО: Разрешаем воспроизведение медиа без прямого клика пользователя в WebView!
            // Без этого WebKit блокирует вызов media.play() из JavaScript.
            config.mediaTypesRequiringUserActionForPlayback = []
            
            let userScriptCode = """
            Object.defineProperty(window, 'innerWidth', { get: function() { return 1024; }, configurable: true });
            Object.defineProperty(window, 'innerHeight', { get: function() { return 768; }, configurable: true });
            Object.defineProperty(document.documentElement, 'clientWidth', { get: function() { return 1024; }, configurable: true });
            Object.defineProperty(document.documentElement, 'clientHeight', { get: function() { return 768; }, configurable: true });
            window.matchMedia = window.matchMedia || function() { return { matches: false, addListener: function() {}, removeListener: function() {} }; };
            """
            let userScript = WKUserScript(source: userScriptCode, injectionTime: .atDocumentStart, forMainFrameOnly: false)
            config.userContentController.addUserScript(userScript)
            
            webView = WKWebView(frame: CGRect(x: 0, y: 0, width: 800, height: 600), configuration: config)
            webView?.customUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            
            WebViewModel.shared.webView = webView
            
            let request = URLRequest(url: URL(string: "https://music.yandex.ru")!)
            webView?.load(request)
            
            let win = NSWindow(
                contentRect: NSRect(x: 0, y: 0, width: 800, height: 600),
                styleMask: [.titled, .closable, .miniaturizable],
                backing: .buffered,
                defer: false
            )
            win.title = "Яндекс Музыка"
            win.center()
            win.contentView = webView
            win.isReleasedWhenClosed = false
            win.delegate = self // ВАЖНО: перехватываем закрытие
            
            self.window = win
            
            Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
                WebViewModel.shared.checkMetadata()
            }
        }
    }
    
    func show() {
        setup()
        // Восстанавливаем видимость окна
        window?.alphaValue = 1.0
        window?.ignoresMouseEvents = false
        window?.makeKeyAndOrderFront(nil)
    }
    
    // Этот метод вызывается, когда пользователь нажимает красный крестик
    func windowShouldClose(_ sender: NSWindow) -> Bool {
        // Вместо реального закрытия (которое ломает WebKit), мы просто делаем окно невидимым!
        sender.alphaValue = 0.0
        sender.ignoresMouseEvents = true
        return false // Запрещаем реальное закрытие
    }
}

