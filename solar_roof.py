from __future__ import print_function
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import glob
from shapely.geometry import Polygon

zoom = 20
tileSize = 256
initialResolution = 2 * math.pi * 6378137 / tileSize
originShift = 2 * math.pi * 6378137 / 2.0
earthc = 6378137 * 2 * math.pi
factor = math.pow(2, zoom)
map_width = 256 * (2 ** zoom)

def grays(im):
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
def white_image(im):
    return cv2.bitwise_not(np.zeros(im.shape, np.uint8))
def pixels_per_mm(lat, length):
    return length / math.cos(lat * math.pi / 180) * earthc * 1000 / map_width
def sharp(gray):
    blur = cv2.bilateralFilter(gray, 5, sigmaColor=7, sigmaSpace=5)
    kernel_sharp = np.array((
        [-2, -2, -2],
        [-2, 17, -2],
        [-2, -2, -2]), dtype='int')
    return cv2.filter2D(blur, -1, kernel_sharp)

def contours_canny(cnts):
    cv2.drawContours(canny_contours, cnts, -1, 255, 1)
    # Removing the contours detected inside the roof
    for cnt in cnts:
        counters = 0
        cnt = np.array(cnt)
        cnt = np.reshape(cnt, (cnt.shape[0], cnt.shape[2]))
        pts = []

        if cv2.contourArea(cnt) > 10:
            for i in cnt:
                x, y = i
                if edged[y, x] == 255:
                    counters += 1
                    pts.append((x, y))

        if counters > 10:
            pts = np.array(pts)
            pts = pts.reshape(-1, 1, 2)
            cv2.polylines(canny_polygons, [pts], True, 0)

def rotation(center_x, center_y, points, ang):
    angle = ang * math.pi / 180
    rotated_points = []
    for p in points:
        x, y = p
        x, y = x - center_x, y - center_y
        x, y = (x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle))
        x, y = x + center_x, y + center_y
        rotated_points.append((x, y))
    return rotated_points

def createLineIterator(P1, P2, img):
    imageH = img.shape[0]
    imageW = img.shape[1]
    P1X = P1[0]
    P1Y = P1[1]
    P2X = P2[0]
    P2Y = P2[1]

    # difference and absolute difference between points
    # used to calculate slope and relative location between points
    dX = P2X - P1X
    dY = P2Y - P1Y
    dXa = np.abs(dX)
    dYa = np.abs(dY)

    # predefine numpy array for output based on distance between points
    itbuffer = np.empty(shape=(np.maximum(dYa, dXa), 3), dtype=np.float32)
    itbuffer.fill(np.nan)

    # Obtain coordinates along the line using a form of Bresenham's algorithm
    negY = P1Y > P2Y
    negX = P1X > P2X
    if P1X == P2X:  # vertical line segment
        itbuffer[:, 0] = P1X
        if negY:
            itbuffer[:, 1] = np.arange(P1Y - 1, P1Y - dYa - 1, -1)
        else:
            itbuffer[:, 1] = np.arange(P1Y + 1, P1Y + dYa + 1)
    elif P1Y == P2Y:  # horizontal line segment
        itbuffer[:, 1] = P1Y
        if negX:
            itbuffer[:, 0] = np.arange(P1X - 1, P1X - dXa - 1, -1)
        else:
            itbuffer[:, 0] = np.arange(P1X + 1, P1X + dXa + 1)
    else:  # diagonal line segment
        steepSlope = dYa > dXa
        if steepSlope:
            slope = dX.astype(float) / dY.astype(float)
            if negY:
                itbuffer[:, 1] = np.arange(P1Y - 1, P1Y - dYa - 1, -1)
            else:
                itbuffer[:, 1] = np.arange(P1Y + 1, P1Y + dYa + 1)
            itbuffer[:, 0] = (slope * (itbuffer[:, 1] - P1Y)).astype(int) + P1X
        else:
            slope = dY.astype(float) / dX.astype(float)
            if negX:
                itbuffer[:, 0] = np.arange(P1X - 1, P1X - dXa - 1, -1)
            else:
                itbuffer[:, 0] = np.arange(P1X + 1, P1X + dXa + 1)
            itbuffer[:, 1] = (slope * (itbuffer[:, 0] - P1X)).astype(int) + P1Y

    # Remove points outside of image
    colX = itbuffer[:, 0]
    colY = itbuffer[:, 1]
    itbuffer = itbuffer[(colX >= 0) & (colY >= 0) & (colX < imageW) & (colY < imageH)]

    # Get intensities from img ndarray
    itbuffer[:, 2] = img[itbuffer[:, 1].astype(np.uint), itbuffer[:, 0].astype(np.uint)]

    return itbuffer

