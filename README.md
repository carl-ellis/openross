# The Open BobRoss image processing service

The Open BobRoss image service provides a way of serving dynamically resized images from amazon S3 in a way that is fast, efficient, and auto-scales with traffic.

## Motivation
At Lyst, we scrape, and have scraped, millions of products that all have at least one image.
In our infancy, we saved any product image into 10 preset sizes, and then chose the nearest one to our needs.
As we grew, this solution was no longer optimum for the levels of traffic we were experiencing and nor was it appropriate for our mobile app.

To address this, we created our BobRoss imaging service which generates a new size on the fly when we need it.
These images are then cached in CloudFront, effectively meaning that Bobross only paints his subjects once, but with more flexibility on dimensions and, in the future, effects.

Since we rolled BobRoss out into production on an auto-scaling amazon cluster, we have decreased page load times and lowered our bandwidth usage by ensuring we only serve images of the exact size.

As this was so useful for us, we have decided to open source our solution, as the Open BobRoss service, or OpenRoss.

## Requirements

* Python 2.7
* Twisted 13.1
* GraphicsMagick 1.3.19
* nginx 1.6.0

## Installation for Testing/Debug

1. Clone openross
2. Run `python setup.py install`
3. Change directory into the inner openross dir
4. Add your AWS credentials to `~/.openross.py`
```python
AWS_ACCESS_KEY_ID = "MYKEYID"
AWS_SECRET_ACCESS_KEY = "MYSECRETKEY"
IMAGES_STORE = 'MYBUCKET'
DEBUG = True
```
5. Run `twisted -n openross`
6. Configure nginx using the `nginx.conf-snippet` file for help
7. Start nginx
8. Navigate to `http://localhost/path/to/image/in/your/s3/bucket`

## Usage

OpenRoss uses a very simple URL scheme http://host/WIDTH/HEIGHT/MODE/path/to/image

Width/height pairs can be white listed in the settings file, or the white list can be turned off for internal development use.

OpenRoss comes bundled with 3 modes: crop, resize, and resizecomp.
Crop does what you think it does, and crops an image into a given size.
Resize does a simple box resize.
ResizeComp does a resize, followed by compostiting the image onto a white background---which ensures the image is always an expected size.

New modes can be added easily in `image_modes.py` and blurring, colourising, desaturation are good starting points if you require them.


## FAQS

**What if I find a bug?**

If you find a bug, please make an issue or a pull request with steps on how to reproduce, screenshots, and (if possible) a codefix.
We will be active in monitoring this project.

**What performance characteristics does OpenRoss have?**

We have a blog post talking about performance in more depth available at BLAHBLAH where we go into detail, however at a rate of 110-120 req/s we have a mean responce time of 200ms.
Bear in mind, that we use CloudFront, so 110-120 req/s are only requests for new images that are not in the cache or have recently expired.

**What happens if I change how an mode works, but use CloudFront?**

If you have set a sensible expiry in your cache (we use a week) the changes will go into effect for new images immediately, and will take hold in old images as they are expunged from the cache.
If you have set a larger expirey time for your cache, then you will have to individually remove them from Cloudfront, which is a tedius and timeconsuming process.

**What if I don't store my images in S3?**

If you dont use Amazon S3 to store your images, but still want to use OpenRoss, fear not!

Modify your `~/.openross.py' to turn off the S3 Downloader pipeline and set the internal cache location to your media director:
```python
AWS_ACCESS_KEY_ID = "MYKEYID"
AWS_SECRET_ACCESS_KEY = "MYSECRETKEY"
IMAGES_STORE = 'MYBUCKET'
DEBUG = True         

# Local media changes
IMAGE_PIPELINES = [
    'pipeline.cache_check.CacheCheck',
    'pipeline.resizer.Resizer',
    'pipeline.cacher.Cacher',
]
CACHE_LOCATION = '/<path>/<to>/<media>/'
```

Next is to modify your nginx root to be where you keep your images, so in our configuation snippet change `root /srv/http/cache;` to `root /<path>/<to>/<media>/;`

This essentially uses your media directory as OpenRoss' cache, so it never has to go to S3 and works as normal.
