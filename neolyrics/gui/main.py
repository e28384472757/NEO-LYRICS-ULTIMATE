"""PySide6 graphical frontend."""
from __future__ import annotations
import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, QUrl
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QLinearGradient, QPixmap, QPen, QPolygon
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QProgressBar, QPushButton, QSizePolicy)
from neolyrics.core.engine import LyricsEngine
from neolyrics.core.animation import format_time

class GothicBackdrop(QWidget):
    """Vector-drawn moonlit backdrop; no low-resolution text-art rasterization."""
    def __init__(self, parent=None):
        super().__init__(parent)
        art = Path(__file__).resolve().parents[1] / "assets" / "anime_background.png"
        self.background = QPixmap(str(art)) if art.exists() else QPixmap()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        g = QLinearGradient(0, 0, r.width(), r.height()); g.setColorAt(0, QColor("#07050d")); g.setColorAt(.5, QColor("#17102c")); g.setColorAt(1, QColor("#05040b"))
        p.fillRect(r, g)
        if not self.background.isNull():
            p.setOpacity(0.42)
            p.drawPixmap(r, self.background)
            p.setOpacity(1.0)
        moon = QRadialGradient(r.width()*.69, r.height()*.28, min(r.width(),r.height())*.34)
        moon.setColorAt(0, QColor(198,158,255,105)); moon.setColorAt(.48,QColor(119,70,190,45)); moon.setColorAt(1,QColor(10,5,20,0))
        p.fillRect(r, moon)
        p.setPen(QPen(QColor(171,105,255,48), 2))
        p.drawEllipse(QRectF(r.width()*.55, r.height()*.02, r.height()*.54, r.height()*.54))
        p.setPen(QPen(QColor(190,130,255,65), 1))
        for inset in (12, 20, 28): p.drawRoundedRect(r.adjusted(inset,inset,-inset,-inset), 14, 14)
        # Cathedral-like silhouettes on the horizon
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(5,3,12,180))
        base = r.height()*.78
        for x,w,h in [(r.width()*.77,45,.42),(r.width()*.84,70,.57),(r.width()*.92,48,.38),(r.width()*.63,38,.29)]:
            p.drawRect(int(x),int(base-h*r.height()),int(w),int(h*r.height()))
            p.drawPolygon(QPolygon([QPoint(int(x-8),int(base-h*r.height())), QPoint(int(x+w/2),int(base-h*r.height()-28)), QPoint(int(x+w+8),int(base-h*r.height()))]))
        p.end()

class LyricsWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.engine = LyricsEngine(); self.last_art = ""
        self.setWindowTitle("NEO-LYRICS ULTIMATE — SHADOW EMPEROR")
        self.resize(1440, 900); self.setMinimumSize(920, 620)
        self.backdrop = GothicBackdrop(); self.setCentralWidget(self.backdrop); self.network = QNetworkAccessManager(self); self.eq_phase = 0
        root = QHBoxLayout(self.backdrop); root.setContentsMargins(34,30,34,28); root.setSpacing(28)
        left = QFrame(); left.setObjectName("sidePanel"); left.setFixedWidth(330)
        lv = QVBoxLayout(left); lv.setContentsMargins(22,22,22,22); lv.setSpacing(12)
        self.cover = QLabel("✦\nSPOTIFY\nWAITING ✦"); self.cover.setObjectName("cover"); self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter); self.cover.setMinimumHeight(290)
        self.title = QLabel("Esperando a Spotify…"); self.title.setObjectName("trackTitle"); self.title.setWordWrap(True)
        self.artist = QLabel("Abre Spotify y reproduce una canción"); self.artist.setObjectName("artist")
        self.album = QLabel("NEO-LYRICS · SHADOW EMPEROR"); self.album.setObjectName("muted")
        self.time = QLabel("00:00 / 00:00"); self.time.setObjectName("muted")
        self.progress = QProgressBar(); self.progress.setTextVisible(False); self.progress.setFixedHeight(9); self.progress.setRange(0,1000)
        controls = QHBoxLayout()
        self.prev = QPushButton("◀◀"); self.toggle = QPushButton("Ⅱ"); self.next = QPushButton("▶▶")
        for b in (self.prev,self.toggle,self.next): b.setObjectName("control"); b.setMinimumHeight(44)
        self.prev.clicked.connect(self.engine.spotify.previous); self.toggle.clicked.connect(self.engine.spotify.play_pause); self.next.clicked.connect(self.engine.spotify.next)
        controls.addWidget(self.prev); controls.addWidget(self.toggle); controls.addWidget(self.next)
        lv.addWidget(self.cover,1); lv.addWidget(self.title); lv.addWidget(self.artist); lv.addWidget(self.album); lv.addWidget(self.time); lv.addWidget(self.progress); lv.addLayout(controls)
        right = QVBoxLayout(); right.setSpacing(18)
        header = QHBoxLayout(); brand = QLabel("✦  N E O  —  L Y R I C S  U L T I M A T E"); brand.setObjectName("brand")
        self.connection = QLabel("●  ESPERANDO SPOTIFY"); self.connection.setObjectName("status")
        header.addWidget(brand); header.addStretch(1); header.addWidget(self.connection); right.addLayout(header)
        right.addStretch(2)
        self.lyric = QLabel("La música comienza\ncuando tú presionas play."); self.lyric.setObjectName("lyric"); self.lyric.setAlignment(Qt.AlignmentFlag.AlignCenter); self.lyric.setWordWrap(True); self.lyric.setMinimumHeight(170)
        self.lyric.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.sub = QLabel("◈  SHADOW SYNC  ◈"); self.sub.setObjectName("subline"); self.sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(self.lyric); right.addWidget(self.sub); right.addStretch(2)
        self.eq = QLabel("▂ ▄ ▆ ▃ ▇ ▅ ▂ ▄ ▆ ▇ ▃ ▅ ▂ ▆ ▄ ▇ ▃ ▂ ▅ ▆ ▄ ▃ ▇ ▅ ▂"); self.eq.setObjectName("equalizer"); self.eq.setAlignment(Qt.AlignmentFlag.AlignCenter); right.addWidget(self.eq)
        footer = QLabel("LRCLIB  ·  MPRIS / PLAYERCTL  ·  TYPEWRITER SYNC"); footer.setObjectName("muted"); footer.setAlignment(Qt.AlignmentFlag.AlignCenter); right.addWidget(footer)
        root.addWidget(left); root.addLayout(right,1)
        self.setStyleSheet("""
        QWidget { color:#f2eaff; font-family:'Noto Sans','DejaVu Sans'; }
        QFrame#sidePanel { background:rgba(7,5,15,218); border:1px solid #8748d8; border-radius:18px; }
        QLabel#cover { background:qradialgradient(cx:.5,cy:.4,r:.8,stop:0 #39215a,stop:1 #090610); border:1px solid #a66aff; border-radius:12px; color:#d8baff; font-size:26px; font-weight:700; }
        QLabel#trackTitle { color:#fff; font-size:23px; font-weight:800; }
        QLabel#artist { color:#c78cff; font-size:17px; } QLabel#muted { color:#a99bbd; font-size:12px; }
        QLabel#brand { color:#d8b2ff; font-size:20px; font-weight:800; letter-spacing:2px; }
        QLabel#status { color:#a9f5c4; font-size:13px; font-weight:700; padding:10px 15px; background:rgba(5,30,20,150); border:1px solid #397f61; border-radius:12px; }
        QLabel#lyric { color:#f7efff; font-family:'Noto Serif','DejaVu Serif'; font-size:38px; font-weight:800; padding:30px; }
        QLabel#subline { color:#b77aff; font-size:14px; letter-spacing:4px; }
        QLabel#equalizer { color:#a35cff; font-size:28px; letter-spacing:4px; }
        QProgressBar { background:#21152f; border:0; border-radius:4px; } QProgressBar::chunk { background:#a44cff; border-radius:4px; }
        QPushButton#control { color:#d8b2ff; background:#1a1027; border:1px solid #8a4acb; border-radius:12px; font-size:18px; }
        QPushButton#control:hover { background:#4a2470; }
        """)
        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(350)
        self.refresh()

    def refresh(self):
        s = self.engine.tick(); t = s.track
        self.eq_phase += 1
        levels = "▁▂▃▄▅▆▇█"
        self.eq.setText(" ".join(levels[(i*3+self.eq_phase*(i%4+1))%len(levels)] for i in range(27)))
        if not t:
            self.connection.setText("●  SPOTIFY CONECTADO · EN ESPERA" if s.connected else "●  SPOTIFY DESCONECTADO / EN ESPERA")
            self.title.setText("Esperando a Spotify…"); self.artist.setText("Abre Spotify y reproduce una canción")
            self.album.setText("NEO-LYRICS · SHADOW EMPEROR"); self.lyric.setText("La música comienza\ncuando tú presionas play.")
            self.time.setText("00:00 / 00:00"); self.progress.setValue(0); self.toggle.setText("Ⅱ"); return
        self.connection.setText("●  SPOTIFY CONECTADO  ·  " + ("REPRODUCIENDO" if s.status=="Playing" else "EN PAUSA"))
        self.title.setText(t.title); self.artist.setText(t.artist); self.album.setText(t.album or "Álbum desconocido")
        self.time.setText(f"{format_time(s.position)} / {format_time(t.duration)}")
        self.progress.setValue(int((s.position/t.duration)*1000) if t.duration else 0)
        self.toggle.setText("Ⅱ" if s.status=="Playing" else "▶")
        if s.lyrics_loading: self.lyric.setText("Buscando letras sincronizadas…")
        elif not s.lyrics: self.lyric.setText(s.message or "No hay letras disponibles.")
        elif s.frame and s.frame.index < 0: self.lyric.setText("✧ La canción está por comenzar ✧")
        elif s.frame: self.lyric.setText(s.frame.visible or "·")
        if t.art_url != self.last_art:
            self.last_art=t.art_url
            self.cover.clear(); self.cover.setText("✦\nNEO-LYRICS\nSHADOW ✦")
            from urllib.parse import unquote
            path = unquote(t.art_url.removeprefix("file://"))
            if path and os.path.isfile(path):
                pix=QPixmap(path)
                if not pix.isNull(): self.cover.setPixmap(pix.scaled(self.cover.size(),Qt.AspectRatioMode.KeepAspectRatioByExpanding,Qt.TransformationMode.SmoothTransformation))
            elif t.art_url.startswith(("https://", "http://")):
                reply = self.network.get(QNetworkRequest(QUrl(t.art_url)))
                reply.finished.connect(lambda r=reply, expected=t.art_url: self._art_loaded(r, expected))

    def _art_loaded(self, reply, expected_url):
        try:
            pix = QPixmap(); pix.loadFromData(reply.readAll())
            if expected_url == self.last_art and not pix.isNull(): self.cover.setPixmap(pix.scaled(self.cover.size(),Qt.AspectRatioMode.KeepAspectRatioByExpanding,Qt.TransformationMode.SmoothTransformation))
        finally: reply.deleteLater()

    def closeEvent(self,event): self.timer.stop(); self.engine.close(); super().closeEvent(event)

def main():
    app=QApplication.instance() or QApplication([]); w=LyricsWindow(); w.showMaximized(); return app.exec()
