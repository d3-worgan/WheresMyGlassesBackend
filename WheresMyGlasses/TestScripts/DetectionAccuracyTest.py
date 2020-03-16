from object_locator import ObjectLocator
import cv2

"""
Test to measure the utility of the object locator.
1. Specify a number of items to locate
2. Take a test sample i.e. x amount of snapshots.
3. Count the number times each object was located or detected in a snapshot.
4. Add the total number of locations divided by number of objects for a score.
4. A Test is passed if the score is 80 out of 100.
"""

test_sample = 13
pass_rate = 80
ol = ObjectLocator(test_sample)


target_objects = []

b = ["bottle", 0, 0]
m = ["mouse", 0, 0]
w = ["wine glass", 0, 0]
dog = ["dog", 0, 0]

target_objects.append(b)
# target_objects.append(m)
# target_objects.append(w)
#target_objects.append(dog)

locations = []

d = "diningtable"
bed = "bed"
person = "person"

#locations.append(d)
#locations.append(bed)
locations.append(person)


# Take samples
i = 0
while i < test_sample:
    ol.take_snapshot(i)
    ol.add_snapshot_to_history(i)
    ol.snapshot_history[-1].print_snapshot()
    i += 1
cv2.destroyAllWindows()

# Collect results
for snap in ol.snapshot_history:
    #print()
    #snap.print_details()

    # Count detections
    for detection in snap.objects_detected:
        for target in target_objects:
            if detection.label == target[0]:
                target[1] += 1

    # Count locations
    for location in snap.objects_located:
        for target in target_objects:
            if location.object1 == target[0] or location.object2 == target[0]:
                target[2] += 1

# Calculate results
detection_score = 0
location_score = 0
total_score = 0
for target in target_objects:
    detection_score += target[1]
    location_score += target[2]

total_score = (detection_score + location_score / len(target_objects)) / 2
total_score = 100 * total_score / test_sample
detection_score = detection_score / len(target_objects)
detection_score = 100 * detection_score / test_sample
location_score = location_score / len(target_objects)
location_score = 100 * location_score / test_sample

# Calculate Pass/Fail
total_pass = False
if total_score >= pass_rate:
    total_pass = True

location_pass = False
if location_score >= pass_rate:
    location_pass = True

detection_pass = False
if detection_score >= pass_rate:
    detection_pass = True

print()
print("Results")
for target in target_objects:
    print(target)

# Output results
print()
print("Pass rate " + str(pass_rate))
print("Total Score " + str(total_score))
print("Total Pass " + str(total_pass))
print("Location Score " + str(location_score))
print("Location Pass " + str(location_pass))
print("Detection Score " + str(detection_score))
print("Detection Pass " + str(detection_pass))
print("Done.")
