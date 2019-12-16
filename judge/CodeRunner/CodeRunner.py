import os
from CodeRunner.languages.Config import *

import docker
import time

__all__ = ['CodeRunner' , 'LanguageNotSupportedError']

class CodeRunner:
    '''
    CodeRunner is the base class used for initializing a Docker container for compiling and executing.
    '''
    def __init__(self , language):
        if language not in LANGUAGES:
            raise LanguageNotSupportedError(language)

        self.language = language
        self.dockerfilePath = os.path.join(BASE_DIR , language)
        self.dockerClient = docker.from_env()
        self.tag = '-'.join((self.language , str(int(time.time()))))

    def initializeDockerContainer(self):
        '''
        Initialize the docker image and container.
        @return bool - If initialization was successful or not.
        '''
        buildSuccessful , dockerImage = self.__buildImage()
        if not buildSuccessful:
            return False

        runSuccessful , self.dockerContainer = self.__runContainer(dockerImage)
        if not runSuccessful:
            return False

        return True
        
    def __buildImage(self):
        '''
        Builds an image from the dockerfile according to the language.
        if image already exists, returns the image.
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
        except docker.errors.BuildError as err:
            return (False , None)

    def __runContainer(self , image):
        '''
        Run the given docker image in a container in detatch mode with tty True.
        Attaches the directory src in the language directory.
        if container already exists, returns the container.
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
                    os.path.join(self.dockerfilePath , CONTAINER_VOLUME_DIR_NAME) : {
                        'bind': os.path.join('/' , 'judge' , CONTAINER_VOLUME_DIR_NAME),
                        'mode': 'rw'
                    }
                }
            )
            return (True , container)
        except docker.errors.ContainerError as err:
            return (False , None)


class CodeRunnerError(Exception):
    '''
    Base class for CodeRunner exceptions.
    '''
    def __init__(self , errorMessage):
        Exception.__init__(self , errorMessage)

class LanguageNotSupportedError(CodeRunnerError):
    def __init__(self , language):
        CodeRunnerError.__init__(self , 'This language is not supported: {}'.format(language))

