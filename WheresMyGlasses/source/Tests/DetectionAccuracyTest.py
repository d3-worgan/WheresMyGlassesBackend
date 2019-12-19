from WheresMyGlasses.source.search_assistant.ObjectLocator import ObjectLocator
import cv2


ol = ObjectLocator(100)

# Take 100 snapshots with 3 key items
# Run through snapshots and total number of detections for each item
# Run through snapshots and total number of locations for each item
# Score out of 100

i = 0
while i < 100:
    ol.take_snapshot(i)
    ol.snapshot_history[-1].print_snapshot()
    i += 1

print("Snapshots " + str(len(ol.snapshot_history)))

# Count detections
d_bottle = 0
d_mouse = 0
d_wine_glass = 0

# Count locations
l_bottle = 0
l_mouse = 0
l_wine_glass = 0

for snap in ol.snapshot_history:
    print()
    snap.print_details()

    # Count detections
    for detection in snap.objects_detected:
        if detection.label == "bottle":
            d_bottle += 1
        if detection.label == "mouse":
            d_mouse += 1
        if detection.label == "wine glass":
            d_wine_glass += 1

    # Count locations
    for location in snap.objects_located:
        print("loco")
        if location.object1 == "bottle" and location.object2 == "diningtable":
            l_bottle += 1
        if location.object1 == "mouse" and location.object2 == "diningtable":
            l_mouse += 1
        if location.object1 == "wine glass" and location.object2 == "diningtable":
            l_wine_glass += 1

print()
print("Detections")
print("bottle     " + str(d_bottle))
print("mouse      " + str(d_mouse))
print("wine glass " + str(d_wine_glass))
print()
print("Locations")
print("bottle     " + str(l_bottle))
print("mouse      " + str(l_mouse))
print("wine glass " + str(l_wine_glass))


cv2.destroyAllWindows()
print("Done.")
