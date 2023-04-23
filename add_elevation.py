import srtm
import gpxpy
gpx = gpxpy.parse(open('/Users/griddic/Downloads/2023-dag\/train/День 1.gpx'))
elevation_data = srtm.get_data()
elevation_data.add_elevations(gpx, smooth=True)
print(gpx.to_xml())