def panel_rotation(panels_series, solar_roof_area):

    high_reso = cv2.pyrUp(solar_roof_area)
    rows, cols = high_reso.shape
    high_reso_new = cv2.pyrUp(edged)

    for _ in range(panels_series - 2):
        for col in range(0, cols, l + 1):
            for row in range(0, rows, w + 1):

                # Rectangular Region of interest for solar panel area
                solar_patch = high_reso[row:row + (w + 1) * pw + 1, col:col + ((l * pl) + 3)]
                r, c = solar_patch.shape

                # Rotation of rectangular patch according to the angle provided
                patch_rotate = np.array([[col, row], [c + col, row], [c + col, r + row], [col, r + row]], np.int32)
                rotated_patch_points = rotation((col + c) / 2, row + r / 2, patch_rotate, solar_angle)
                rotated_patch_points = np.array(rotated_patch_points, np.int32)

                # Check for if rotated points go outside of the image
                if (rotated_patch_points > 0).all():
                    solar_polygon = Polygon(rotated_patch_points)
                    polygon_points = np.array(solar_polygon.exterior.coords, np.int32)

                    # Appending points of the image inside the solar area to check the intensity
                    patch_intensity_check = []

                    # Point polygon test for each rotated solar patch area
                    for j in range(rows):
                        for k in range(cols):
                            if cv2.pointPolygonTest(polygon_points, (k, j), False) == 1:
                                patch_intensity_check.append(high_reso[j, k])

                    # Check for the region available for Solar Panels
                    if np.mean(patch_intensity_check) == 255:

                        # Moving along the length of line to segment solar panels in the patch
                        solar_line_1 = createLineIterator(rotated_patch_points[0], rotated_patch_points[1], high_reso)
                        solar_line_1 = solar_line_1.astype(int)
                        solar_line_2 = createLineIterator(rotated_patch_points[3], rotated_patch_points[2], high_reso)
                        solar_line_2 = solar_line_2.astype(int)
                        line1_points = []
                        line2_points = []
                        if len(solar_line_2) > 10 and len(solar_line_1) > 10:

                            # Remove small unwanted patches
                            cv2.fillPoly(high_reso, [rotated_patch_points], 0)
                            cv2.fillPoly(high_reso_new, [rotated_patch_points], 0)
                            cv2.polylines(high_reso_orig, [rotated_patch_points], 1, 0, 2)
                            cv2.polylines(high_reso_new, [rotated_patch_points], 1, 0, 2)

                            cv2.fillPoly(high_reso_orig, [rotated_patch_points], (0, 0, 255))
                            cv2.fillPoly(high_reso_new, [rotated_patch_points], (0, 0, 255))

                            for i in range(5, len(solar_line_1), 5):
                                line1_points.append(solar_line_1[i])
                            for i in range(5, len(solar_line_2), 5):
                                line2_points.append(solar_line_2[i])

                        # Segmenting Solar Panels in the Solar Patch
                        for points1, points2 in zip(line1_points, line2_points):
                            x1, y1, _ = points1
                            x2, y2, _ = points2
                            cv2.line(high_reso_orig, (x1, y1), (x2, y2), (0, 0, 0), 1)
                            cv2.line(high_reso_new, (x1, y1), (x2, y2), (0, 0, 0), 1)

        # Number of Solar Panels in series (3/4/5)
        panels_series = panels_series - 1
    result = Image.fromarray(high_reso_orig)
    resut_2 = Image.fromarray(high_reso_new)



    BLUE_MIN = np.array([0, 0, 255], np.uint8)
    BLUE_MAX = np.array([50,50,255], np.uint8)

    dst = cv2.inRange(high_reso_orig, BLUE_MIN, BLUE_MAX)
    no_blue_pixels = cv2.countNonZero(dst)

    area_of_panels = no_blue_pixels*0.075

def output(fname):
    # images = glob.glob('2.jpeg')
    

    # for fname in images:
    # pl = No of panels together as length commonside, pw = Same as for pw here w = width
    # l = Length of panel in mm, w = Width of panel in mm
    # solar_angle = Angle for rotation
    global pl, pw, l, w, solar_angle
    pl, pw, l, w, solar_angle = 1, 1, 2, 2, 30
    image = cv2.imread(fname)
    img = cv2.pyrDown(image)
    #print('image shape : ',img.shape)
    global n_white_pix
    n_white_pix = np.sum(img==255)
    # Upscaling of Image
    global high_reso_orig
    high_reso_orig = cv2.pyrUp(image)

    # White blank image for contours of Canny Edge Image
    global canny_contours
    canny_contours = white_image(image)
    # White blank image for contours of original image
    global image_contours,image_polygons,canny_polygons
    image_contours = white_image(image)

    # White blank images removing rooftop's obstruction
    image_polygons = grays(canny_contours)
    canny_polygons = grays(canny_contours)

    # Gray Image
    global grayscale,sharp_image,edged,solar_roof,pixel_width,pixel_height
    grayscale = grays(image)
    # Edge Sharpened Image
    sharp_image = sharp(grayscale)
    # Canny Edge
    edged = cv2.Canny(sharp_image, 200, 300)
    edge_image = sharp_image
    # Contours in Canny Edge Image
    contours_canny(cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2])

    # Optimum place for placing Solar Panels
    solar_roof = cv2.bitwise_and(image_polygons, canny_polygons)
    pixel_width = solar_roof.shape[1]
    pixel_height = solar_roof.shape[0]
    area_in_pixels = pixel_width * pixel_height

    # Convert the pixel size to mm^2
    pixel_resolution = 0.1
    solar_panels_area= area_in_pixels * pixel_resolution**2
    ret, thresh2 = cv2.threshold(edge_image, 198, 255, cv2.THRESH_BINARY)

    total_roof_area = np.sum(thresh2==255)
    area_roof = total_roof_area*0.075

    print('area of building roof: ',total_roof_area*0.075/15,'sqm')
    print('area of solar roof: ', solar_panels_area/15, 'sqm')

    # Print the size of the solar roof in mm^2
    return solar_panels_area /15

print(output("library.jpg"))

