#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
import subprocess
import os.path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from mpd import MPDClient
from mutagen import File as Mutagen_file
from mutagen import mp3 as Mutagen_mp3

global app, label, mpdClient, dim, libPath, defaultImage

def getCoverPath(songPath):
    songDir = os.path.dirname(songPath)
    candidates = ['Folder.jpg', 'Folder.png']
    for candidate in candidates:
        path = songDir + '/' + candidate
        if os.path.isfile(path):
            return path
    return None

def initMPDClient(socket):
    global mpdClient
    mpdClient = MPDClient()
    mpdClient.timeout = 10
    mpdClient.connect(socket, 0)

def quit():
    sys.exit(app.exec_())

def initWindow():
    global label
    w = QWidget()
    w.setWindowTitle('Artwork Display')
    w.setAttribute(Qt.WA_TranslucentBackground)
    QShortcut(QKeySequence('q'), w, quit)

    label = QLabel()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.Alignment(Qt.AlignHCenter))
    w.setLayout(layout)
    layout.addWidget(label)
    updateLabel()

    return w

def displayArt(pixmap):
    pixmap = pixmap.scaled(dim, dim, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    label.setPixmap(pixmap)

def updateLabel():
    songPath = libPath + '/' + mpdClient.currentsong()['file']
    coverPath = getCoverPath(songPath)
    # Prioritize path in folder
    if coverPath != None:
        pixmap = QPixmap(coverPath)
        displayArt(pixmap)
        return
    # Try finding ID3 attached
    try:
        apic = Mutagen_file(songPath).tags.get('APIC:')
    except Mutagen_mp3.HeaderNotFoundError as e:
        displayArt(QPixmap())
        return
    if apic != None:
        artwork = apic.data # access APIC frame and grab the image
        pixmap = QPixmap()
        pixmap.loadFromData(artwork)
        displayArt(pixmap)
        return
    displayArt(QPixmap())

def main():
    global label, dim, libPath, app, defaultImage

    mpdSocket = sys.argv[1]
    libPath = sys.argv[2]
    dim = int(sys.argv[3])
    defaultImage = sys.argv[4]
    if len(sys.argv) >= 6:
        interval = int(sys.argv[5])
    else:
        interval = 1000

    app = QApplication(sys.argv)
    initMPDClient(mpdSocket)
    w = initWindow()

    # Refresh artwork every second
    t = QTimer()
    t.setInterval(interval)
    t.timeout.connect(updateLabel)
    t.start()

    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
