import cv2
import mediapipe as mp
from  detect_gesture import *

# load img and video ####################################################
dark = cv2.imread("data/dark_v2.jpg", cv2.IMREAD_COLOR)
lighten = cv2.imread("data/lighten.jpg", cv2.IMREAD_COLOR)

sun = cv2.VideoCapture("data/sun.mp4")
len_sun_video = int(sun.get(cv2.CAP_PROP_FRAME_COUNT))
sun_list = []
for i in range(len_sun_video):
    ret, frame = sun.read()
    if not ret:
        print("error when loading sun video")
    sun_list.append(frame)
sun.release()

light_rotate = cv2.VideoCapture("data/rotate.mp4")
len_light_video = int(light_rotate.get(cv2.CAP_PROP_FRAME_COUNT))
light_video_list = []
for i in range(len_light_video):
    ret, frame = light_rotate.read()
    if not ret:
        print("error when loading lightening video")
    light_video_list.append(frame)
light_rotate.release()

tears = cv2.VideoCapture("data/blue_tears_v3.mp4")
len_tear_video = int(tears.get(cv2.CAP_PROP_FRAME_COUNT))
tears_video_list = []
for i in range(len_tear_video):
    ret, frame = tears.read()
    if not ret:
        print("error when loading tears video")
    tears_video_list.append(frame)
tears.release()
del frame

# init params ############################################################
display = dark  # which to display
Case = "dark"     # condition

restrict = False    # restrict screen and cannot do hand recognition
end = False     # is sunrise end or not?
zoom = False    # zoom in/out blue tear

sun_video_slide = round(len_sun_video/(180/5))
sun_idx = 0         # # index for sunrise video
light_idx = 0       # index for lighthouse video
tear_idx = 0        # index for blue tear video
cnt = 20            # waiting for the blue tear appearing
count_2min = 200    # the time blue tear disappeared
crop_i, crop_j = 3402, 2702     # crop size; used for zoom in/out blue tear

# Argument parsing #######################################################
args = get_args()

use_static_image_mode = args.use_static_image_mode
min_detection_confidence = args.min_detection_confidence
min_tracking_confidence = args.min_tracking_confidence
use_brect = True

# camera preparation #####################################################
cap_device = args.device
cap_width = args.width
cap_height = args.height

cap = cv2.VideoCapture(cap_device)
cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

# Model load #############################################################
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=1,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
)

keypoint_classifier = KeyPointClassifier()
point_history_classifier = PointHistoryClassifier()

