import sys
import os
import platform
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ┌────┐                                                     ║
║   │   ─┐    MediaHUD :: CrossPlatform Media Indicator        ║
║   │   ─┘    Designed & Engineered by Eymen ERDOĞDU           ║
║   └────┘    github.com/eymenerdogdu                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

SYSTEM = platform.system()

if SYSTEM == "Linux":
    try:
        import dbus
    except ImportError:
        print("Linux üzerinde DBus kütüphanesi bulunamadı! 'pip install dbus-python' yapın.")
elif SYSTEM == "Windows":
    try:
        import asyncio
        import winrt.windows.media.control as wmc
        from winrt.windows.storage.streams import DataReader, Buffer
    except ImportError:
        print("Windows özellikleri için gerekli kütüphaneler eksik! 'pip install winrt-Windows.Media.Control' yapın.")

class MediaHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setWindowTitle("MediaHUD")
        self.setStyleSheet("background: #202020; color: white; border-radius: 10px;")
        self.setFixedSize(380, 105)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 8)
        main_layout.setSpacing(8)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        self.art_label = QLabel("🎵")
        self.art_label.setFixedSize(60, 60)
        self.art_label.setStyleSheet("background: #333; border-radius: 6px;")
        self.art_label.setAlignment(Qt.AlignCenter)
        body_layout.addWidget(self.art_label, alignment=Qt.AlignVCenter)

        right_stack = QVBoxLayout()
        right_stack.setSpacing(3)

        title_row = QHBoxLayout()
        title_row.setSpacing(5)
        
        self.title_label = QLabel("Bekleniyor...")
        self.title_label.setFont(QFont("Sans Serif", 10, QFont.Bold))
        title_row.addWidget(self.title_label, stretch=1)
        
        self.btn_min = QPushButton("—")
        self.btn_min.setFixedSize(18, 18)
        self.btn_min.setStyleSheet("background: #3c3c3c; border: none; border-radius: 9px; font-size: 8px; font-weight: bold; color: #aaaaaa;")
        self.btn_min.clicked.connect(self.showMinimized)
        title_row.addWidget(self.btn_min, alignment=Qt.AlignTop)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(18, 18)
        self.btn_close.setStyleSheet("background: #550000; border: none; border-radius: 9px; font-size: 9px; font-weight: bold;")
        self.btn_close.clicked.connect(self.close)
        title_row.addWidget(self.btn_close, alignment=Qt.AlignTop)
        
        right_stack.addLayout(title_row)

        self.info_label = QLabel("Sanatçı - Albüm")
        self.info_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")
        right_stack.addWidget(self.info_label)

        controls_row = QHBoxLayout()
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #ff5555; font-size: 9px; font-weight: bold;")
        controls_row.addWidget(self.time_label, alignment=Qt.AlignVCenter)
        
        controls_row.addStretch(1)
        
        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("⏭")
        for btn in [self.btn_prev, self.btn_play, self.btn_next]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setFixedSize(36, 26)
            btn.setStyleSheet("background: #333; border: none; border-radius: 5px; color: white;")
            controls_row.addWidget(btn)
            
        right_stack.addLayout(controls_row)
        body_layout.addLayout(right_stack, stretch=1)
        main_layout.addLayout(body_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { background: #333; border: none; border-radius: 1px; } QProgressBar::chunk { background: #ff5555; }")
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

        self.btn_next.clicked.connect(lambda: self.send_cmd("Next"))
        self.btn_prev.clicked.connect(lambda: self.send_cmd("Previous"))
        self.btn_play.clicked.connect(lambda: self.send_cmd("PlayPause"))
        
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.on_image_downloaded)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
        
        self.current_title = ""
        self.scroll_text = ""
        self.last_art = ""

    def update_ui(self):
        if SYSTEM == "Linux":
            self.update_linux()
        elif SYSTEM == "Windows":
            self.update_windows()
        else:
            self.title_label.setText("Desteklenmeyen OS")

    def get_player_bus(self):
        if SYSTEM != "Linux": return None
        try:
            bus = dbus.SessionBus()
            for name in bus.list_names():
                if name.startswith('org.mpris.MediaPlayer2.'): return name
        except: pass
        return None

    def update_linux(self):
        player = self.get_player_bus()
        if not player: return
        try:
            bus = dbus.SessionBus()
            proxy = bus.get_object(player, '/org/mpris/MediaPlayer2')
            props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
            meta = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
            pos = props.Get('org.mpris.MediaPlayer2.Player', 'Position')
            
            status = str(props.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
            self.btn_play.setText("⏸" if status == "Playing" else "▶")
            
            title = str(meta.get('xesam:title', 'Bilinmiyor'))
            artist = str(meta.get('xesam:artist', ['Bilinmiyor'])[0])
            album = str(meta.get('xesam:album', 'Bilinmiyor'))
            length = meta.get('mpris:length', 0)
            
            self.handle_text_and_time(title, artist, album, pos, length)
            
            art_url = str(meta.get('mpris:artUrl', ''))
            if art_url and self.last_art != art_url:
                self.last_art = art_url
                if art_url.startswith("file://"):
                    pixmap = QPixmap(art_url.replace("file://", ""))
                    self.art_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.manager.get(QNetworkRequest(QUrl(art_url)))
        except: pass

    def update_windows(self):
        try:
            async def get_media_info():
                sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
                current_session = sessions.get_current_session()
                if not current_session: return None
                
                info = await current_session.try_get_media_properties_async()
                timeline = current_session.get_timeline_properties()
                info_status = current_session.get_playback_info()
                
                thumb_pixmap = None
                if info.thumbnail:
                    stream = await info.thumbnail.open_read_async()
                    reader = DataReader(stream.get_input_streamAt(0))
                    await reader.load_async(stream.size)
                    buffer = reader.read_buffer(stream.size)
                    
                    import ctypes
                    from winrt._winrt import DataWriter
                    writer = DataWriter()
                    writer.write_buffer(buffer)
                    
                    data = bytearray(stream.size)
                    reader.seek(0)
                    reader.read_bytes(data)
                    thumb_pixmap = QPixmap()
                    thumb_pixmap.loadFromData(data)

                return {
                    "title": info.title,
                    "artist": info.artist,
                    "album": info.album_title,
                    "status": info_status.playback_status,
                    "pos": timeline.position.total_seconds() * 1000000,
                    "length": timeline.end_time.total_seconds() * 1000000,
                    "pixmap": thumb_pixmap
                }

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(get_media_info())
            loop.close()

            if res:
                self.btn_play.setText("⏸" if res["status"] == 4 else "▶")
                self.handle_text_and_time(res["title"], res["artist"], res["album"], res["pos"], res["length"])
                if res["pixmap"]:
                    self.art_label.setPixmap(res["pixmap"].scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            pass

    def handle_text_and_time(self, title, artist, album, pos, length):
        if title != self.current_title:
            self.current_title = title
            self.scroll_text = title + "        "

        if len(title) > 16:
            self.scroll_text = self.scroll_text[1:] + self.scroll_text[0]
            self.title_label.setText(self.scroll_text)
        else:
            self.title_label.setText(title)
        
        self.info_label.setText(f"{artist} - {album}")
        self.time_label.setText(f"{self.format_time(pos)} / {self.format_time(length)}")
        if length > 0: 
            self.progress_bar.setValue(int((pos / length) * 100))

    def format_time(self, ms):
        return f"{int((ms / 60000000) % 60):02}:{int((ms / 1000000) % 60):02}"

    def send_cmd(self, cmd):
        if SYSTEM == "Linux":
            player = self.get_player_bus()
            if player:
                try:
                    bus = dbus.SessionBus()
                    proxy = bus.get_object(player, '/org/mpris/MediaPlayer2')
                    getattr(dbus.Interface(proxy, 'org.mpris.MediaPlayer2.Player'), cmd)()
                except: pass
        elif SYSTEM == "Windows":
            try:
                async def send_windows_cmd():
                    sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
                    current_session = sessions.get_current_session()
                    if current_session:
                        if cmd == "PlayPause": await current_session.try_toggle_play_pause_async()
                        elif cmd == "Next": await current_session.try_skip_next_async()
                        elif cmd == "Previous": await current_session.try_skip_previous_async()
                loop = asyncio.new_event_loop()
                loop.run_until_complete(send_windows_cmd())
                loop.close()
            except: pass

    def on_image_downloaded(self, reply):
        if reply.error() == QNetworkReply.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.art_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MediaHUD()
    win.show()
    sys.exit(app.exec_())
