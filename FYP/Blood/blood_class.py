from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import cv2
import numpy as np

class BlurBlood:
    def __init__(self):
        self.model = YOLO("Blood/blood.pt")
        self.names = self.model.names
        self.blur_ratio = 50

    def __generate_rainbow_pattern(self, width, height):
        # Create an image with a horizontal gradient of hues
        rainbow_img = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(width):
            hue = int((i / width) * 180)  # OpenCV uses hue range from 0-180
            rainbow_img[:, i] = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR).squeeze()
        return rainbow_img

    def blur_blood_image(self, image_path, output_path=None):
        # Load the image
        im0 = cv2.imread(image_path)

        # Perform inference
        results = self.model(image_path)
        
        if (results[0].masks == None):
            return False

        for result in results:
            # Check if masks are available for the detected object
            if hasattr(result, 'masks'):
                # Loop over each mask
                for mask_polygon in result.masks:
                    # Get the points of the polygon
                    points = mask_polygon.xy.pop().astype(np.int32)
                    points = points.reshape((-1, 1, 2))

                    # Create a mask where the polygon will be drawn
                    mask = np.zeros(im0.shape[:2], dtype=np.uint8)
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

        # Save the image
        if output_path:
            cv2.imwrite(output_path, im0)
            return True
        return False






if __name__ == "__main__":
    blur_blood = BlurBlood()
    image_path = "Blood/a.jpg"
    blurred_image = blur_blood.blur_blood_image(image_path)
    cv2.imwrite("Blood/blured.jpg", blurred_image) 