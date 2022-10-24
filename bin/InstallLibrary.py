from pip._internal import main

libraries = ['pillow', 'matplotlib', 'opencv-python']


def install_libraries():
    global libraries
    for item in libraries:
        main(['install', item])
