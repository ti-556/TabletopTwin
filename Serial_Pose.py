import math
import cv2
import mediapipe as mp
import time
import serial

ser = serial.Serial("COM4", 9600, timeout = None)
time.sleep(2.0)

mp_drawing = mp.solutions.drawing_utils #landmarking tool
mp_drawing_styles = mp.solutions.drawing_styles #landmarking style
mp_pose = mp.solutions.pose #pose detection model
 
def round(number,increment):
    N = number / increment
    M = number // increment
    if (N - M > 0.5):
      round = (M + 1) * increment
    else:
       round = M * increment
    return round

def deg2ics(angle):
  icsangle = 29.63 * angle + 3470.37037
  return(icsangle)

def deg2ics_90(angle):
  icsangle = 29.63 * abs(80 + angle) + 3470.37037
  return(icsangle)

def deg2ics_face(angle):
  icsangle = 29.63 * angle + 7500
  if icsangle < 7000:
    icsangle = 7000
  elif icsangle > 8000:
    icsangle = 8000
  return icsangle

def deg2ics_roll(angle):
  icsangle = 25 * angle + 3470.37037
  if icsangle < 8000:
    icsangle = 8000
  elif icsangle > 7000:
    icsangle = 7000
  return(icsangle)

def getAngle(A, B, C):
    AB = [B[0] - A[0], B[1] - A[1]]
    BC = [C[0] - B[0], C[1] - B[1]]

    # Dot product
    dot_product = AB[0]*BC[0] + AB[1]*BC[1]

    # Magnitudes
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    magnitude_BC = math.sqrt(BC[0]**2 + BC[1]**2)

    # Cosine of angle
    cos_angle = dot_product / (magnitude_AB * magnitude_BC)

    # Angle in radians and then in degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = angle_radians * (180 / math.pi)

    angle_degrees = round(angle_degrees, 1)

    return angle_degrees

def getAngle_YZ(A, B, C):
    AB = [B[1] - A[1], B[2] - A[2]]
    BC = [C[1] - B[1], C[2] - B[2]]
    # Dot product
    dot_product = AB[0]*BC[0] + AB[1]*BC[1] 

    # Magnitudes
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    magnitude_BC = math.sqrt(BC[0]**2 + BC[1]**2)

    # Cosine of angle
    cos_angle = dot_product / (magnitude_AB * magnitude_BC)

    # Angle in radians and then in degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = angle_radians * (180 / math.pi)

    angle_degrees = round(angle_degrees, 1)

    return angle_degrees

def getAngle_face_yaw(A, B, C, D):
    AB = [B[0] - A[0], B[2] - A[2]]
    CD = [D[0] - C[0], D[2] - C[2]]
    AC = [C[0] - A[0], C[2] - A[2]]
    BD = [D[0] - B[0], D[2] - B[2]]
    # Dot product
    dot_product = AB[0]*CD[0] + AB[1]*CD[1]

    # Magnitudes
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    magnitude_CD = math.sqrt(CD[0]**2 + CD[1]**2)

    # Cosine of angle
    cos_angle = dot_product / (magnitude_AB * magnitude_CD)

    # Angle in radians and then in degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = angle_radians * (180 / math.pi)

    angle_degrees = round(angle_degrees, 1)

    if(AC > BD):
       angle_degrees = -1 * angle_degrees

    return angle_degrees

def getAngle_face_roll(A, B, C, D):
    AB = [B[0] - A[0], B[1] - A[1]]
    CD = [D[0] - C[0], D[1] - C[1]]
    AC = [C[0] - A[0], C[1] - A[1]]
    BD = [D[0] - B[0], D[1] - B[1]]

    # Dot product
    dot_product = AB[0]*CD[0] + AB[1]*CD[1]

    # Magnitudes
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    magnitude_CD = math.sqrt(CD[0]**2 + CD[1]**2)
    magnitude_AC = math.sqrt(AC[0]**2 + AC[1]**2)
    magnitude_BD = math.sqrt(BD[0]**2 + BD[1]**2)

    # Cosine of angle
    cos_angle = dot_product / (magnitude_AB * magnitude_CD)

    # Angle in radians and then in degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = angle_radians * (180 / math.pi)

    angle_degrees = round(angle_degrees, 1)

    if(A[1] > B[1]):
       angle_degrees = -1 * angle_degrees

    return angle_degrees

def getAngle_Armpit(hip, shoulder, elbow):
    A = hip
    B = shoulder
    C = elbow

    AB = [-(B[1] - A[1]), B[0] - A[0], 0] #cross product of (0, 0, 1) and hip --> shoulder vector
    BC = [C[0] - B[0], C[1] - B[1], C[2] - B[2]]

    # Dot product
    dot_product = AB[0]*BC[0] + AB[1]*BC[1] + AB[2]*BC[2]

    # Magnitudes
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2 + AB[2]**2)
    magnitude_BC = math.sqrt(BC[0]**2 + BC[1]**2 + BC[2]**2)

    # Cosine of angle
    sin_angle = dot_product / (magnitude_AB * magnitude_BC)

    # Angle in radians and then in degrees
    angle_radians = math.asin(sin_angle)
    angle_degrees = angle_radians * (180 / math.pi)

    angle_degrees = round(angle_degrees, 1)

    return abs(angle_degrees)


