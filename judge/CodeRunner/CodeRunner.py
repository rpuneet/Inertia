import os
from languages.Config import BASE_DIR, LANGUAGES , MAIN_FILE_NAME

import docker
import time

class CodeRunner:
    '''
    CodeRunner is a base class for initializing a Docker container for compiling and executing.
    '''
    def __init__(self , language):
        if language not in LANGUAGES:
            raise LanguageNotSupportedError(language)

        self.language = language
        self.dockerfilePath = os.path.join(BASE_DIR , language)
        self.dockerClient = docker.from_env()
        self.tag = '-'.join((self.language , str(int(time.time()*10000))))

    def intializeDockerContainer(self):
        buildSuccessful , dockerImage = self.buildImage()
        if not buildSuccessful:
            return False
        runSuccessful , self.dockerContainer = self.runContainer(dockerImage)
        if not runSuccessful:
            return False

        return True
        
    def buildImage(self):
        '''
        Builds an image from the dockerfile mentioned.
        @return (success , image) - 
                        success bool - True if build was successful.
                        image - docker.Image object
        '''

        # Check if image already exists.
        for image in self.dockerClient.images.list():
            for tag in image.tags:
                if '-'.join(('compiler' , self.language)) in tag:
                    return (True , image)
        
        try:
            image , logs = self.dockerClient.images.build(
                path=self.dockerfilePath , 
                tag='-'.join(('compiler' , self.tag)),
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
        # Check if container is already running.
        for container in self.dockerClient.containers.list():
            if self.language in container.name:
                return (True , container)
        try:
            container = self.dockerClient.containers.run(
                image=image,
                detach=True,
                tty=True,
                name=self.tag,
                auto_remove=True,
                volumes={
                    os.path.join(self.dockerfilePath , 'src') : {
                        'bind': '/judge/src',
                        'mode': 'rw'
                    }
                }
            )
            return (True , container)
        except docker.errors.ContainerError as err:
            print(err)
            return (False , None)


class CodeRunnerError(Exception):
    '''
    Base class for compiler exceptions.
    '''
    def __init__(self , errorMessage):
        Exception.__init__(self , errorMessage)

class LanguageNotSupported(CodeRunnerError):
    def __init__(self , language):
        CodeRunnerError.__init__(self , 'This language is not supported: {}'.format(language))

