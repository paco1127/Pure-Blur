# import the inference-sdk
from inference_sdk import InferenceHTTPClient
import cv2
import numpy as np

class BlurBlood:
    def __init__(self):
        self.CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="wfzM80fSbz4VVCiHAp46"
        )
        self.blur_ratio = 100

    def predict(self, image_path):
        return self.CLIENT.infer(image_path, model_id="blood-zwo1s/2")
    
    def __generate_rainbow_pattern(self, width, height):
        # Create an image with a horizontal gradient of hues
        rainbow_img = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(width):
            hue = int((i / width) * 180)  # OpenCV uses hue range from 0-180
            rainbow_img[:, i] = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR).squeeze()
        return rainbow_img
    

    def blur_blood_image(self, image_path, segmentation_results):
        # Load the image
        im0 = cv2.imread(image_path)

        for prediction in segmentation_results['predictions']:
            # Get the points of the polygon
            points = np.array([[int(point['x']), int(point['y'])] for point in prediction['points']], np.int32)
            points = points.reshape((-1, 1, 2))

            # Create a mask where the polygon will be drawn
            mask = np.zeros(im0.shape[:2], dtype=np.uint8)

            # Fill the polygon in the mask
            cv2.fillPoly(mask, [points], 255)

            # Create a blurred image
            blurred_image = cv2.blur(im0, (self.blur_ratio, self.blur_ratio))

            # Create a rainbow pattern for the bounding box size
            height, width, _ = im0.shape
            rainbow_overlay = self.__generate_rainbow_pattern(width, height)

            # Overlay the rainbow pattern onto the blurred object
            rainbow_obj = cv2.addWeighted(blurred_image, 0.5, rainbow_overlay, 0.5, 0)

            # Use the mask to combine the original and rainbow-blurred image
            im0 = np.where(mask[:,:,None].astype(bool), rainbow_obj, im0)

        return im0

if __name__ == "__main__":
    image_path = "Blood/blood.jpg"
    bb = BlurBlood()
    result = bb.predict(image_path)
    blurred_image = bb.blur_blood_image(image_path, result)
    cv2.imwrite("Blood/blured.jpg", blurred_image) 
    print("Image saved as blured.jpg")