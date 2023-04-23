import srtm
elevation_data = srtm.get_data()
print('CGN Airport elevation (meters):', elevation_data.get_elevation(43.039522, 47.276555))