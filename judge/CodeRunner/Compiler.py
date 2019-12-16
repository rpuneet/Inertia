from CodeRunner import CodeRunner
from languages.Config import *

import os

class Compiler(CodeRunner):
    '''
    Compiler class is used to compile the code.
    '''
    def __init__(self , language):
        super().__init__(language)
        self.compilationSuccessful = False
        self.dockerVolumePath = os.path.join(self.dockerfilePath , CONTAINER_VOLUME_DIR_NAME)

    def compile(self , code , timeout=5):
        '''
        Compiles the code and returns the exitCode, errorMessage and warnings.
        '''
        self.compilationSuccessful = False
        self.__saveCodeToVolume(code)

        compilationCommand = ['timeout' , str(timeout) , 'sh' , 'compile.sh' , '-k']
        exitCode , output = self.dockerContainer.exec_run(
            compilationCommand,
            stdout=True,
            stderr=True,
            demux=True
        )
        stdout , stderr = output
        if stderr:
            stderr = stderr.decode()

        warnings = ''
        if exitCode == 0 and stderr:
            warnings = stderr
            stderr = ''
        # Check for time out
        if exitCode == 124:
            stderr = 'Compilation timeout'
        
        if exitCode == 0:
            self.compilationSuccessful = True
        return {
            'exitCode': exitCode,
            'stderr': stderr,
            'warnings': warnings
        }

    def __saveCodeToVolume(self , code):
        fileName = '.'.join((MAIN_FILE_NAME , LANGUAGES[self.language]['extension']))
        filePath = os.path.join(self.dockerVolumePath , fileName)

        with open(filePath , 'w') as codeFile:
            codeFile.write(code)
    def __deleteCodeFromVolume(self):
        fileName = '.'.join((MAIN_FILE_NAME , LANGUAGES[self.language]['extension']))
        filePath = os.path.join(self.dockerVolumePath , fileName)
        os.remove(filePath)

    def __del__(self):
        self.__deleteCodeFromVolume()