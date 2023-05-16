import math
from operator import itemgetter
import os
from pathlib import Path
from turtle import width
import srtm
import gpxpy
from gpxpy.geo import length_3d
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["figure.autolayout"] = True

class Point:
    def __init__(self, distance, elevation) -> None:
        self.distance = distance
        self.elevation = elevation
        self.marks = []
        
        

def get_file(file_path):
    gpx = gpxpy.parse(open(file_path))
    elevation_data = srtm.get_data()
    elevation_data.add_elevations(
        gpx, 
        smooth=True,
    )
    return gpx

def calc_total_asc_desc_angl(track):
    asc = 0
    desc = 0
    max_angl = 0
    max_angl_index = 0
    prev = 0
    for i in range(1, len(track)):
        if (track[i].distance - track[prev].distance) > (50 / 1000):
            if (up := track[i].elevation - track[prev].elevation) > 0:
                asc += up 
            else:
                desc -= up
            prev = i

        for l in range(i, 0, -1):
            if track[i].distance - track[l].distance > 0.1:
                break
        if track[i].distance - track[l].distance < 0.1:
            continue
            
        for r in range(i, len(track)):
            if track[r].distance - track[i].distance > 0.1:
                break
        if track[r].distance - track[i].distance < 0.1:
            continue
        angl = (track[r].elevation - track[l].elevation) / ((track[r].distance - track[l].distance) * 1000)
        if angl > max_angl:
            max_angl = angl
            max_angl_index = i
    return int(asc), int(desc), (max_angl_index, int(max_angl * 100))

def process_file(file_path):
    gpx = get_file(file_path)
    assert len(gpx.tracks) == 1
    track = gpx.tracks[0]
    assert len(track.segments) == 1
    seg = track.segments[0]
    track = []
    for i, point in enumerate(seg.points):
        track.append(Point(length_3d(seg.points[:i+1])/1000, point.elevation))
        # print(int(length_3d(seg.points[:i+1])), point.elevation)
    
    my_dpi=96
    plt.figure(figsize=(1000/my_dpi, 600/my_dpi), dpi=my_dpi)
    # fig, ax = plt.subplots()

    t = [p.distance for p in track]
    s = [p.elevation for p in track]
    plot = plt.plot(
        t, 
        s, 
        
        # lw=2,
        )
    
    # plt.annotate('local max', xy=(20_000, 400),xytext=(20_000, 0),
    #             arrowprops=dict(facecolor='black', shrink=0.05, width=0.5),
    #             )

    min_elevation = min(p.elevation for p in track)
    max_elevation = max(p.elevation for p in track)
    prev_annotations_y = []
    def y_to_annotane(index):
        cur_elevation = int(track[index].elevation)
        forbidden_y = [t.elevation for t in track if abs(t.distance - track[index].distance) < 1]
        forbidden_y.extend(prev_annotations_y[-10:])
        for y in range(int(min_elevation - 200), cur_elevation, 10):
            # if abs(y - track[index].elevation) < 200:
            #     continue
            # if prev_annotations_y and min([abs(y - prev) for prev in prev_annotations_y[-5:]]) < 100:
            #     continue
            if forbidden_y and min([abs(y - prev) for prev in forbidden_y]) < 50:
                continue
            return y
        for y in range(int(max_elevation + 100), cur_elevation, -10):
            # if abs(y - track[index].elevation) < 200:
            #     continue
            # if prev_annotations_y and min([abs(y - prev) for prev in prev_annotations_y[-5:]]) < 100:
            #     continue
            if forbidden_y and min([abs(y - prev) for prev in forbidden_y]) < 30:
                continue
            return y
        return min_elevation - 200
    
    waypoints_with_trackpoints = []
    for p in gpx.waypoints:
        index = None
        min_d = None
        for i, sp in enumerate(seg.points):
            d = length_3d([p, sp])
            if min_d is None:
                min_d = d
                index = i 
            if d < min_d:
                min_d = d 
                index = i
        del i
        assert index is not None
        waypoints_with_trackpoints.append((p.name, index, track[index].distance))
    acs, desc, (mangli, mangl) = calc_total_asc_desc_angl(track)
    waypoints_with_trackpoints.append((f'набор: {acs}', 0, 0))
    waypoints_with_trackpoints.append((f'сброс: {desc}', 0, 0))
    waypoints_with_trackpoints.append((f'макс угол: {mangl}', mangli, track[mangli].distance))
                                      
    waypoints_with_trackpoints = sorted(waypoints_with_trackpoints, key=itemgetter(2))

        
    for name, index, _ in waypoints_with_trackpoints:
        annotation_y = y_to_annotane(index)
        prev_annotations_y.append(annotation_y)
        plt.annotate(
            name, 
            xy=(track[index].distance, track[index].elevation), 
            xytext=(track[index].distance, annotation_y),
            arrowprops=dict(
                    # facecolor='black', 
                    shrink=0.05, 
                    width=1, 
                    headwidth = 2,
                    linestyle=':',
                    ),
        )


    plt.ylim(min_elevation - 200, max_elevation + 100)
    plt.grid(True, which='both', linestyle=':')
    plt.minorticks_on()
    # plt.xlabel([t.distance / 1000 for t in track])
    plt.xticks(np.arange(0, track[-1].distance, 5))
    plt.title(Path(file_path).name)
    # plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(file_path + '.jpg')


def main():
    # file_path = '/Users/griddic/Downloads/2023-dag/train/День 1.gpx'
    dir = '/Users/griddic/Downloads/2023-dag/days/'
    names = os.listdir(dir)
    names = [n for n in names if n.endswith('.gpx')]
    for n in names:
        process_file(os.path.join(dir, n))


if __name__ == '__main__':
    main()