cap = cv2.VideoCapture(0) #initializing video capture object from webcam
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose: #initializing pose model
  while cap.isOpened(): #while loop until terminated with "esc"
    success, image = cap.read() #retrieve frame
    if not success:
      print("Ignoring empty camera frame.")
      continue
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #coversion from BGR to RGB for pose detection
    results = pose.process(image) #putting frme into pose detection model
    
    #getting landmark attributes:
    #left elbow angle
    L_hip = (results.pose_landmarks.landmark[23].x, results.pose_landmarks.landmark[23].y, results.pose_landmarks.landmark[23].z)
    L_shoulder = (results.pose_landmarks.landmark[11].x, results.pose_landmarks.landmark[11].y, results.pose_landmarks.landmark[11].z)
    L_elbow = (results.pose_landmarks.landmark[13].x, results.pose_landmarks.landmark[13].y, results.pose_landmarks.landmark[13].z)
    L_wrist = (results.pose_landmarks.landmark[15].x, results.pose_landmarks.landmark[15].y, results.pose_landmarks.landmark[15].z)
    L_mouth = (results.pose_landmarks.landmark[9].x, results.pose_landmarks.landmark[9].y, results.pose_landmarks.landmark[9].z)
    L_elbowProjection = (results.pose_landmarks.landmark[13].x, results.pose_landmarks.landmark[13].y, results.pose_landmarks.landmark[11].z)

    R_hip = (results.pose_landmarks.landmark[24].x, results.pose_landmarks.landmark[24].y, results.pose_landmarks.landmark[24].z)
    R_shoulder = (results.pose_landmarks.landmark[12].x, results.pose_landmarks.landmark[12].y, results.pose_landmarks.landmark[12].z)
    R_elbow = (results.pose_landmarks.landmark[14].x, results.pose_landmarks.landmark[14].y, results.pose_landmarks.landmark[14].z)
    R_wrist = (results.pose_landmarks.landmark[16].x, results.pose_landmarks.landmark[16].y, results.pose_landmarks.landmark[16].z)
    R_mouth = (results.pose_landmarks.landmark[10].x, results.pose_landmarks.landmark[10].y, results.pose_landmarks.landmark[10].z)
    R_elbowProjection = (results.pose_landmarks.landmark[14].x, results.pose_landmarks.landmark[14].y, results.pose_landmarks.landmark[12].z)

    L_elbowAngle = getAngle(L_shoulder, L_elbow, L_wrist)
    L_armpitAngle = getAngle(L_hip, L_shoulder, L_elbow)
    L_bicepAngle = getAngle_YZ(L_elbow, L_shoulder, L_elbowProjection)

    R_elbowAngle = getAngle(R_shoulder, R_elbow, R_wrist)
    R_armpitAngle = getAngle(R_hip, R_shoulder, R_elbow)
    R_bicepAngle = getAngle_YZ(R_elbow, R_shoulder, R_elbowProjection)

    faceAngleYaw = getAngle_face_yaw(L_mouth, R_mouth, L_shoulder, R_shoulder)
    faceAngleRoll = getAngle_face_roll(L_mouth, R_mouth, L_shoulder, R_shoulder)
  
    print(f"left elbow angle: {L_elbowAngle} | right elbow angle: {R_elbowAngle}")
    print(f"left armpit angle: {L_armpitAngle} | right armpit angle: {R_armpitAngle}")
    print(f"left bicep angle: {L_bicepAngle} | right bicep angle: {R_bicepAngle}")
    print(f"Face angle yaw {faceAngleYaw}")
    print(f"Face angle roll {faceAngleRoll}")
    print(f"L_shoulder:{L_shoulder}\nL_wrist:{L_wrist}\nL_hip:{L_hip}\nL_elbowProjection:{L_elbowProjection}\nL_elbow:{L_elbow}")
    print(f"R_shoulder:{R_shoulder}\nR_wrist:{R_wrist}\nR_hip:{R_hip}\nR_elbowProjection:{R_elbowProjection}\nR_elbow:{R_elbow}")

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) #conversoin back to BGR
    mp_drawing.draw_landmarks(
        image, #frame
        results.pose_landmarks, #landmarks
        mp_pose.POSE_CONNECTIONS, #skeleton links
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()) #default landmark drawing
    cv2.imshow('MediaPipe Pose', cv2.flip(image, 1)) #frame flipped and displayed
    if cv2.waitKey(5) & 0xFF == 27: #terminate if "esc" pressed
      break
    print(deg2ics_face(faceAngleRoll))
    ser.write(bytes(f"{deg2ics_90(L_elbowAngle)},{deg2ics(L_armpitAngle)},{7500},{deg2ics_90(R_elbowAngle)},{deg2ics(R_armpitAngle)},{7500},{7500},{7500}\n", "utf-8"))
    time.sleep(0.8)
cap.release()
ser.close()