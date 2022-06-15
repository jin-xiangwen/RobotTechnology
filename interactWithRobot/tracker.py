import cv2
import torch
import numpy as np

def draw_bboxes(image, bboxes, line_thickness):
    line_thickness = line_thickness or round(
        0.002 * (image.shape[0] + image.shape[1]) * 0.5) + 1

    for (x1, y1, x2, y2, lbl, conf) in bboxes:
        color = (0, 255, 0)

        c1, c2 = (x1, y1), (x2, y2)
        cv2.rectangle(image, c1, c2, color, thickness=line_thickness)

        font_thickness = max(line_thickness - 1, 1)
 
        cv2.putText(image, lbl, (c1[0], c1[1] - 2), 0, line_thickness / 3,
                    [225, 255, 255], thickness=font_thickness, lineType=cv2.LINE_AA)


    return image
