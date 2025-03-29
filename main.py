import mss # import mss for monitor data
import cv2
import numpy as np
import pytesseract # Import pytesseract to use the OCR for scanning the screencapped region for text and saving results in a variable
import sched, time # Import schedule and time to run every 30 seconds and check if text is on the screen
import webbrowser # Used to open the webrowser and see the information of the player that eliminated you
import requests
import re # Import re to help with extracting our K/D from the website
from bs4 import BeautifulSoup
import pandas as pd # Import pandas to store the data from the website into a spreadsheet

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
    return text.strip()

region = get_region()


def get_player_data(username):
    url = "https://fortnitetracker.com/profile/all/" + username # Get the link for the page
    headers = {"User-Agent": "Mozilla/5.0"} # Get the content from the page
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract Play Time (e.g., "225h 57m Play Time")
        play_time_element = soup.find("div", class_="trn-card__annotation")
        if play_time_element:
            play_time_text = play_time_element.text.strip()
            time_match = re.search(r"(\d+)h\s+(\d+)m", play_time_text)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                total_hours = hours + (minutes / 60)
            else:
                return
        else:
            return

        # Extract K/D Ratio 
        kd_element = soup.find(string=re.compile("K/D"))
        if kd_element:
            kd_match = re.search(r"(\d+\.\d+)", kd_element)
            kd_ratio = float(kd_match.group(1)) if kd_match else None
        else:
            kd_ratio = None

        # Print results
        print(f"Total Play Time: {total_hours} hours")
        print(f"K/D Ratio: {kd_ratio}")

        return total_hours, kd_ratio
        
        
# Save to Excel
def write_to_spreadsheet(e_playtime, e_kd, p_playtime, p_kd):
    # Initialize DataFrame with column titles
    columns = ['Player', 'Playtime', 'KD', 'Average playtime of players that eliminate you', 'Average KD of players that eliminate you']
    df = pd.DataFrame(columns=columns)
    df.loc[0] = {p_playtime, p_kd, None, None}
    enemy_row = {e_playtime,e_kd, None, None}
    new_row = pd.Series(enemy_row, index=df.columns)
    df = df.append(new_row, ignore_index=True)
    
    df.to_excel("fortnite_stats.xlsx", index=False)


previous_text = ""
# Scheduler function that will run every 15 seconds to check if you've been eliminated
def do_something(scheduler): 
    global previous_text
    
    # schedule the next call first
    scheduler.enter(15, 1, do_something, (scheduler,))
     
    
    detected_text: str = extract_text_from_screen(region)
    print("Detected Text:", detected_text)
    # Open a webpage if a username is detected in the chosen area 
    if detected_text != "" and detected_text != previous_text:
        webbrowser.open("https://fortnitetracker.com/profile/all/" + detected_text)
        enemy_playtime, enemy_kd = get_player_data(detected_text)
        player_playtime, player_kd = get_player_data("StillSheisty")
        if enemy_playtime != None and enemy_kd != None and player_playtime != None and player_kd != None:
            write_to_spreadsheet(enemy_playtime, enemy_kd, player_playtime, player_kd)
        previous_text = detected_text




# region = get_region()
# detected_text: str = extract_text_from_screen(region)
# print("Detected Text:", detected_text)
my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(15, 1, do_something, (my_scheduler,))
my_scheduler.run()





