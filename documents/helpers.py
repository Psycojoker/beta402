import struct
import imghdr
from os.path import join
from www import settings


def document_pdir(document):
    return join(settings.PROCESSING_DIR, "doc-{}".format(document.id))


def r(self):
    return 60 * (1 + self.request.retries * 2)


def get_image_size(filename):
    '''Determine the image type of fhandle and return its size.'''

    fhandle = open(filename, 'rb')
    head = fhandle.read(24)
    if len(head) != 24:
        raise ValueError('{} is less than 24 bytes, cannot be a valid image.'.format(filename))
    if imghdr.what(filename) == 'png':
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
            raise ValueError('{} is not a valid png file.'.format(filename))
        width, height = struct.unpack('>ii', head[16:24])
    elif imghdr.what(filename) == 'gif':
        width, height = struct.unpack('<HH', head[6:10])
    elif imghdr.what(filename) == 'jpeg':
        try:
            fhandle.seek(0)  # Read 0xff next
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf:
                fhandle.seek(size, 1)
                byte = fhandle.read(1)
                while ord(byte) == 0xff:
                    byte = fhandle.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', fhandle.read(2))[0] - 2
            # We are at a SOFn block
            fhandle.seek(1, 1)  # Skip `precision' byte.
            height, width = struct.unpack('>HH', fhandle.read(4))
        except:
            raise ValueError('{} is not a valid jpeg file.'.format(filename))
    else:
        raise ValueError('{} must be a jpeg, gif or png image.'.format(filename))
    return width, height
