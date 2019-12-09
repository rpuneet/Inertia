from flask_restful import Resource
from flask import request

from src.compiler import Compiler , LanguageNotSupportedError

from validator.CompileDataValidator import CompileDataVaildator

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
        @return exitCode, errorMessage and warningMessage (if any)
        '''
        compileData = request.get_json()

        # Validate compile data
        isValid , errors = CompileDataVaildator().validateCompileData(compileData)
        if not isValid:
            return errors

        #Initialize output
        compilationOutput = {
            'exitCode': 0,
            'errorMessage': ''
        }
        # Initialize compiler
        try:
            compiler = Compiler(compileData['language'] , compileData['timeout'])
        except LanguageNotSupportedError:
            compilationOutput['exitCode'] = 404
            compilationOutput['errorMessage'] = 'The language is not supported'
            return compilationOutput
        except:
            compilationOutput['exitCode'] = 500
            compilationOutput['errorMessage'] = 'Internal server error'
            return compilationOutput
        
        #Initialize docker container
        initializationSuccessful = compiler.intializeDockerContainer(compileData['code'])
        if not initializationSuccessful:
            compilationOutput['exitCode'] = 500
            compilationOutput['errorMessage'] = 'Internal server error'
            return compilationOutput
        
        #Compile the code
        compilationOutput = compiler.compile()

        return compilationOutput

        