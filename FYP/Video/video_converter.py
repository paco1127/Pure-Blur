
import cv2 
import os 
import shutil
from moviepy.editor import *
from Foul.mute import Audio

class video:
    def mute(video_path):
        Audio.mute_audio(video_path, output_file_path = "uploads/beep_temp.mp3")

    def getMP3(video_path):
        # for further usage
        video = VideoFileClip(video_path)
        video.audio.write_audiofile("uploads/temp.mp3")
        video.close()

    def video_to_frames(video_path, start_frame, end_frame):
    # Read the video from specified path 

        cam = cv2.VideoCapture(video_path)
        global previous_bitrate
        previous_bitrate = int(cam.get(cv2.CAP_PROP_BITRATE))

        global fps
        fps = cam.get(cv2.CAP_PROP_FPS)

        try: 
        # creating a folder named data 
            if not os.path.exists('uploads'): 
                os.makedirs('uploads') 
            if not os.path.exists('uploads/frame'): 
                os.makedirs('uploads/frame') 
            else:
                shutil.rmtree("uploads/frame")
                os.makedirs('uploads/frame')
            if not os.path.exists('uploads/frameDone'): 
                os.makedirs('uploads/frameDone') 
            else:
                shutil.rmtree("uploads/frameDone")
                os.makedirs('uploads/frameDone') 
    # if not created then raise error 
        except OSError: 
            print ('Error: Creating directory of uploads') 


        # Get the total number of frames in the video
        total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))

        # Validate the start and end frames
        if start_frame < 0 or start_frame >= total_frames:
            start_frame = 0
        if end_frame < 0 or end_frame >= total_frames:
            end_frame = total_frames - 1

        # Set the current frame to the start frame
        cam.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Iterate through the frames and extract the specified range
        frame_count = start_frame
        while frame_count <= end_frame:
            success, frame = cam.read()
            if not success:
                break

            # Save the frame as a JPEG image
            frame_name = f"uploads/frame/frame{frame_count:05d}.png"
            cv2.imwrite(frame_name, frame)

            # Display the frame count
            print(f"Extracting frame {frame_count}")

            frame_count += 1

        # Release the video file
        cam.release()




    def frame_to_video(frames_dir, out_path, output_video_path_temp="uploads/temp.avi", MuteFoul = False):
        frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])

        image_sequence = []
        for frame_file in frame_files:
            frame_path = os.path.join(frames_dir, frame_file)
            frame = cv2.imread(frame_path)
            if frame is None:
                print("Failed to load frame:", frame_path)
                continue  # Skip files that failed to load
            image_sequence.append(frame)

        frame_height, frame_width, _ = image_sequence[0].shape
        img_size = (frame_width, frame_height)

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        video = cv2.VideoWriter(output_video_path_temp, fourcc, fps, img_size)

        for frame in image_sequence:
            video.write(frame)

        video.release()
        cv2.destroyAllWindows()
        merge_video(output_video_path_temp, output_path=out_path,MuteFoul=MuteFoul)

def merge_video(video_path, output_path="uploads/censor_video.avi", MuteFoul=False):
    try:
        videoclip = VideoFileClip(video_path)
        if MuteFoul:
            audio_path = "uploads/beep_temp.mp3"
        else:
            audio_path = "uploads/temp.mp3"
        audioclip = AudioFileClip(audio_path)
        final_clip = videoclip.set_audio(audioclip)
        video = CompositeVideoClip([final_clip])
        video.write_videofile(output_path, codec='libx264')
    except Exception as e:
        print(f"Error occurred during video merging: {str(e)}")
    finally:
        video.close()
        videoclip.close()
        audioclip.close()
        os.remove(audio_path)
        os.remove(video_path)
        tomp4(output_path)

def tomp4(video_path):
    '''Converts the video to mp4 format using moviepy library'''

    clip = VideoFileClip(video_path)
    # Save the video in mp4 format with the same name
    clip.write_videofile(video_path.replace('.avi', '.mp4'))
    os.remove(video_path)
