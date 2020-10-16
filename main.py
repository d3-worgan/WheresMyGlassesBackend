import argparse
import os
from modules.backend_manager import BackendManager

parser = argparse.ArgumentParser(description='Run the object location system')
parser.add_argument("--model",
                    help="Specify the name of the detection model e.g. yolov3, yolo9000, yoloCSP, open_images, wmg_v3, wmg_SPP, wmg_custom_anchors",
                    required=False, type=str, default="yoloCSP")
parser.add_argument("--location", help="Specify the path to base location of the detection models", required=False,
                    type=str, default=r"/media/dan/UltraDisk/wmg_detection_models")
parser.add_argument("--interval", help="Specify an interval to take snapshots in seconds (else fast as possible)",
                    required=False, type=float, default=0)
parser.add_argument("--darknet", help="True to use darknet implementation or False for openCV", required=False,
                    type=bool, default=True)
parser.add_argument("--mqtt", help="False to switch off connection to MQTT", required=False, type=bool, default=False)
parser.add_argument("--broker", help="Specify the IP address of the MQTT broker", required=False, type=str,
                    default="192.168.0.159")
parser.add_argument("--display", help="True to display the output of the detection streams", required=False, type=bool,
                    default=True)
parser.add_argument("--resolution", help="Specify input res e.g. 1080, 720", required=False, type=int, default=1080)
parser.add_argument("--flip", help="True to vertically flip the camera image", required=False, type=bool, default=False)


if __name__ == "__main__":
    """
    Entry point for the backend system. Initialise parameters etc here....
    """
    args = parser.parse_args()

    od_model = args.model
    model_folder = args.location
    snapshot_interval = args.interval
    use_darknet = args.darknet
    #use_mqtt = args.mqtt
    use_mqtt = True
    print(use_mqtt)
    broker = args.broker
    display_output = args.display
    res = args.resolution
    flip_cameras = args.flip

    assert os.path.exists(model_folder), "Couldn't find the detection models folder..."
    # assert od_model is "yolov3" or od_model is "yolo9000" or od_model is "yoloCSP" or od_model is "open_images" or od_model is "wmg_v3" or od_model is "wmg_anchors" or od_model is "wmg_spp", "Invalid model specified"
    assert snapshot_interval >= 0, "interval must be float greater than 0"
    assert res == 720 or res == 1080, "Resolution must be 720 or 1080"

    resolution_width = 1280
    resolution_height = 720
    frame_rate = 30

    if res == 720:
        resolution_width = 1280
        resolution_height = 720
        frame_rate = 30
    elif res == 1080:
        resolution_width = 1920
        resolution_height = 1080
        frame_rate = 30
    else:
        print("WARNING: Not a valid resolution")

    print("Detection model     : " + od_model)
    print("Model base directory: " + model_folder)
    print("Snapshot interval   : " + str(snapshot_interval))
    print("Darknet             : " + str(use_darknet))
    print("Connect MQTT        : " + str(use_mqtt))
    print("MQTT Broker         : " + str(broker))
    print("Display on          : " + str(display_output))
    print("Input Resolution    : " + str(res))

    backend_manager = BackendManager(od_model, model_folder, resolution_width, resolution_height, frame_rate, flip_cameras, broker,
                                     "BackendManager", snapshot_interval, use_darknet, use_mqtt, display_output)

    try:
        backend_manager.idle()
    except KeyboardInterrupt:
        print("User quit.")
    finally:
        print("done")
