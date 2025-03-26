import mss
import cv2
import numpy as np
import pytesseract
import sched, time # Import schedule and time to run every 30 seconds and check if text is on the screen
import webbrowser # Used to open the webrowser and see the information of the player that eliminated you

# (Optional) Set the Tesseract path if it's not in the system PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to capture the screen 
def capture_screen(region=None):
    with mss.mss() as sct:
        #screenshot = sct.grab(region or sct.monitors[1])  # Capture full screen or a specific region
        screenshot = sct.grab(sct.monitors[1])  # Capture full screen or a specific region
        img = np.array(screenshot)  # Convert to NumPy array
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)  # Convert to grayscale for better OCR accuracy
        return img

# Function to extract username of the player that brought you to your demise
def extract_text_from_screen(region=None):
    img = capture_screen(region)
    text = pytesseract.image_to_string(img)  # Extract text
    return text.strip()



# Scheduler function that will run every 15 seconds to check if you've been eliminated
def do_something(scheduler): 
    # schedule the next call first
    scheduler.enter(15, 1, do_something, (scheduler,))
    print("Doing stuff...")
    # then do your stuff
    # Example usage: Capture and read text in a specific area (x, y, width, height)
    region = {"top": 0, "left": 0, "width": 30, "height": 10}  
    detected_text: str = extract_text_from_screen(region)
    print("Detected Text:", detected_text)

    # Open a webpage if a certain word appears
    if detected_text != "" and detected_text != detected_text:
        webbrowser.open("https://fortnitetracker.com/profile/all/" + detected_text)
    

my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(60, 1, do_something, (my_scheduler,))
my_scheduler.run()





