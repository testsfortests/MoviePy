from moviepy.editor import *
import requests
import tempfile

image1_path = "./uploads/image_que.png"
image2_path = "./uploads/image_ans.png"
sound1_path = "./uploads/music_que.mp3"
sound2_path = "./resource/countdown.mp3"
sound3_path = "./uploads/music_ans.mp3"
output_path = "./uploads/output.mp4"

TELE_ENDPOINT_URL = "https://tft-backend.onrender.com/tele/send-file"  # URL of the tele endpoint

def create_final_video():
    # Load images
    image1_clip = ImageClip(image1_path)
    image2_clip = ImageClip(image2_path)

    # Load audio files
    sound1_clip = AudioFileClip(sound1_path)
    sound2_clip = AudioFileClip(sound2_path)
    sound3_clip = AudioFileClip(sound3_path)

    # Combine the sounds for the first image
    combined_sound1 = concatenate_audioclips([sound1_clip, sound2_clip])

    # Set the duration of the video clips to match the duration of the audio files
    video_clip1 = image1_clip.set_audio(combined_sound1).set_duration(combined_sound1.duration or 1)
    video_clip2 = image2_clip.set_audio(sound3_clip).set_duration(sound3_clip.duration or 1)

    # Concatenate the video clips to create the final video
    final_clip = concatenate_videoclips([video_clip1, video_clip2])

    print("writing started...")

    final_clip.write_videofile(output_path, codec='libx264', fps=24)

    print("Video file sent successfully to the Telegram endpoint")
    
# Example usage:

# create_final_video()
