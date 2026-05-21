import sys
import os

# Añadir el directorio actual al path para facilitar importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import App

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
