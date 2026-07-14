import sys
from .gui.app import App

def main():
    app = App()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
        sys.exit(0)

if __name__ == "__main__":
    main()
