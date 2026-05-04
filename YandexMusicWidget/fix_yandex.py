import sys

with open("/Users/artemcirkov/Gravity/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/YandexWebView.swift", "r") as f:
    content = f.read()

start_marker = "        (function() {\n            try {\n                var title = 'Не играет';"
end_marker = "            } catch (e) {\n                return {\n                    title: 'Ошибка JS: ' + e.toString(),\n                    artist: '',\n                    cover: '',\n                    isPlaying: false,\n                    progress: 0.0,\n                    positionText: \"0:00\",\n                    remainingText: \"0:00\"\n                };\n            }\n        })();"

if start_marker not in content:
    print("start not found")
    sys.exit(1)
if end_marker not in content:
    print("end not found")
    sys.exit(1)

pre = content.split(start_marker)[0]
post = content.split(end_marker)[1]

new_js = """        (function() {
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
        })();"""

with open("/Users/artemcirkov/Gravity/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/YandexWebView.swift", "w") as f:
    f.write(pre + new_js + post)

print("Replaced!")
