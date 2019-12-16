from flask_restful import Resource
from flask import request

from validator.ExecuteDataVaildator import ExecuteDataVaildator

from CodeRunner.Executer import Executer
from CodeRunner.CodeRunner import LanguageNotSupportedError
from config import version

class Execute(Resource):
    '''
    @route /api/execute
    @desc API endpoint for executing.
    '''
    def get(self):
        '''
        @desc Just a dummy for checking if the endpoint works.
        @access public
        @return Version of the compiler
        '''
        return {'message': ' '.join(('Executer' , 'version:' , version))}
    
    def post(self):
        '''
        @desc execute the given code in the specified language with the given input
        @access public
        @return exitCode, stdout, stderr, warnings and timeTaken
        '''
        executeData = request.get_json()

        # Validate execute data
        isValid , errors = ExecuteDataVaildator().validateExecuteData(executeData)
        if not isValid:
            return errors

        #Initialize output
        compilationOutput = {
            'exitCode': 0,
            'stderr': ''
        }

        # Initialize compiler
        try:
            executer = Executer(executeData['language'])
        except LanguageNotSupportedError:
            compilationOutput['exitCode'] = 404
            compilationOutput['stderr'] = 'Language not found'
            return compilationOutput
        except:
            compilationOutput['exitCode'] = 500
            compilationOutput['stderr'] = 'Internal server error'
            return compilationOutput
        
        #Initialize docker container
        initializationSuccessful = executer.initializeDockerContainer()
        if not initializationSuccessful:
            compilationOutput['exitCode'] = 500
            compilationOutput['stderr'] = 'Internal server error'
            return compilationOutput
        
        #Compile the code
        compilationOutput = executer.compile(executeData['code'])
        if compilationOutput['exitCode'] == 1:
            return {
                'exitCode': 1,
                'stderr': 'Compilation error',
                'warnings': '',
                'stdout': '',
                'compilationOutput': compilationOutput
            }

        #Execute the code for the input.
        executionOutput = executer.execute(executeData['input'] , executeData['timeout'])

        executionOutput['compilationOutput'] = compilationOutput

        return executionOutput
        