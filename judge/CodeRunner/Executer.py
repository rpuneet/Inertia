import os
from CodeRunner.Compiler import Compiler
from CodeRunner.languages.Config import INPUT_FILE_NAME

import time

class Executer(Compiler):
    '''
    Executer class is used to execute the given code with the given output 
    '''
    def __init__(self , language):
        super().__init__(language)
    
    def execute(self , input='' , timeout=2):
        '''
        Execute the given code which has been compiled.

        @param string input - The input for the compiled code.
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
        
        self.__saveInputToVolume(input)

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

    def __saveInputToVolume(self , input):
        filePath = os.path.join(self.dockerVolumePath , INPUT_FILE_NAME)

        with open(filePath , 'w') as inputFile:
            inputFile.write(input)

    def __deleteInputFromVolume(self):
        filePath = os.path.join(self.dockerVolumePath , INPUT_FILE_NAME)
        os.remove(filePath)

    def __del__(self):
        if self.compilationSuccessful:
            self.__deleteInputFromVolume()
        super().__del__()