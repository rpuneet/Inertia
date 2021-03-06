from CodeRunner.CodeRunner import CodeRunner
from CodeRunner.languages.Config import *
from CodeRunner.TarDataGenerator import TarDataGenerator
import os

class Compiler(CodeRunner):
    '''
    Compiler class is used to compile the code. It is the base class for Executer.
    '''
    def __init__(self , language):
        super().__init__(language)
        self.compilationSuccessful = False
        # self.dockerVolumePath = os.path.join(self.dockerfilePath , CONTAINER_VOLUME_DIR_NAME)

    def compile(self , code , timeout=5):
        '''
        Compiles the given code.
        @param string code - The code to compile.
        @param int timeout - time limit for the compilation process.
        @return dict - returns the exitCode, stderr and warnings.
        '''
        self.compilationSuccessful = False
        
        self.__addCodeToContainer(code)

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
            stderr = 'Compilation timed out'
        
        if exitCode == 0:
            self.compilationSuccessful = True

        return {
            'exitCode': exitCode,
            'stderr': stderr,
            'warnings': warnings
        }

    def __addCodeToContainer(self , code):
        fileName = '.'.join((MAIN_FILE_NAME , LANGUAGES[self.language]['extension']))
        self.dockerContainer.put_archive(
            SRC_CONTAINER_PATH , 
            TarDataGenerator((fileName , code)).getBytes()
            )
            
    def __del__(self):
        super().__del__()