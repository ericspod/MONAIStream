# MONAI Stream

Experimental revival of this repo, please comment but don't expect anything to be final or even work.

## Docker

1. Build: `docker build -t monaistream .`

2. Run `xhost +local:docker` to grant X permissions to Docker containers

3. Run: `docker run -ti --rm -e DISPLAY --gpus device=1 -v $PWD:/opt/monaistream monaistream`


## Numpy Transform Test

```sh
PYTHONPATH=$PWD GST_PLUGIN_PATH=$PWD/monaistream/gstreamer gst-launch-1.0 \
    videotestsrc num-buffers=1 ! video/x-raw,width=1280,height=720 ! \
    numpyinplacetransform ! jpegenc ! multifilesink location="img_%06d.jpg"
```
