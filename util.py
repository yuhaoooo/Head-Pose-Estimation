'''some functions for debug and some utility functions'''

import cv2
import math
import numpy as np

def move_box(box, offset):
    ''' Move the box to direction speficied by vector offset '''
    left_x = box[0] + offset[0]
    top_y = box[1] + offset[1]
    right_x = box[2] + offset[0]
    bottom_y = box[3] + offset[1]
    return [left_x, top_y, right_x, bottom_y]

def get_square_box(box):
    ''' Get a square box out of the given box, by expanding it.'''
    left_x = box[0]
    bottom_y = box[1]
    right_x = box[2]
    top_y = box[3]

    box_width = right_x - left_x
    box_height = top_y - bottom_y

    # check if box is already a square. If not, make it a square. 
    diff = box_height - box_width

    delta = int(abs(diff) / 2)

    if diff == 0:      # already a square
        return box
    elif diff > 0:     # height > width, a slim box
        left_x -= delta
        right_x += delta
        if diff % 2 == 1: 
            right_x += 1
    else:
        top_y += delta
        bottom_y -= delta
        if diff % 2 == 1:
            bottom_y -= 1

    # Make sure box is always square.
    # print("%d ---- %d ---- %d ---- %d ----- %d ----- %d" %(right_x, left_x, bottom_y, top_y, (right_x - left_x), (bottom_y - top_y)))
    assert ((right_x - left_x) == (top_y - bottom_y)), 'Box is not square.'
    return [left_x, bottom_y, right_x, top_y]

def box_in_image(box, image):
    ''' Check if the box is in image. '''
    rows = image.shape[0]
    cols = image.shape[1]
    return box[0] >= 0 and box[1] >= 0 and box[2] <= cols and box[3] <= rows

def draw_faceboxes(image, facebox):
    '''Draw the detection result on image'''

    cv2.rectangle(image, (facebox[0], facebox[1]), (facebox[2], facebox[3]), (0, 255, 0))
    label = "face"
    label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

    cv2.rectangle(image, (facebox[0], facebox[1] - label_size[1]), (facebox[0] + label_size[0], facebox[1] + base_line), (0, 255, 0), cv2.FILLED)
    cv2.putText(image, label, (facebox[0], facebox[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

def draw_marks(image, marks, color=(255, 255, 255)):
    """Draw mark points on image"""
    for mark in marks:
        cv2.circle(image, (int(mark[0]), int(mark[1])), 1, color, -1, cv2.LINE_AA)


def draw_annotion_box(image, rotation_vector, translation_vector, color = (255,255,255), line_width = 2):
    '''Draw a 3D box as annoation of pose'''

    point_3d = []
    rear_size = 75
    rear_depth = 0
    point_3d.append((-rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, rear_size, rear_depth))
    point_3d.append((rear_size, -rear_size, rear_depth))
    point_3d.append((-rear_size, -rear_size, rear_depth))

    front_size = 100
    front_depth = 100
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d.append((-front_size, front_size, front_depth))
    point_3d.append((front_size, front_size, front_depth))
    point_3d.append((front_size, -front_size, front_depth))
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d = np.array(point_3d, dtype=np.float).reshape(-1, 3)

    # map to 2d image points.
    (point_2d, _) = cv2.projectPoints(point_3d, rotation_vector, translation_vector, self.camera_matrix,self.dist_coeefs)
    point_2d = np.int32(point_2d.reshape(-1, 2))

    # Draw all the lines
    cv2.polylines(image, [point_2d], True, color, line_width, cv2.LINE_AA)
    cv2.line(image, tuple(point_2d[1]), tuple(point_2d[6]), color, line_width, cv2.LINE_AA)
    cv2.line(image, tuple(point_2d[2]), tuple(point_2d[7]), color, line_width, cv2.LINE_AA)
    cv2.line(image, tuple(point_2d[3]), tuple(point_2d[8]), color, line_width, cv2.LINE_AA)

def get_angle(rotation_vector):
    '''convert the rotation vectors into angle'''

    rotation_matrix = np.zeros((3,3), dtype=np.float32)
    cv2.Rodrigues(rotation_vector, rotation_matrix)

    sy = np.sqrt(rotation_matrix[0,0] * rotation_matrix[0,0] + rotation_matrix[1,0] * rotation_matrix[1,0])

    if sy < 1e-6:
        x = math.atan2(rotation_matrix[1,2], rotation_matrix[1, 1])
        y = math.atan2(rotation_matrix[2,0], sy)
        z = 0
    else:
        x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        y = math.atan2(-rotation_matrix[2, 0], sy)
        z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    
    return [x, y, z]