import sys
import os

# Añadir el directorio actual al path para facilitar importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import App

def main():
    # Manejo de argumentos para Menú Contextual
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf2word", type=str, help="Convertir PDF a Word vía CLI")
    parser.add_argument("--word2pdf", type=str, help="Convertir Word a PDF vía CLI")
    args, unknown = parser.parse_known_args()

    app = App()

    # Si se recibe un archivo por argumento, procesarlo inmediatamente
    if args.pdf2word:
        app.after(1000, lambda: app.process_selected_file(args.pdf2word))
    elif args.word2pdf:
        app.after(1000, lambda: app.process_selected_file(args.word2pdf))

    app.mainloop()

if __name__ == "__main__":
    main()
