################################################################################
#
# reduce_overlap_by_percent.py
# 
# enable/disable selected cameras according to given maximum overlap
#
# 
# Christoph Locker 2024
#
################################################################################


import Metashape
import math
import argparse
from shapely.geometry import Polygon

def overlap(cam1, cam2):
    """ calculates overlap of two cameras.

    cam1, cam2: Metashape.Camera
    returns: float
    """

    w = cam1.sensor.width
    h = cam1.sensor.height
    sensor_rect = Polygon([(0,0),(w,0),(w,h),(0,h)])

    corners_1 = []
    shape_corners_1 = []
    corners_2 = []
    shape_corners_2 = []

    # pick surface point for all four corners of camera sensor
    # camera 1:
    for (x, y) in [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]:
        ray_origin = cam1.unproject(Metashape.Vector([x, y, 0]))# same as 
                                                                # cam.center
        ray_target = cam1.unproject(Metashape.Vector([x, y, 1]))
        corner = surface.pickPoint(ray_origin, ray_target)
        if not corner:
            break #TODO: error handling
        corners_1.append(corner)

    # camera 2:
    for (x, y) in [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]:
        ray_origin = cam2.unproject(Metashape.Vector([x, y, 0]))
        ray_target = cam2.unproject(Metashape.Vector([x, y, 1]))
        corner = surface.pickPoint(ray_origin, ray_target)
        if not corner:
            break
        corners_2.append(corner)

    for vertex in corners_1:	
        if not cam2.project(vertex):
        	continue
        x = round(cam2.project(vertex).x,3)
        y = round(cam2.project(vertex).y,3)
        shape_corners_1.append((x,y))           

    poly1 = Polygon(shape_corners_1)

    for vertex in corners_2:	
        if not cam1.project(vertex):
        	continue
        x = round(cam1.project(vertex).x,3)
        y = round(cam1.project(vertex).y,3)
        shape_corners_2.append((x,y))           

    poly2 = Polygon(shape_corners_2)   

    return poly1.intersection(sensor_rect).area/sensor_rect.area


def enable_by_overlap(cameras, max_overlap, margin):
    """ enable cameras according to given maximum overlap 

    cameras: list
    max_overlap: integer (percent)
    margin: integer (percent)
    returns: None
    """

    max_overlap = max_overlap/100
    margin = margin/100
    cameras[0].enabled = True
    cams_iter = iter(cameras)
    previous_cam = None 

    for cam in cams_iter:
        if not previous_cam: # first camera
            previous_cam = cam
            try:
                next_cam = next(cams_iter)
            except StopIteration: # should never been reached ;)
                print('processed all selected cameras!')
                break
        else:
            next_cam = cam

        ol = overlap(previous_cam, next_cam)

        if ol < (max_overlap - margin): # overlap to low
            next_cam.enabled = True
            print("W: %s 's overlap with %s is only %.3f" % (next_cam.label, previous_cam.label, ol))
            previous_cam = next_cam
            continue

        while ol > max_overlap:
            next_cam.enabled = False
            interim_cam = next_cam # in case overlap with next cam ist too low.
            interim_ol = ol
            try:
                next_cam = next(cams_iter)
            except StopIteration:
                print('processed all selected cameras!')
                return
            ol = overlap(previous_cam, next_cam)

        if ol < (max_overlap - margin): # resulting overlap to high
            interim_cam.enabled = True
            print("W: %s 's overlap with %s is %.3f" % (interim_cam.label, previous_cam.label, interim_ol))
        else:
            next_cam.enabled=True
            print("%s 's overlap with %s is %.3f" % (next_cam.label, previous_cam.label, ol))

        previous_cam = next_cam

    print('processed all selected cameras!')


if __name__ == '__main__':
    print('Script started!')

    # get command line arguments
    desc = "reduces overlap between cameras given in percent"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("--overlap", required=True, type=int)
    parser.add_argument("--margin", required=False, type=int, default=2)
    args = parser.parse_args()

    o = args.overlap
    m = args.margin

    # start work
    chunk = Metashape.app.document.chunk
    
    # TODO: make argument to function? or leave as below?
    # -> test with HePa where there ar a lot more artifacts in tie points
    #

    # choose surface model
    #if chunk.model:
    #    surface = chunk.model
    #elif chunk.dense_cloud:
    #    surface = chunk.dense_cloud
    #else:
    #    surface = chunk.point_cloud
    surface = chunk.tie_points

    cameras_sel = [camera for camera in chunk.cameras if camera.selected]

    if len(cameras_sel) < 2:
	    raise Exception("Must select at least two images!")
    
    print("%d cameras selected." % len(cameras_sel))

    enable_by_overlap(cameras_sel, o, m)

    print("Script completed!")
