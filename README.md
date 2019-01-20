# LifePath

## How to run it

1. Follow [these instructions from Google](https://support.google.com/accounts/answer/3024190) to "checkout" your full location history as KML.

2. Clone this repo and then run [LifePath.py](./LifePath.py) with any of these 4 flags:

Flag | Purpose | Example Usage
--- | --- | ---
`-shorten` | To prepare a shorter list of location data | `./LifePath.py -shorten locations.kml`
`-plotall` | To generate a single image with one LifePath | `./LifePath.py -plotall locationsSHORT.dat`
`-plot` | To generate a set of images for GIF-making | `./LifePath.py -plot locationsSHORT.dat`
`-gif` | To generate a GIF from the set of images | `./LifePath.py -gif images/*png`

3. The source code of [LifePath.py](./LifePath.py) has a few settings at the top that can be tweaked.



---



## Description from the [Devpost submission](https://devpost.com/software/lifepath)

### Inspiration
I realised I've carried a smartphone since 2011 so my location history was pretty reliably captured since then. You can download this from Google but it's just a block of coordinates in KML, so I wanted a visualisation. I thought a single unbroken line would be an elegant way to see where I'd been, like a wake or trail of footprints.

### What it does

1. **Shorten the list of locations:** [Google allows you to "checkout" your full location history as KML](https://support.google.com/accounts/answer/3024190). For me, this resulted in over 450,000 pairs of latitudes and longitudes. Most of these were very close together (e.g. home, office, supermarket, repeated *ad nauseum*). Running *LifePath* with the `-shorten` flag will tidy up the huge KML file that Google gives you and reduce it to locations separated by at least 100km. For me, that stripped it down to just over 200 locations.

2. **Plot geodesics between all those points:** a [geodesic](https://en.wikipedia.org/wiki/Geodesic) is the path of minimum distance across a curved surface (hence on flat map projections, flight paths appear curved). Using the `-plotall` flag will produce a single map with a single LifePath for all the input data. City name labels are optional. Using the `-plot` flag will produce a folder of images with each additional geodesic (which can then be combined into a GIF). This is what the combined LifePath looks like (higher quality version on [Imgur](https://i.imgur.com/3fVL6ar.png)): ![Alt Text](https://i.imgur.com/3fVL6ar.png)

3. **Animate the LifePath in a GIF**: all the geodesic maps created using the `-plot` flag can be combined into a GIF using the `-gif` flag. The result looks like this (higher quality version on [Imgur](https://i.imgur.com/Y4zwgfR.gifv)):

![Devpost-compressed GIF](https://i.imgur.com/ysMfohO.gif)

### How I built it
Once I had the first basic *LifePath* I realised I wanted to add some meaningful labels, but Google's data only contains geocoordinates. This is where [HERE.com's API](https://developer.here.com/) came in. I used [their reverse geocoding API](https://developer.here.com/documentation/geocoder/topics/example-reverse-geocoding.html) to extract the city names of some well-separated points, then passed those to my plotting routine to add labels (higher quality version on [Imgur](https://i.imgur.com/ujE5INg.png)): ![Alt Text](https://i.imgur.com/ujE5INg.png)

### Challenges I ran into
Manually adding a bunch of coordinates from 10-20 family holidays before I had a smartphone took longer than I thought it would. However, in the end I think it's worth it to see my entire LifePath traced from birth, including childhood travel.

### Accomplishments that I'm proud of
Implementing the labels in a couple of hours flat - HERE.com's API was much simpler to implement than I expected.

### What I learned
I learned out how to handle JSON data, as that was the format the HERE.com API supplied its results in.

### What's next for LifePath
Interactivity - rather than a static image, it would be nice to be able to zoom in and click on locations to see the dates when I was there.
