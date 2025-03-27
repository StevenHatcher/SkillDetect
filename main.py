import mss
import cv2
import numpy as np
import pytesseract
import sched, time # Import schedule and time to run every 30 seconds and check if text is on the screen
import webbrowser # Used to open the webrowser and see the information of the player that eliminated you
from screeninfo import get_monitors

# (Optional) Set the Tesseract path if it's not in the system PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# This function will return the values of the users monitors, including the resolution of main and other monitors **as well as which is the user's main monitor. 
## Use it to universally find a) where the main window is and b) where the text will be displayed within that window (probably use percentages) 
for m in get_monitors():
    print(str(m))


# Function to capture the screen 
def capture_screen(region):
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Get the main monitor
        # Adjust region coordinates relative to the main monitor
        adjusted_region = {
            "top": monitor["top"] + region["top"],
            "left": monitor["left"] + region["left"],
            "width": region["width"],
            "height": region["height"]
        }
        screenshot = sct.grab(adjusted_region)  # Capture only the specified region
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)  # Convert to grayscale for better OCR
        cv2.imwrite("captured_image.png", img)
        return img


# Function to extract username of the player that brought you to your demise
def extract_text_from_screen(region):
    img = capture_screen(region)
    text = pytesseract.image_to_string(img)  # Extract text
    return text.strip()

#left value is 1080 for first monitor plus 890 for region
# 892 for top?
region = {"top": 1200, "left": 880, "width": 645, "height": 122}
previous_text = ""

# Scheduler function that will run every 15 seconds to check if you've been eliminated
def do_something(scheduler): 
    # schedule the next call first
    scheduler.enter(15, 1, do_something, (scheduler,))

     
    detected_text: str = extract_text_from_screen(region)
    print("Detected Text:", detected_text)
    # Open a webpage if a username is detected in the chosen area 
    if detected_text != "" and detected_text != previous_text:
        webbrowser.open("https://fortnitetracker.com/profile/all/" + detected_text)
        #previous_text = detected_text
    

my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(15, 1, do_something, (my_scheduler,))
my_scheduler.run()





