import sys

from snakesheets.ui.app import App


def main():
    app = App()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
