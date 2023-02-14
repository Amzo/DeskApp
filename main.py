import sys
from GUI import Main
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = Main.App()
    player.showMaximized()
    sys.exit(app.exec_())