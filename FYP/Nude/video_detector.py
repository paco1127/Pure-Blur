from .nude_detector import NudeDetector
import os 
import shutil
import cv2
import concurrent.futures

from Video.video_converter import video as vc

class VideoDetector:
    def __init__(self):
        self.detector = NudeDetector()

    def censor_frame(self,file_path, done_directory, start_file, end_file, classes=[], mode='normal'):
        for i in range(start_file, end_file):
            filename = file_path + "/"  + f"frame{i:05d}.png"
            print(filename)
            output_path = done_directory + "/" + f"frame{i:05d}.png"

            self.detector.censor(image_path=filename, classes=classes, output_path=output_path, mode=mode)

    def censor(self, video_path, v_output_path='uploads/output.avi', classes = [], FoulMute = False, mode='normal'):
        #cocurrent process!

        total_frames = int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FRAME_COUNT))

        frame_range = total_frames // 4

        # Create four concurrent tasks for extracting frames
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(4):
                start = i * frame_range
                end = start + frame_range

                # Adjust the end frame for the last task to handle any remaining frames
                if i == 3:
                    end = total_frames 
                
                future = executor.submit(vc.video_to_frames, video_path, start, end)
                futures.append(future)

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

        #vc.video_to_frames(video_path, 0, total_frames)

        vc.getMP3(video_path)
        if(FoulMute):
            vc.mute(video_path)

        frame_directory = 'uploads/frame'
        done_directory = 'uploads/frameDone'

        file_count = len([filename for filename in os.listdir(frame_directory) if filename.endswith('.png')])

           # Calculate the frame range
        frame_range = file_count // 4


        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(4):
                start = i * frame_range
                end = start + frame_range

                if i == 3:
                    end = file_count

                future = executor.submit(self.censor_frame, frame_directory, done_directory, start, end, classes, mode)
                futures.append(future)

            concurrent.futures.wait(futures)

        #self.censor_frame(frame_directory, done_directory, 0, file_count, classes)


        vc.frame_to_video('uploads/frameDone/',v_output_path, MuteFoul=FoulMute)
        shutil.rmtree("uploads/frameDone")
        shutil.rmtree("uploads/frame")

if __name__ == '__main__':
    # test code
    detector = VideoDetector()
    detector.censor('../uploads/video.mp4')
    print("done")
        