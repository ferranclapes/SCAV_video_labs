import ffmpeg
import numpy as np
from PIL import Image
import os

class traslator:
    def rgb_to_yuv(r, g, b):                            #Use the formulas to convert RGB to YUV
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.14713 * r - 0.28886 * g + 0.436 * b
        v = 0.615 * r - 0.51499 * g - 0.10001 * b
        return y, u, v
    
    def yuv_to_rgb(y, u, v):                           #Use the formulas to convert YUV to RGB
        r = y + 1.13983 * v
        g = y - 0.39465 * u - 0.58060 * v
        b = y + 2.03211 * u
        return r, g, b


def resize_image(input_image, output_image, width = -1, height = -1):   #Resize image using ffmpeg
    stream = ffmpeg.input(input_image)
    stream = ffmpeg.filter(stream, 'scale', width, height)
    stream = ffmpeg.output(stream, output_image)
    ffmpeg.run(stream)


def serpentine(input_image):
    with Image.open(input_image) as img:
        pixels = np.array(img)
        height, width = pixels.shape[:2]

        output_pixels = np.zeros((height*width,3))

        total_diagonals = height-1 + width-1

        for diag in range(total_diagonals + 1):
            if diag % 2 == 0:       #if the diagonal is even, go from bottom to top until the end of the diagonal
                for x in range(diag + 1):
                    y = diag - x
                    if (x < width and y < height) and (x >= 0 and y >= 0):
                        output_pixels[diag+x] = pixels[y, x] #put the pixel in the correct order in the output array
            else:                   #if the diagonal is odd, go from top to bottom until the end of the diagonal
                for x in range(diag + 1):
                    y = diag - x
                    if (x < width and y < height) and (x >= 0 and y >= 0):
                        output_pixels[diag+x] = pixels[y, x] #put the pixel in the correct order in the output array

        return output_pixels
    
def run_length_encoding(byte_stream):
    encoded_stream = []
    for i in range(len(byte_stream)):
        count = 1
        while i + count < len(byte_stream) and byte_stream[i] == byte_stream[i + count]:
            count += 1
        encoded_stream.append((byte_stream[i], count))
    return encoded_stream

def to_black_white(input_image):
    stream = ffmpeg.input(input_image)
    stream = ffmpeg.filter(stream, 'format', 'gray')
    output_image = 'bw_' + input_image
    stream = ffmpeg.output(stream, output_image)
    ffmpeg.run(stream)
