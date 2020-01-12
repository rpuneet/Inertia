import tarfile
from io import BytesIO
import time


class TarDataGenerator:
    def __init__(self , *data):
        self.pw_tarstream = BytesIO()

        self.pw_tar = tarfile.TarFile(fileobj=self.pw_tarstream, mode='w')

        for filename , filedata in data:
            self.__addToTarArchive(filename , filedata)

        self.pw_tar.close()

    def __addToTarArchive(self , filename , filedata):
        filedata = filedata.encode('utf8')

        tarinfo = tarfile.TarInfo(name=filename)
        tarinfo.size = len(filedata)
        tarinfo.mtime = time.time()

        self.pw_tar.addfile(tarinfo, BytesIO(filedata))

    def getBytes(self):
        self.pw_tarstream.seek(0)
        return self.pw_tarstream
