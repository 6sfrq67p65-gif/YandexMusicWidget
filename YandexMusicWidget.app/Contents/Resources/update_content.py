import sys

with open("/Users/artemcirkov/Gravity/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/ContentView.swift", "r") as f:
    content = f.read()

new_content = """import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = WebViewModel.shared
    @AppStorage("isHorizontal") private var isHorizontal = false
    
    var body: some View {
        ZStack {
            // Фон матовое стекло (с принудительным заполнением 100% пространства)
            VisualEffectView(material: .hudWindow, blendingMode: .behindWindow)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .ignoresSafeArea()
            
            // Основной интерфейс мини-плеера
            if isHorizontal {
                horizontalBody
            } else {
                verticalBody
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity) // Динамическое заполнение всего окна Mac
        .onAppear {
            // При запуске приложения невидимо инициализируем браузер в фоне
            BrowserWindowManager.shared.setup()
            updateWindowSize(animated: false)
        }
        .onChange(of: isHorizontal) { _ in
            updateWindowSize(animated: true)
        }
    }
    
    private func updateWindowSize(animated: Bool) {
        if let window = NSApplication.shared.windows.first {
            let newSize = isHorizontal ? NSSize(width: 420, height: 180) : NSSize(width: 250, height: 420)
            
            if animated {
                var frame = window.frame
                frame.origin.y += frame.size.height - newSize.height // Сохраняем позицию верхнего левого угла
                frame.size = newSize
                window.setFrame(frame, display: true, animate: true)
            } else {
                window.setContentSize(newSize)
            }
        }
    }
    
    private var verticalBody: some View {
        VStack(spacing: 12) {
            // Обложка
            coverView(size: 200)
            
            // Название и артист
            VStack(spacing: 4) {
                Text(viewModel.trackTitle)
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                
                Text(viewModel.artist.isEmpty ? " " : viewModel.artist)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.7))
                    .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 10)
            
            // Кнопки управления
            HStack(spacing: 25) {
                playbackControls
            }
            .padding(.top, 5)
            
            Spacer(minLength: 0) // Толкает нижние кнопки вниз, а верхние элементы вверх
            
            // Нижняя панель кнопок
            HStack(spacing: 12) {
                powerButton
                browserButton
                layoutButton
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 20)
        }
        .padding(.top, 25)
    }
    
    private var horizontalBody: some View {
        HStack(spacing: 15) {
            // Обложка
            coverView(size: 140)
            
            VStack(alignment: .leading, spacing: 0) {
                // Название и артист
                Text(viewModel.trackTitle)
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                
                Text(viewModel.artist.isEmpty ? " " : viewModel.artist)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.7))
                    .lineLimit(1)
                    .padding(.top, 2)
                
                Spacer()
                
                // Кнопки управления
                HStack(spacing: 25) {
                    playbackControls
                }
                .frame(maxWidth: .infinity, alignment: .center)
                
                Spacer()
                
                // Нижняя панель кнопок
                HStack(spacing: 12) {
                    powerButton
                    browserButton
                    layoutButton
                }
            }
            .padding(.vertical, 5)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 20)
    }
    
    private func coverView(size: CGFloat) -> some View {
        AsyncImage(url: URL(string: viewModel.coverURL)) { phase in
            if let image = phase.image {
                image.resizable()
                     .aspectRatio(contentMode: .fill)
            } else if phase.error != nil {
                Color.black.opacity(0.5)
            } else {
                Color.black.opacity(0.3)
            }
        }
        .frame(width: size, height: size)
        .cornerRadius(12)
        .shadow(radius: 5)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.white.opacity(0.2), lineWidth: 1)
        )
    }
    
    @ViewBuilder
    private var playbackControls: some View {
        Button(action: { viewModel.prevTrack() }) {
            Image(systemName: "backward.fill")
                .font(.system(size: 18))
                .foregroundColor(.white)
        }
        .buttonStyle(PlainButtonStyle())
        
        Button(action: { viewModel.playPause() }) {
            Image(systemName: viewModel.isPlaying ? "pause.circle.fill" : "play.circle.fill")
                .font(.system(size: 38))
                .foregroundColor(.white)
        }
        .buttonStyle(PlainButtonStyle())
        
        Button(action: { viewModel.nextTrack() }) {
            Image(systemName: "forward.fill")
                .font(.system(size: 18))
                .foregroundColor(.white)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var powerButton: some View {
        Button(action: { 
            NSApplication.shared.terminate(nil)
        }) {
            Image(systemName: "power")
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(.white.opacity(0.8))
                .frame(width: 36, height: 36)
                .background(Color.white.opacity(0.15))
                .clipShape(Circle())
                .overlay(
                    Circle()
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var browserButton: some View {
        Button(action: { 
            BrowserWindowManager.shared.show()
        }) {
            HStack {
                Image(systemName: "safari.fill")
                Text("Открыть плеер")
                    .fontWeight(.medium)
            }
            .font(.system(size: 13))
            .foregroundColor(.white.opacity(0.9))
            .frame(maxWidth: .infinity, minHeight: 36, maxHeight: 36)
            .background(Color.white.opacity(0.15))
            .cornerRadius(18)
            .overlay(
                RoundedRectangle(cornerRadius: 18)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var layoutButton: some View {
        Button(action: { 
            withAnimation {
                isHorizontal.toggle()
            }
        }) {
            Image(systemName: isHorizontal ? "rectangle.portrait" : "rectangle")
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(.white.opacity(0.8))
                .frame(width: 36, height: 36)
                .background(Color.white.opacity(0.15))
                .clipShape(Circle())
                .overlay(
                    Circle()
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// Вспомогательная View для эффекта размытия (Vibrancy) в macOS
struct VisualEffectView: NSViewRepresentable {
    let material: NSVisualEffectView.Material
    let blendingMode: NSVisualEffectView.BlendingMode

    func makeNSView(context: Context) -> NSVisualEffectView {
        let visualEffectView = NSVisualEffectView()
        visualEffectView.material = material
        visualEffectView.blendingMode = blendingMode
        visualEffectView.state = .active
        return visualEffectView
    }

    func updateNSView(_ visualEffectView: NSVisualEffectView, context: Context) {
        visualEffectView.material = material
        visualEffectView.blendingMode = blendingMode
    }
}
"""

with open("/Users/artemcirkov/Gravity/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/YandexMusicWidget/ContentView.swift", "w") as f:
    f.write(new_content)

print("Updated ContentView.swift")
