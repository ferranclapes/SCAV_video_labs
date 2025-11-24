import ffmpeg
import numpy as np
from PIL import Image
import os
from scipy.fftpack import dct, idct
import matplotlib.pyplot as plt

class traslator:
    def rgb_to_yuv(self, r, g, b):                            #Use the formulas to convert RGB to YUV
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.14713 * r - 0.28886 * g + 0.436 * b
        v = 0.615 * r - 0.51499 * g - 0.10001 * b
        return y, u, v
    
    def yuv_to_rgb(self, y, u, v):                           #Use the formulas to convert YUV to RGB
        r = y + 1.13983 * v
        g = y - 0.39465 * u - 0.58060 * v
        b = y + 2.03211 * u
        return r, g, b

    def resize_image(self, input_image, output_image, width = -1, height = -1):   #Resize image using ffmpeg
        stream = ffmpeg.input(input_image)
        stream = ffmpeg.filter(stream, 'scale', width, height)
        stream = ffmpeg.output(stream, output_image)
        ffmpeg.run(stream)


    def serpentine(self, input_image):
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
        

    def to_black_white(self, input_image):
        stream = ffmpeg.input(input_image)
        stream = ffmpeg.filter(stream, 'format', 'gray')
        output_image = 'bw_' + input_image
        stream = ffmpeg.output(stream, output_image)
        ffmpeg.run(stream)
        return stream
    
    def run_length_encoding(self, byte_stream):
        encoded_stream = []
        i = 0 
        n = len(byte_stream)
        while i < n:
            count = 1
            while i + 1 < n and byte_stream[i] == byte_stream[i + 1]:
                count += 1
                i += 1 #To move to the next byte till the next byte is different
            encoded_stream.append((byte_stream[i], count))
            i += 1 #Move to the next different byte
        return encoded_stream
        '''
        FAIL VERSION, with the for loop it does not work well.
        encoded_stream = []
        for i in range(len(byte_stream)):
            count = 1
            while i < len(byte_stream) and byte_stream[i] == byte_stream[i + 1]:
                count += 1
                i += 1 #To move to the next byte till the next byte is different
            encoded_stream.append((byte_stream[i], count))
            i += 1 #Move to the next different byte
        return encoded_stream
        '''
    

class DCTEncoder:
    def encode(self, input):
        return dct(dct(input.T, norm='ortho').T, norm='ortho')
    
    def decode(self, input):
        return idct(idct(input.T, norm='ortho').T, norm='ortho') 


class DWTEncoder:

    def lowpassfilter(self, input_1, input_2):
        return (input_1 + input_2) / 2
    def highpassfilter(self, input_1, input_2):
        return (input_1 - input_2) / 2


    def encode(self, input):
        high, width = input.shape
        
        #if the dimensions are not even, make them even by a tiny crop as an easy way.
        if high % 2 != 0:
            high -= 1
            input = input[:high, :]
        if width % 2 != 0:
            width -= 1
            input = input[:, :width]
        
        #Divide the image in odd and even columns to apply the horitzontal filters
        even_columns = input[:, 0:width:2]
        odd_columns = input[:, 1:width:2]

        L = self.lowpassfilter(even_columns, odd_columns)
        H = self.highpassfilter(even_columns, odd_columns)

        #Now apply the vertical filters
        #First we have to divide L and H in odd and even rows as before
        L_even_rows = L[0:high:2, :]
        L_odd_rows = L[1:high:2, :]
        H_even_rows = H[0:high:2, :]
        H_odd_rows = H[1:high:2, :]

        LL = self.lowpassfilter(L_even_rows, L_odd_rows)
        LH = self.highpassfilter(L_even_rows, L_odd_rows)

        HL = self.lowpassfilter(H_even_rows, H_odd_rows)
        HH = self.highpassfilter(H_even_rows, H_odd_rows)

        return LL, LH, HL, HH
    

    def visualize_dwt(self, LL, LH, HL, HH):
        #AI GENERATED CODE
        #Function to visualize the 4 subbands of the DWT, only for verification purposes

        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        bands = [
            (LL, "LL: Approximation (Low-Low)"),
            (HL, "HL: Vertical Detail (High-Low)"),
            (LH, "LH: Horizontal Detail (Low-High)"),
            (HH, "HH: Diagonal Detail (High-High)")
        ]
        ax_flat = axes.flatten()
        for i, (band, title) in enumerate(bands):
            ax_flat[i].imshow(band, cmap='gray')
            ax_flat[i].set_title(title)
            ax_flat[i].axis('off')
        plt.tight_layout()
        plt.show()

    def encode_auto(self, input_image):
        #Function that uses pywt library to compute the DWT only to prove that our results are correct
        import pywt
        coeffs = pywt.dwt2(input_image, 'db1')
        LL, (LH, HL, HH) = coeffs
        
        return LL, LH, HL, HH
    

    def decode(self, coeffs):
        LL, LH, HL, HH = coeffs
        h, w = LL.shape

        # Vertical reconstruction
        L_rec = np.zeros((h * 2, w))
        H_rec = np.zeros((h * 2, w))
        # Apply (A = L + H) in the evens, and (B = L - H) in the odds
        L_rec[0::2, :] = LL + LH
        L_rec[1::2, :] = LL - LH
        
        H_rec[0::2, :] = HL + HH
        H_rec[1::2, :] = HL - HH

        #Horizontal reconstruction
        img_rec = np.zeros((h * 2, w * 2))
        
        # Apply (A = L + H) in the evens, and (B = L - H) in the odds
        img_rec[:, 0::2] = L_rec + H_rec
        img_rec[:, 1::2] = L_rec - H_rec

        return img_rec
