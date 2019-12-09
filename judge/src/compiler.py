from config import basedir
import os
from dockerfiles.LanguageConfig import LANGUAGES , MAIN_FILE_NAME

import docker
import time

class Compiler:
    '''
    Compiler class is used to compile the given code and returns it's output/error.
    '''
    def __init__(self , language , timeout=5):
        if language not in LANGUAGES:
            raise LanguageNotSupportedError(language)

        self.language = language
        self.timeout = timeout
        self.dockerfilePath = os.path.join(basedir , 'dockerfiles' , language)
        self.dockerClient = docker.from_env()
        self.tag = '-'.join((self.language , str(int(time.time()*10000))))

    def compile(self):
        '''
        Compiles the code and returns the exitCode, errorMessage and warningMessage.
        '''
        compilationCommand = ['timeout' , str(self.timeout) , 'sh' , 'compile.sh' , '-k']
        exitCode , output = self.dockerContainer.exec_run(
            compilationCommand,
            stdout=True,
            stderr=True,
            demux=True
        )
        stdout , stderr = output
        if stderr:
            stderr = stderr.decode()
        warningMessage = ''
        if exitCode == 0 and stderr:
            warningMessage = stderr
            stderr = ''
        # Check for time out
        if exitCode == 124:
            stderr = 'Compilation timeout'
        return {
            'exitCode': exitCode,
            'errorMessage': stderr,
            'warningMessage': warningMessage
        }

    def intializeDockerContainer(self , code):
        self.saveCodeToFile(code)
        buildSuccessful , dockerImage = self.buildImage()
        if not buildSuccessful:
            return False
        runSuccessful , self.dockerContainer = self.runContainer(dockerImage)
        if not runSuccessful:
            return False

        return True
    
    def saveCodeToFile(self , code):
        fileName = '.'.join((MAIN_FILE_NAME , LANGUAGES[self.language]['extension']))
        filePath = os.path.join(self.dockerfilePath , fileName)

        with open(filePath , 'w') as codeFile:
            codeFile.write(code)
        
    def buildImage(self):
        '''
        Builds an image from the dockerfile mentioned.
        @return (success , image) - 
                        success bool - True if build was successful.
                        image - docker.Image object
        '''
        try:
            image , logs = self.dockerClient.images.build(
                path=self.dockerfilePath , 
                tag=self.tag,
                rm=True,
                forcerm=True,
            )
            return (True , image)
        except:
            return (False , None)

    def runContainer(self , image):
        '''
        Run the given docker image in a container in detatch mode with tty True.
        @return (success , container) - 
                        success bool - True if run was successful.
                        container - docker.Container object
        '''
        try:
            container = self.dockerClient.containers.run(
                image=image,
                detach=True,
                tty=True,
                name=self.tag,
                auto_remove=True,
            )
            return (True , container)
        except docker.errors.ContainerError as err:
            print(err)
            return (False , None)
    
    def __del__(self):
        self.dockerContainer.remove(force=True)
        self.dockerClient.images.remove(self.tag , force=True)

        fileName = '.'.join((MAIN_FILE_NAME , LANGUAGES[self.language]['extension']))
        filePath = os.path.join(self.dockerfilePath , fileName)
        os.remove(filePath)


class CompilerError(Exception):
    '''
    Base class for compiler exceptions.
    '''
    def __init__(self , errorMessage):
        Exception.__init__(self , errorMessage)

class LanguageNotSupportedError(CompilerError):
    def __init__(self , language):
        CompilerError.__init__(self , 'This language is not supported: {}'.format(language))

