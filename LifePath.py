#!/usr/bin/env python
# -*- coding: latin-1 -*-

print "Importing libraries..."
import sys, os, imageio, copy, urllib2, json, re
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from mpl_toolkits.basemap import Basemap
from PIL import Image
from haversine import haversine
from colour import Color
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation) # who cares about warnings amirite?
print "Imports done."

# settings
minDist = 100.0 # minimum distance to be included
saveOn = True # don't change this, use the argument -plot or -plotall
showLabels = False # toggle labels

# you have to tweak these to get the kind of aspect ratio you want
# corners = [-10,70,-140,160,20] # a bit smaller
corners = [-1,70,-130,150,20] # lat lower left, lat upper right, lon lower left, lon upper right, lat truth (see https://matplotlib.org/basemap/api/basemap_api.html)



###########################################################################################
# functions to do stuff
###########################################################################################

# (unused) function to read data from JSON file
def getDatFromJSON(jsonFileName):
	print " > Reading data from '"+jsonFileName+"' ..."
	data_file = open(jsonFileName,'r')
	data = json.load(data_file)
	return data

# function to read data from KML file
def getLocationsFromKML(kmlFileName):
	locations = []
	kmlFile = open(kmlFileName,'r')
	for line in kmlFile:
		if "gx:coord" in line:
			locationString = str(line).replace("<gx:coord>","").replace("</gx:coord>","").strip()
			values = locationString.split(" ") # lat, lon, something
			locations.append((float(values[0]),float(values[1])))
	return locations

# function to read data from DAT file
def getLocationsFromDAT(datFileName):
	locations = []
	datFile = open(datFileName,'r')
	for line in datFile:
		locationString = str(line).replace("(","").replace(")","").strip()
		values = locationString.split(",") # TODO ordering?
		locations.append((float(values[0]),float(values[1])))
	return locations

# get rid of points closer than a minimum distance
def trimLocations(locations, minDistance=minDist):
	previousLocation = (9999999,9999999)
	trimmedLocations = []
	for location in locations:
		dist = haversine(previousLocation,location)
		if dist > minDistance:
			trimmedLocations.append(location)
			previousLocation = location
	return trimmedLocations