# Read labels ###########################################################
with open('model/keypoint_classifier/keypoint_classifier_label.csv',
          encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [
        row[0] for row in keypoint_classifier_labels
    ]
with open(
        'model/point_history_classifier/point_history_classifier_label.csv',
        encoding='utf-8-sig') as f:
    point_history_classifier_labels = csv.reader(f)
    point_history_classifier_labels = [
        row[0] for row in point_history_classifier_labels
    ]

# Finger gesture history ################################################
history_length = 16
point_history = deque(maxlen=history_length)
finger_gesture_history = deque(maxlen=history_length)

def get_frame(sun_angle):
    global display, end, sun_idx
    detect_main(sun_angle)
    ret, jpeg = cv2.imencode('.jpg', display)

    angle = int(sun_idx/sun_video_slide)
    return jpeg.tobytes(), end, angle

def detect_main(sun_angle):
    global display
    global Case, restrict, end, zoom
    global sun_idx, light_idx, tear_idx, cnt, count_2min, crop_i, crop_j
    
    mode = 0
    key = cv2.waitKey(1)
    number, mode = select_mode(key, mode)

    """ Camera capture """
    ret, image = cap.read()
    if not ret:
        print("cannot open the camera")
    image = cv2.flip(image, 1)  # Mirror display
    debug_image = copy.deepcopy(image)

    # Detection implementation ############################################
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True

    #  ####################################################################
    if results.multi_hand_landmarks is not None:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Bounding box calculation
            brect = calc_bounding_rect(debug_image, hand_landmarks)
            # Landmark calculation
            landmark_list = calc_landmark_list(debug_image, hand_landmarks)

            # Conversion to relative coordinates / normalized coordinates
            pre_processed_landmark_list = pre_process_landmark(landmark_list)
            pre_processed_point_history_list = pre_process_point_history(debug_image, point_history)
            # Write to the dataset file
            logging_csv(number, mode, pre_processed_landmark_list, pre_processed_point_history_list)

            # Hand sign classification
            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)

            if hand_sign_id == 0 and (not restrict):
                # sunset
                Case = "sunset"
            elif hand_sign_id == 1 and (not restrict):
                """ turn on the light """
                Case = "lighthouse"
            elif hand_sign_id == 2 and (not restrict):
                """ turn off the light """
                Case = "dark"
            elif hand_sign_id == 3 and (not restrict):
                """ blue tears appear """
                # down count for display the video
                if cnt > 0:
                    cnt -= 1
                elif cnt == 0:
                    Case = "pray"
                    restrict = True
            elif hand_sign_id == 5 and Case == "pray":
                """ zoom in blue tear """
                zoom = True
            elif hand_sign_id == 6 and Case == "pray":
                zoom = False

            # Finger gesture classification
            finger_gesture_id = 0
            point_history_len = len(pre_processed_point_history_list)
            if point_history_len == (history_length * 2):
                finger_gesture_id = point_history_classifier(pre_processed_point_history_list)

            # Calculates the gesture IDs in the latest detection
            finger_gesture_history.append(finger_gesture_id)
            most_common_fg_id = Counter(finger_gesture_history).most_common()
            
            # Drawing part
            debug_image = draw_bounding_rect(use_brect, debug_image, brect)
            debug_image = draw_landmarks(debug_image, landmark_list)
            debug_image = draw_info_text(
                debug_image,
                brect,
                handedness,
                keypoint_classifier_labels[hand_sign_id],
                point_history_classifier_labels[most_common_fg_id[0][0]],
            )
    else:
        point_history.append([0, 0])
    #cv2.imshow('Hand Gesture Recognition', debug_image)

    """ display on the screen """
    if Case == "sunset":
        restrict = True
        display = sun_list[sun_idx]
        cv2.waitKey(1)
        if (sun_idx < len_sun_video-1):
            sun_idx += 1
        else:
            sun_idx = 0
            Case = "reverse"
            #restrict = False
    elif Case == "dark":
        display = dark
    elif Case == "lighthouse":
        display = light_video_list[light_idx]
        cv2.waitKey(1)
        if (light_idx < len_light_video-1):
            light_idx += 1
        else:
            light_idx = 0
    elif Case == "pray":
        restrict = True
        count_2min -= 1
        if count_2min == 0:     # time out
            cnt = 20
            count_2min = 200
            Case = "dark"
            restrict = False
            zoom = False
        else:       # play blue tear video
            if zoom: 
                pts1, pts2 = zoomin(1122, 891, crop_i, crop_j)
                M = cv2.getPerspectiveTransform(pts1, pts2)
                dst = cv2.warpPerspective(tears_video_list[tear_idx], M, (1024, 813))
                display = dst
                cv2.waitKey(10)
                if (tear_idx < len_tear_video-1):
                    tear_idx += 1
                else:
                    tear_idx = 0
                # 972=3402-243*10; 772=2702-193*10 (3402:2702=243:193)
                if crop_i > 972 and crop_j > 772:
                    crop_i -= 243
                    crop_j -= 193
            else:
                pts1, pts2 = zoomin(1122, 891, crop_i, crop_j)
                M = cv2.getPerspectiveTransform(pts1, pts2)
                dst = cv2.warpPerspective(tears_video_list[tear_idx], M, (1024, 813))
                display = dst
                cv2.waitKey(10)
                if (tear_idx < len_tear_video-1):
                    tear_idx += 1
                else:
                    tear_idx = 0

                if crop_i < 3402 and crop_j < 2702:
                    crop_i += 243
                    crop_j += 193
    elif Case == "reverse":
        if sun_angle == 0:  # revserse to 0 degree, start again
            Case = "dark"
            end = False
            restrict = False
        else:       # waitin for revsering back
            end = True
            restrict = True
    else:
        pass