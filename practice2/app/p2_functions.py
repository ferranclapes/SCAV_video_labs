import ffmpeg
from . import s2_functions as s2
import zipfile
import os

def convert_into_open_codecs(input_video_path, output_video_path, codec):
    # Function to convert an input video into VP8, VP9, h265 and AV1 codecs
    stream = ffmpeg.input(input_video_path, ss=20, to=50)
    if codec == 'vp8':
        stream = ffmpeg.output(stream, output_video_path, vcodec='libvpx', acodec='libvorbis')
    elif codec == 'vp9':
        stream = ffmpeg.output(stream, output_video_path, vcodec='libvpx-vp9', acodec='libvorbis')
    elif codec == 'h265':
        stream = ffmpeg.output(stream, output_video_path, vcodec='libx265', acodec='aac')
    elif codec == 'av1':
        stream = ffmpeg.output(stream, output_video_path, vcodec='libaom-av1', acodec='libopus')
    else:
        raise ValueError("You put an invalid codec, choose: vp8, vp9, h265 or av1")
    
    #execute the conversion to the choosen codec, it overwrites the output if exists
    stream.run(overwrite_output=True)

def encoding_ladder(input_video_path, output_folder):

    # This array contains the resolutions which the video will be scaled to.
    # found that if the resolution is higher than the original it outputs an error
    res_bitrate = [
        ('426', '240'),
        ('854', '480'),
        ('1280', '720'), 
        #('1920', '1080'),
    ]

    #array of the path of the generated videos
    generated_video_files = []

    #for each resolution, generate a scaled version of the video
    for res in res_bitrate:
        try:
            #reuse the function created in the seminar 2
            output_video_path = s2.change_video_resolution(
                input_video_path,
                os.path.join(output_folder, f"video_{res[0]}x{res[1]}.mp4"),
                res[0],
                res[1]
            )
            generated_video_files.append(output_video_path)
        except Exception as e:
            print(f"Error processing resolution {res[0]}x{res[1]}: {e}")
    
    # Because we cannot return multiple files, we will compress them into a zip file to output
    zip_path = os.path.join(output_folder, "encoding_ladder.zip")

    with zipfile.ZipFile(zip_path, 'w') as zip:
        for video_file in generated_video_files:
            zip.write(video_file, arcname=os.path.basename(video_file))
    
    return zip_path
    

