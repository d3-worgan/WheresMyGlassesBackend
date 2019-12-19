from WheresMyGlasses.source.search_assistant.ObjectLocator import ObjectLocator
import cv2

ol = ObjectLocator(100)

i = 0
while True:
    ol.take_snapshot(i)
    ol.snapshot_history[-1].print_snapshot()
    i += 1

print("Snapshots " + str(len(ol.snapshot_history)))

for snap in ol.snapshot_history:
    print()
    snap.print_details()


cv2.destroyAllWindows()
print("Done.")
