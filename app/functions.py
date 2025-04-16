from moviepy import VideoFileClip
from openai import OpenAI, OpenAIError

import filetype
import os
import tempfile
import uuid

import prompt

ALLOWED_FILE_TYPES = {"mp4", "mp3"}

def _save_video(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(file_bytes)
        video_path = temp_video.name
    return video_path

def fileCheckup(file_byte: bytes) -> bool:
    try:
        kind = filetype.guess(file_byte) 
        # If the url provide no file
        if kind is None:
            return False
        # If url provided file
        file_ext = kind.extension
        # But wrong file extension
        if file_ext not in ALLOWED_FILE_TYPES:
            return False
        else:
        # And is the correct file extension
            return True
    except Exception:
        return False
    
def convert_bytes_2_audio(file_bytes: bytes):
    # Save file bytes as a temporary mp4
    video_path = _save_video(file_bytes=file_bytes)
    # Generate a temporary audio file with empty content
    audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
    # Write into audio file with audio extract from mp4
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()
    # Remove video file
    os.remove(video_path)
    # Return the temp audio file path
    return audio_path

def convert_bytes_2_vid_no_audio(file_bytes: bytes):
    video_path = _save_video(file_bytes=file_bytes)
    clip = VideoFileClip(video_path)
    output_path = "output.mp4"
    clip.without_audio().write_videofile(output_path, codec="libx264", audio=False)
    clip.close()
    return output_path

def ai_transcript(audio_path: str, token: str):
    print("token: " + token)
    
    # client = OpenAI(api_key=token)
    # audio_file = client.files.create(
    #     file=open(audio_path, "rb"), 
    #     purpose="user_data",
    # )
    # response = client.responses.create(
    #     model="gpt-4.1", 
    #     input=[
    #         {
    #             "role": "user", 
    #             "content": [
    #                 {
    #                     "type": "input_file", 
    #                     "file_id": audio_file.id, 
    #                 }, 
    #                 {
    #                     "type": "input_text", 
    #                     "text": prompt.PROMPT
    #                 }
    #             ]
    #         }
    #     ]
    # )
    # return response

