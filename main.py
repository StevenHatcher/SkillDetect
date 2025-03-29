import mss
import cv2
import numpy as np
import pytesseract
import sched, time # Import schedule and time to run every 30 seconds and check if text is on the screen
import webbrowser # Used to open the webrowser and see the information of the player that eliminated you
import math #import math for floor() when calculating height of text based on percentage away from top of screen
# from screeninfo import get_monitors

# (Optional) Set the Tesseract path if it's not in the system PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# This function will return the values of the users monitors, including the resolution of main and other monitors **as well as which is the user's main monitor. 
## Use it to universally find a) where the main window is and b) where the text will be displayed within that window (probably use percentages) 

        


def get_region():
    with mss.mss() as sct:
        monitors = sct.monitors
        mainMonitor = monitors[1]  # Create a monitor object of the primary monitor
        relativeMonitor = monitors[0] # since the user might have more than one monitor, this relative monitor is the overarching dimensions of the all monitors
        
        text_height = int(mainMonitor["height"] * 0.085)
        text_width = int(mainMonitor["width"] * 0.26)

        # if len(m) > 1:
        if mainMonitor["left"] < relativeMonitor["left"]:
            left_of_monitor = relativeMonitor["left"] - mainMonitor["left"]
        else:
            left_of_monitor = 0
        if mainMonitor["top"] < relativeMonitor["top"]:
            top_of_monitor = relativeMonitor["top"] - mainMonitor["top"]
        else:
            top_of_monitor = 0

        left_of_text = left_of_monitor + ((0.47 * mainMonitor["width"]) - (0.5 * text_width))
        top_of_text = top_of_monitor + (0.8725 * mainMonitor["height"] - (0.5 * text_height))
        
        # Adjust region coordinates relative to the main monitor
        regionVar = {
            "top": int(top_of_text),
            "left": int(left_of_text),
            "width": int(text_width),
            "height": int(text_height)
        }
        print(f"Calculated Region: {regionVar}")
        return regionVar


# Function to capture the screen 
def capture_screen(regionPara):
    with mss.mss() as sct:
        screenshot = sct.grab(regionPara)  # Capture only the specified region
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)  # Convert to grayscale for better OCR
        cv2.imwrite("captured_image.png", img)
        return img

# Function to extract username of the player that brought you to your demise
def extract_text_from_screen(regionPara1):
    img = capture_screen(regionPara1)
    text = pytesseract.image_to_string(img)  # Extract text
    # print(f"Extracted Text: '{text}'")  # Debugging
    return text.strip()

region = get_region()


# Scheduler function that will run every 15 seconds to check if you've been eliminated
def do_something(scheduler): 
    global previous_text
    
    # schedule the next call first
    scheduler.enter(15, 1, do_something, (scheduler,))
     
    
    detected_text: str = extract_text_from_screen(region)
    print("Detected Text:", detected_text)
    # Open a webpage if a username is detected in the chosen area 
    # if detected_text != "" and detected_text != previous_text:
        # webbrowser.open("https://fortnitetracker.com/profile/all/" + detected_text)
        # previous_text = detected_text


# region = get_region()
# detected_text: str = extract_text_from_screen(region)
# print("Detected Text:", detected_text)
my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(15, 1, do_something, (my_scheduler,))
my_scheduler.run()