# plot geodesics on map:
def drawCurvesOnMap(darkMap, lightMap, coords):
	
	# yellow colour
	yel = Color("#FFFF99").hex_l

	if saveOn:
		# folder to hold images
		print " > Creating directory 'images'..."
		os.mkdir("images")
	
	# track labelled cities
	lastPlotName = ""
	plottedCities = []
	citylats = []
	citylons = []

	# loop over coordinates
	(prevLat,prevLon) = coords[0]
	ncoords = len(coords)
	for i, coord in enumerate(coords[1:]):
		num = ("000000"+str(i))[-5:]
		lastPlotName = num
		percent = 100*float(i)/float(ncoords)
		
		# save map as it is
		if saveOn:
			plt.savefig("images/map"+num+".png", bbox_inches='tight')
		
		# prepare next geodesic
		thisLat = coord[0]
		thisLon = coord[1]
		
		print " > Plotting geodesic "+str(i)+" of "+str(ncoords)+" ("+str(percent)[:4]+"% complete): ("+str(prevLat)+", "+str(prevLon)+") ---> ("+str(thisLat)+", "+str(thisLon)+")"
		"""
		# plot highlighted geodesic
		if saveOn:
			lightMap = copy.copy(darkMap)
			#lightMap.drawgreatcircle(thisLat, thisLon, prevLat, prevLon, linewidth=1.0,color="white",alpha=1.0)
			plt.savefig("images/map"+num+"_highlight.png", bbox_inches='tight') # save highlight plot
		"""
		# plot less glowy geodesic on top
		dist = haversine((prevLat, prevLon),(thisLat, thisLon))
		darkMap.drawgreatcircle(thisLat, thisLon, prevLat, prevLon, linewidth=4.0,color=yel,alpha=0.1)
		darkMap.drawgreatcircle(thisLat, thisLon, prevLat, prevLon, linewidth=3.0,color=yel,alpha=0.1)
		darkMap.drawgreatcircle(thisLat, thisLon, prevLat, prevLon, linewidth=2.0,color=yel,alpha=0.1)
		darkMap.drawgreatcircle(thisLat, thisLon, prevLat, prevLon, linewidth=1.0,color="white",alpha=0.3)
		if dist > 500 and showLabels:
			city = getCityFromLatLon(coord)
			if city != "FAILFAIL" and city not in plottedCities:
				addLabel = True
				for i, citylat in enumerate(citylats):
					otherLat = citylats[i]
					otherLon = citylons[i]
					thisDist = haversine((otherLat,otherLon),(thisLat,thisLon))
					if thisDist < 500:
						addLabel = False
				if addLabel:
					print "> Adding city label for "+city
					plottedCities.append(city)
					citylons.append(thisLon)
					citylats.append(thisLat)
					cityX,cityY = darkMap(citylats,citylons)
					darkMap.plot(cityX,cityY,'bo',markersize=4,color=yel,alpha=0.3)	 # from https://peak5390.wordpress.com/2012/12/08/matplotlib-basemap-tutorial-plotting-points-on-a-simple-map/			
					for cityname, xpt, ypt in zip(plottedCities,cityX,cityY):
						plt.text(xpt,ypt,cityname,bbox={'facecolor':yel, 'alpha':1.0, 'pad':3,'edgecolor':'none'})


		# setup for next point
		(prevLat,prevLon) = (thisLat,thisLon)
		

	if saveOn:
		# pad 9 extra frames at the end
		print " > Padding with 9 extra frames at the end..."
		for numextra in range(1,9):
			plt.savefig("images/map"+lastPlotName+str(numextra)+".png", bbox_inches='tight')




###########################################################################################
# HERE.com geocoder API interface
###########################################################################################
# documentation at https://developer.here.com/documentation/geocoder/topics/example-reverse-geocoding.html
def getCityFromLatLon(coord):
	lat = str(coord[0])
	lon = str(coord[1])
	radius = str(250) # metres
	URLstub = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?app_id=HoLTRv9D0X8fGBdrmFJb&app_code=3kqpd9yjE9LapimxHOmSzw&mode=retrieveAddresses"
	URLfull = URLstub+"&prox="+lon+","+lat+","+radius
	response = urllib2.urlopen(URLfull)
	info = json.load(response)
	try:
		thisCity = info["Response"]["View"][0]["Result"][0]["Location"]["Address"]["City"]
		chinese = re.findall(ur'[\u4e00-\u9fff]+', thisCity) # check for chinese characters, which don't play well with pyplot
		if len(chinese) > 0:
			return "FAILFAIL"
		return thisCity
	except Exception, e:
		return "FAILFAIL"




###########################################################################################
# code runs from here
###########################################################################################
inputs = sys.argv
if len(inputs) < 2:
	print "------------------------------------------------------------------------------------------------------------------"
	print " NEED TO PROVIDE ARGUMENTS"
	print "------------------------------------------------------------------------------------------------------------------"
	print " FLAG:        PURPOSE:                                            EXAMPLE USAGE:"
	print " -shorten     To prepare a shorter list of location data          ./LifePath.py -shorten locations.kml"
	print " -plot        To generate a set of images for GIF-making          ./LifePath.py -plot locationsSHORT.dat"
	print " -gif         To generate a GIF from the set of images            ./LifePath.py -gif images/*png"
	print " -plotall     To generate a single image that can't be GIF'd      ./LifePath.py -plotall locationsSHORT.dat"
	print "------------------------------------------------------------------------------------------------------------------"
	quit()
elif "-shorten" in inputs:
	mode = "shorten"
	for arg in inputs:
		if arg.endswith(".kml"):
			kmlFileName = arg			
