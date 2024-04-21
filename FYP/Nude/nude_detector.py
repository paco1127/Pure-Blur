import os
import math
import cv2
import numpy as np
import onnxruntime
from onnxruntime.capi import _pybind_state as C

__labels = [
    "FEMALE_GENITALIA_COVERED",
    "FACE_FEMALE",
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "BELLY_COVERED",
    "FEET_COVERED",
    "ARMPITS_COVERED",
    "ARMPITS_EXPOSED",
    "FACE_MALE",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_COVERED",
    "FEMALE_BREAST_COVERED",
    "BUTTOCKS_COVERED",
]


def _read_image(image_path, target_size=320):
    img = cv2.imread(image_path)
    img_height, img_width = img.shape[:2]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    aspect = img_width / img_height

    if img_height > img_width:
        new_height = target_size
        new_width = int(round(target_size * aspect))
    else:
        new_width = target_size
        new_height = int(round(target_size / aspect))

    resize_factor = math.sqrt(
        (img_width**2 + img_height**2) / (new_width**2 + new_height**2)
    )

    img = cv2.resize(img, (new_width, new_height))

    pad_x = target_size - new_width
    pad_y = target_size - new_height

    pad_top, pad_bottom = [int(i) for i in np.floor([pad_y, pad_y]) / 2]
    pad_left, pad_right = [int(i) for i in np.floor([pad_x, pad_x]) / 2]

    img = cv2.copyMakeBorder(
        img,
        pad_top,
        pad_bottom,
        pad_left,
        pad_right,
        cv2.BORDER_CONSTANT,
        value=[0, 0, 0],
    )

    img = cv2.resize(img, (target_size, target_size))

    image_data = img.astype("float32") / 255.0  # normalize
    image_data = np.transpose(image_data, (2, 0, 1))
    image_data = np.expand_dims(image_data, axis=0)

    return image_data, resize_factor, pad_left, pad_top


def _postprocess(output, resize_factor, pad_left, pad_top):
    outputs = np.transpose(np.squeeze(output[0]))
    rows = outputs.shape[0]
    boxes = []
    scores = []
    class_ids = []

    for i in range(rows):
        classes_scores = outputs[i][4:]
        max_score = np.amax(classes_scores)

        if max_score >= 0.2:
            class_id = np.argmax(classes_scores)
            x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]
            left = int(round((x - w * 0.5 - pad_left) * resize_factor))
            top = int(round((y - h * 0.5 - pad_top) * resize_factor))
            width = int(round(w * resize_factor))
            height = int(round(h * resize_factor))
            class_ids.append(class_id)
            scores.append(max_score)
            boxes.append([left, top, width, height])

    indices = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.45)

    detections = []
    for i in indices:
        box = boxes[i]
        score = scores[i]
        class_id = class_ids[i]
        detections.append(
            {"class": __labels[class_id], "score": float(score), "box": box}
        )

    return detections


class NudeDetector:
    def __init__(self, providers=None):
        self.onnx_session = onnxruntime.InferenceSession(
            f"Nude/best.onnx",
            providers=C.get_available_providers() if not providers else providers,
        )
        model_inputs = self.onnx_session.get_inputs()
        input_shape = model_inputs[0].shape
        self.input_width = input_shape[2]  # 320
        self.input_height = input_shape[3]  # 320
        self.input_name = model_inputs[0].name

    def detect(self, image_path):
        preprocessed_image, resize_factor, pad_left, pad_top = _read_image(
            image_path, self.input_width
        )
        outputs = self.onnx_session.run(None, {self.input_name: preprocessed_image})
        detections = _postprocess(outputs, resize_factor, pad_left, pad_top)

        return detections

    def censor(self, image_path, classes=[], output_path=None, mode="normal"):
        '''
            mode: normal, blur, mosaic, cover
            classes: FEMALE_GENITALIA_COVERED,FACE_FEMALE,BUTTOCKS_EXPOSED,FEMALE_BREAST_EXPOSED,FEMALE_GENITALIA_EXPOSED,MALE_BREAST_EXPOSED,ANUS_EXPOSED,FEET_EXPOSED,BELLY_COVERED,FEET_COVERED,ARMPITS_COVERED,ARMPITS_EXPOSED,FACE_MALE,BELLY_EXPOSED,MALE_GENITALIA_EXPOSED,ANUS_COVERED,FEMALE_BREAST_COVERED,BUTTOCKS_COVERED
        '''
        detections = self.detect(image_path)
        if classes:
            detections = [
                detection for detection in detections if detection["class"] in classes
            ]
    
        img = cv2.imread(image_path)
        # repeat the small image to cover the large image
        if mode == "normal":
            s_img = cv2.imread('Nude/blur.jpg')
            s_height, s_width = s_img.shape[:2]
        elif mode == "cover":
            s_img = cv2.imread('Nude/test.jpg', -1)
        # Get the dimensions of the small image
        

        for detection in detections:
            box = detection["box"]
            x, y, w, h = box[0], box[1], box[2]-1, box[3]-1
            # fix the problem of detection out of the image
            if (x<0):
                x=0
            if(y<0):
                y=0
            #code for blur
            if mode == "blur":
                blur = cv2.GaussianBlur(img[y: y + h, x: x + w, :], (99, 99), 30)
                img[y: y + h, x: x + w, :] = blur
            elif mode == "mosaic":
                mosaic = img[y:y+h, x:x+w]   # 取得剪裁區域
                level = 15         # 馬賽克程度
                ch = int(h/level)  # 縮小的高度 ( 使用 int 去除小數點 )
                cw = int(w/level)  # 縮小的寬度 ( 使用 int 去除小數點 )
                mosaic = cv2.resize(mosaic, (cw,ch), interpolation=cv2.INTER_LINEAR)
                mosaic = cv2.resize(mosaic, (w,h), interpolation=cv2.INTER_NEAREST)
                img[y:y+h, x:x+w] = mosaic   # 將圖片的剪裁區域，換成馬賽克的圖
            elif mode == "cover":
                s_img_resized = cv2.resize(s_img, (w, h))
                if (x<0):
                    x=0
                if(y<0):
                    y=0
                try:
                    img[y: y + h, x: x + w, :] = s_img_resized
                except:
                    print("^^^^^")
            elif mode == "normal":
                # Define the dimensions of the large image (imf)
                large_height, large_width = h,w  # Example dimensions, set to what you need

                # Calculate how many times to repeat the small image
                x_repeat = np.ceil(large_width / s_width).astype(int)
                y_repeat = np.ceil(large_height / s_height).astype(int)

                # Create a new image by repeating the small image
                tiled_image = np.tile(s_img, (y_repeat, x_repeat, 1))

                # Now, if the tiled image is larger than the desired dimensions, we should crop it
                tiled_image = tiled_image[:large_height, :large_width]

                img[y: y + h, x: x + w, :] = tiled_image
                # Save or display the tiled image
                #cv2.imwrite('tiled_image.jpg', tiled_image)

    
        if not output_path:
            image_path, ext = os.path.splitext(image_path)
            output_path = f"{image_path}_censored{ext}"
    
        cv2.imwrite(output_path, img)
    
        return output_path
    
if __name__ == "__main__":
    # test code
    detector = NudeDetector()
    d= detector.censor("../f31098dd-9fad-47d2-bd0b-01182d23f723")
    #d= detector.censor("2.png")
    print(d)

