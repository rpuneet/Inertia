import os

__all__ = ['LANGUAGES' , 'SRC_CONTAINER_PATH' , 'MAIN_FILE_NAME' , 'BASE_DIR' , 'INPUT_FILE_NAME']

LANGUAGES = {
    'python3': {
        'name': 'Python 3',
        'version': '3.8.0',
        'compiler': 'Python 3.8.0',
        'extension': 'py',
    },
    'cpp11': {
        'name': 'C++ 11',
        'version': '11',
        'compiler': 'gcc 9.2.0',
        'extension': 'cpp',
    },
    'java': {
        'name': 'Java 13.0.1',
        'version': '13.0.1',
        'compiler': 'jdk 13',
        'extension': 'java',
    }
}
INPUT_FILE_NAME = 'input.txt'
SRC_CONTAINER_PATH = '/judge/src'
MAIN_FILE_NAME = 'Solution'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