elif "-plot" in inputs:
	mode = "plot"
	for arg in inputs:
		if arg.endswith(".dat"):
			datFileName = arg			
elif "-plotall" in inputs:
	mode = "plot"
	saveOn=False
	for arg in inputs:
		if arg.endswith(".dat"):
			datFileName = arg			

elif "-gif" in inputs:
	mode = "gif"
else:
	print "> Unrecognised argument, exiting."





###########################################################################################
# shorten mode (trims list of locations to only those >50km apart)
###########################################################################################
if mode is "shorten":
	print " > Getting locations from long KML file '"+kmlFileName+"'..."
	locs = getLocationsFromKML(kmlFileName)
	print " > Total number of locations = "+str(len(locs))
	print " > Trimming locations to those separated by >"+str(minDist)+"km..."
	trimmedLocs = trimLocations(locs)
	trimmedLocs.reverse() # Google gives top->bottom with new at the top, reverse to make chronological
	print " > Number of distinct locations = "+str(len(trimmedLocs))
	outputFileName = kmlFileName.replace(".kml", "SHORT.dat")
	print " > Saving to '"+outputFileName+"'..."
	outputFile = open(outputFileName,'w')
	for trimmedLoc in trimmedLocs:
		outputFile.write(str(trimmedLoc)+"\n")
	outputFile.close()
	quit()






###########################################################################################
# plot mode
###########################################################################################
if mode is "plot":
	# get trimmed locations
	print " > Getting locations from shortened file '"+datFileName+"'..."
	trimmedLocs = getLocationsFromDAT(datFileName)
	print " > Number of distinct locations = "+str(len(trimmedLocs))

	# create figure for map
	fig = plt.figure(figsize=(30,15)) # figure 2?

	# colour scale: water / lines / land
	#colours = ["midnightblue","black","darkolivegreen"] # bluegren
	#colours = ["darkslategrey","darkslategrey","lightgrey"] # greys
	#colours = ["midnightblue","midnightblue","cornflowerblue"] # blues
	darkassblue = Color("#000222").hex_l
	darkassgrey = Color("#727272").hex_l
	colours = [darkassblue,darkassblue,darkassgrey] # darkAF
	water = colours[0]
	lines = colours[1]
	land = colours[2]

	# draw map and curves
	print " > Creating background map..."
	worldMap = Basemap(projection='merc',llcrnrlat=corners[0],urcrnrlat=corners[1],llcrnrlon=corners[2],urcrnrlon=corners[3],lat_ts=corners[4],resolution='i')
	worldMap.drawmapboundary(fill_color=water) # ocean colour
	worldMap.fillcontinents(color=land,lake_color=water) # fill continents, set lake color same as ocean colour
	worldMap.drawcoastlines(linewidth=.25, color=lines)
	worldMap.drawcountries(linewidth=.25, color=lines)
	highlightMap = copy.copy(worldMap)
	
	print " > Adding geodesics..."
	drawCurvesOnMap(worldMap, highlightMap, trimmedLocs)
	if not saveOn:
		plt.savefig("LifePath.png", bbox_inches='tight')
	print " > Finished!"
	quit()






###########################################################################################
# GIF mode
###########################################################################################
if mode is "gif":
	images = []
	N = len(inputs)-2
	print " > GIF maker: converting "+str(N)+" images to GIF..."
	for i, filename in enumerate(inputs):
		if not str(filename).endswith(".png"):
			continue

		print " > Generating GIF: processing image "+str(i)+" of "+str(N)+" ("+str(round(float(100*i)/float(N),2))+"% complete)"
		images.append(imageio.imread(filename))
	print " > Saving GIF (this could take a while!)..."
	imageio.mimsave('LifePath.gif', images) # post about imageio: https://stackoverflow.com/a/35943809/4367240
	print " > Saved as 'LifePath.gif'!"
	quit()






