from flask_restful import Resource
from flask import request

from validator.CompileDataValidator import CompileDataVaildator
from CodeRunner.Compiler import Compiler
from CodeRunner.CodeRunner import LanguageNotSupportedError
from config import version

class Compile(Resource):
    '''
    @route /api/compile
    @desc API endpoint for compiling.
    '''
    def get(self):
        '''
        @desc Just a dummy for checking if the endpoint works.
        @access public
        @return Version of the compiler
        '''
        return {'message': ' '.join(('Compiler' , 'version:' , version))}
    
    def post(self):
        '''
        @desc compile the given code in the specified language
        @access public
        @return exitCode, stderr and warnings
        '''
        compileData = request.get_json()

        # Validate compile data
        isValid , errors = CompileDataVaildator().validateCompileData(compileData)
        if not isValid:
            return errors

        #Initialize output
        compilationOutput = {
            'exitCode': 0,
            'stderr': ''
        }

        # Initialize compiler
        try:
            compiler = Compiler(compileData['language'])
        except LanguageNotSupportedError:
            compilationOutput['exitCode'] = 404
            compilationOutput['stderr'] = 'Language not found'
            return compilationOutput
        except:
            compilationOutput['exitCode'] = 500
            compilationOutput['stderr'] = 'Internal server error'
            return compilationOutput
        
        #Initialize docker container
        initializationSuccessful = compiler.initializeDockerContainer()
        if not initializationSuccessful:
            compilationOutput['exitCode'] = 500
            compilationOutput['stderr'] = 'Internal server error'
            return compilationOutput
        
        #Compile the code
        compilationOutput = compiler.compile(compileData['code'])

        return compilationOutput

        