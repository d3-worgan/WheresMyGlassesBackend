import pyrealsense2 as rs

pipe = rs.pipeline()
profile = pipe.start()
try:
    while True:
        frames = pipe.wait_for_frames()

        for f in frames:

finally:
    pipe.stop()