import os
from CodeRunner.Compiler import Compiler
from CodeRunner.languages.Config import *
from CodeRunner.TarDataGenerator import TarDataGenerator

import time

class Executer(Compiler):
    '''
    Executer class is used to execute the given code with the given output 
    '''
    def __init__(self , language):
        super().__init__(language)
    
    def execute(self , inputData='' , timeout=2):
        '''
        Execute the given code which has been compiled.

        @param string inputData - The inputData for the compiled code.
        @param int timeout - Time limit for the execution process.
        @return dict - returns the exitCode , stdout , stderr , 
                        warnings and timeTaken for the execution.
        '''
        if not self.compilationSuccessful:
            return {
                'exitCode': 404,
                'stdout': '',
                'stderr': 'Nothing to execute. Compile the code first.'
            }
        
        self.__addInputToContainer(inputData)

        executeCommand = ['timeout' , str(timeout) , 'sh' , 'execute.sh' , '-k']

        startTime = time.time()
        exitCode , output = self.dockerContainer.exec_run(
            executeCommand,
            stdout=True,
            stderr=True,
            demux=True
        )
        endTime = time.time()
        
        stdout , stderr = output
        if stderr:
            stderr = stderr.decode()
        if stdout:
            stdout = stdout.decode()

        warnings = ''
        if exitCode == 0 and stderr:
            warnings = stderr
            stderr = ''
        # Check for time out
        if exitCode == 124:
            stderr = 'Time Limit Exceeded'

        return {
            'exitCode': exitCode,
            'stdout': stdout,
            'stderr': stderr,
            'warnings': warnings,
            'timeTaken': endTime - startTime
        }

    def __addInputToContainer(self , inputData):
        self.dockerContainer.put_archive(
            SRC_CONTAINER_PATH , 
            TarDataGenerator((INPUT_FILE_NAME , inputData)).getBytes()
            )

    def __del__(self):
        super().__del__()