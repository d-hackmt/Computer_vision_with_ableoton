import cv2
import mediapipe as mp
import mido
import time

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

# Set up the virtual MIDI port (replace with the name of your virtual MIDI port)
midi_out = mido.open_output('abcdef 2')  # Use the name of your virtual MIDI port here

# Define MIDI control parameters for each hand
left_hand_control = 10  # MIDI CC number for left hand (e.g., filter knob)
right_hand_control = 74  # MIDI CC number for right hand (e.g., LFO knob)

def send_midi(control, value):
    """Send MIDI CC message directly to Ableton."""
    midi_msg = mido.Message('control_change', control=control, value=value)
    midi_out.send(midi_msg)
    print(f"Sent MIDI - Control: {control}, Value: {value}")  # Debugging output

def detect_pinch(hand_landmarks):
    """Detect pinch gesture by measuring distance between thumb and index finger tips."""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    return distance < 0.05  # Threshold for pinch gesture

# Open the camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Process image for hand landmarks
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Determine which hand (left or right) based on wrist position
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            hand_label = 'Left' if wrist.x < 0.5 else 'Right'

            # Check if the hand is pinching
            if detect_pinch(hand_landmarks):
                # Map hand Y position to MIDI value (0-127)
                midi_value = int((1 - wrist.y) * 127)

                if hand_label == 'Left':
                    send_midi(left_hand_control, midi_value)
                elif hand_label == 'Right':
                    send_midi(right_hand_control, midi_value)

    # Display the image with landmarks
    cv2.imshow("Hand Tracking", image)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
midi_out.close()
