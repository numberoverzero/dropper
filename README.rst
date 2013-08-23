dropper
=============================

Based on:

blog post http://charlesleifer.com/blog/using-python-to-generate-awesome-linux-desktop-themes/
gist https://gist.github.com/coleifer/33484bff21c34644dae1


Usage
----------------

To get dominant colors as a list of (r,g,b) lists::

    dominant_colors(path, k, min_diff, speed)

path is a file location

k is the number of colors to select

speed is the inverse of quality, so speed of 2 will scale a 1920x1080 image to 960x540 before processing.  Higher numbers are faster.

min_diff is the maximum change in cluster centers that will terminate the algorithm.  Higher numbers are faster.

To render a list of colors::

    render_colors(colors, dst)

colors is a list of (r,g,b) lists (the output of dominant_colors) and dst is a file to save an html rendering of the colors to.

The output of render_colors is an html file such as::

	<html>
	<head>
	<link rel="stylesheet" type="text/css" href="http://reset5.googlecode.com/hg/reset.min.css">
	<style>
		img {
		  max-width: 100%;
		  height: auto;
		}
		.box {
				max-width: 978px;
				min-height: 70px;
				max-height: 70px;
				margin: 0 auto;
				margin-top: 10px;
				margin-bottom: 10px;
			}
		.box .src {
			max-height: 978px;
		}
	</style>
	</head>
	<body>
	<div class='box' style='background-color: #1f1d0b'></div>
	<div class='box' style='background-color: #64691c'></div>
	<div class='box' style='background-color: #d1cc2d'></div>
	<div class='box' style='background-color: #f7f7ce'></div>
	<div class='box src'><img src='~/Downloads/rainforest.jpg'></div>
	</body>
	</html>

To render a palette from a source image, use::

    full_render(src, dst, k, min_diff, speed)
