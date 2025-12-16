import ffmpeg

def change_video_resolutin(input_video_path, output_video_path, width, height):
    stream = ffmpeg.input(input_video_path)
    stream = ffmpeg.filter(stream, 'scale', width, height)
    stream = ffmpeg.output(stream, output_video_path)
    ffmpeg.run(stream)
    return output_video_path

def change_chroma_subsampling(input_video_path, output_video_path, subsampling):
    stream = ffmpeg.input(input_video_path)
    stream = ffmpeg.output(stream, output_video_path, vf=f"format=yuv{subsampling}")
    ffmpeg.run(stream)
    return output_video_path

def get_video_info(video_path):
    probe = ffmpeg.probe(video_path)
    format_info = probe.get('format', {})

    video_stream = next((s for s in probe['streams'] if s.get('codec_type') == 'video'), None)

    if not video_stream:
        print("No video stream found")
        return None
    
    relevant_data = {
        "Video duration (seconds)": float(format_info.get('duration', 0.0)),
        "Video resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
        "Video codec": video_stream.get('codec_name'),
        "Video framerate (fps)": eval(video_stream.get('r_frame_rate', '0/1')),
        "Video bitrate (kbps)": float(format_info.get('bit_rate', 0)) // 1000,
        "Chroma subsampling": video_stream.get('pix_fmt'),
    }

    return relevant_data

def process_bbb(input_video_path, output_video_path):
    input_stream = ffmpeg.input(input_video_path, ss=0, to=20)  #Cut the first 20 seconds

    video_stream = input_stream.video
    audio_stream = input_stream.audio

    (
        ffmpeg
        .output(
            video_stream,
            audio_stream,
            audio_stream,
            audio_stream,
            output_video_path,
            # Video Parameters (copy without recodification)
            **{
                '-c:v': 'copy',

                # Audio 1 Parameters (AAC Mono)
                '-c:a:0': 'aac',
                '-ac:a:0': '1',
                '-b:a:0': '128k',

                # Audio 2 Parameters (MP3 Low Quality Stereo)
                '-c:a:1': 'libmp3lame',
                '-ac:a:1': '2',
                '-b:a:1': '32k',

                # Audio 3 Parameters (AC3 Stereo)
                '-c:a:2': 'ac3',
                '-ac:a:2': '2',
                '-b:a:2': '192k',
            }
        )
        .run(overwrite_output=True)
    )


def count_tracks(video_path):
    if not video_path.endswith('.mp4'):
        raise ValueError("The function only supports .mp4 files.")


    probe = ffmpeg.probe(video_path)  #probe function as exercice 3
    multimedia_files = probe.get('streams', [])  #creates an array of all streams in the container
    
    total_tracks = len(multimedia_files) #count the total number of tracks
    
    #this is complately optional but it looks very visual
    audio_tracks = len([s for s in multimedia_files if s['codec_type'] == 'audio'])
    video_tracks = len([s for s in multimedia_files if s['codec_type'] == 'video'])
    subtitle_tracks = len([s for s in multimedia_files if s['codec_type'] == 'subtitle'])
    
    return {
        "total_tracks": total_tracks,   #THE ONLY IMPORTANT OF THE EXERCICE
        "breakdown": {
            "audio": audio_tracks,
            "video": video_tracks,
            "subtitle": subtitle_tracks,
            "other": total_tracks - (audio_tracks + video_tracks + subtitle_tracks)
        }
    }


def visualize_motion_vectors(input_video_path, output_video_path):    
    stream = ffmpeg.input(input_video_path, flags2='+export_mvs')  #export motion vectors information of the video
    stream = ffmpeg.output(stream, output_video_path, vf='codecview=mv=pf+bf+bb')  #paint the motion vectors on the video
    ffmpeg.run(stream)
    
    return output_video_path

def show_yuv_histogram(input_video_path, output_image_path):
    stream = ffmpeg.input(input_video_path)
    stream = ffmpeg.output(stream, output_image_path, vf='histogram=yuv=1', vframes=1)
    ffmpeg.run(stream)
    return output_image_path