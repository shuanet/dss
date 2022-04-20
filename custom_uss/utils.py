#!/usr/bin/python3


import xml.etree.ElementTree as ET
import pyproj
import shapely.geometry


def to_sec(time):

	a = time.split(" ")
	AMPM = a[1]
	b = a[0].split(":")
	h = int(b[0])
	m = int(b[1])
	s = int(b[2])
	sec = h * 3600 + m * 60 + s
	if AMPM == 'PM':
		sec += 12 * 3600
	return sec



def parse_fp(fp_file):

	pprz_fp_info = {}
	waypoints = []

	tree = ET.parse(fp_file)
	root = tree.getroot()

	for child in root:
		if child.tag == "waypoints":
			print(child)
			for wp in child:
				waypoint = Waypoint(wp.attrib["name"], wp.attrib["x"], wp.attrib["y"])
				waypoints.append(waypoint)

	pprz_fp_info["alt"] = root.attrib["alt"]
	pprz_fp_info["lat0"] = root.attrib["lat0"]
	pprz_fp_info["lon0"] = root.attrib["lon0"]
	pprz_fp_info["waypoints"] = waypoints

	return pprz_fp_info


def get_mission_geometry(fp_info):

	lat0 = fp_info["lat0"]
	lon0 = fp_info["lon0"]
	waypoints = fp_info["waypoints"]

	utm_crs_list = pyproj.database.query_utm_crs_info(
	datum_name = "WGS 84",
	area_of_interest = pyproj.aoi.AreaOfInterest(
		west_lon_degree = float(lon0),
		south_lat_degree = float(lat0),
		east_lon_degree = float(lon0),
		north_lat_degree = float(lat0)
		)
	)

	utm_crs = pyproj.CRS.from_epsg(utm_crs_list[0].code)

	p = pyproj.Proj(utm_crs, preserve_units = False)

	x0, y0 = p(lon0, lat0)

	for wp in waypoints:
		x, y = x0 + float(wp.x), y0 + float(wp.y)
		wp.lon, wp.lat = p(x, y, inverse = True)

	coords = []
	for i in range(len(waypoints) - 1):
		coords.append(((waypoints[i].lon, waypoints[i].lat), (waypoints[i + 1].lon, waypoints[i + 1].lat)))

	mission_path = shapely.geometry.MultiLineString(coords)

	mission_buffer = mission_path.buffer(0.001) # fixed buffer around 50m 

	return mission_buffer




def compute_mean_delay(ac_list):
	total_delay = 0
	number_of_flight_plan_val_ac = 0
	for ac in ac_list:
		if ac.has_flight_plan_validated:
			total_delay += ac.delay
			number_of_flight_plan_val_ac += 1
	mean_delay = total_delay / number_of_flight_plan_val_ac
	return mean_delay, total_delay, number_of_flight_plan_val_ac




class Waypoint():

	def __init__(self, name, x, y):

		self.name = name
		self.x = x
		self.y = y
		self.lat = None
		self.lon = None