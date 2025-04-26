import mss # import mss for monitor data
import cv2
import numpy as np
import pytesseract # Import pytesseract to use the OCR for scanning the screencapped region for text and saving results in a variable
import pyautogui
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

#create a variable to store the crosshair image
crosshair_image = 'imgs/caseSpecificCH.png'
crosshair_location = None



# This function will return the values of the users monitors, including the resolution of main and other monitors **as well as which is the user's main monitor. 
## Use it to universally find a) where the main window is and b) where the text will be displayed within that window (using percentages)         
def get_region():
    with mss.mss() as sct:
        monitors = sct.monitors
        mainMonitor = monitors[1]  # Create a monitor object of the primary monitor
        relativeMonitor = monitors[0] # since the user might have more than one monitor, this relative monitor is the overarching dimensions of the all monitors
    
        # The text height is ~8.75% of the height of the screen (Consider giving extra .5% tolerance)
        text_height = int(mainMonitor["height"] * 0.088)
        

        # if len(m) > 1:
        if mainMonitor["left"] < relativeMonitor["left"]:
            left_of_monitor = relativeMonitor["left"] - mainMonitor["left"]
        else:
            left_of_monitor = 0
        if mainMonitor["top"] < relativeMonitor["top"]:
            top_of_monitor = relativeMonitor["top"] - mainMonitor["top"]
        else:
            top_of_monitor = 0

        try:
            if pyautogui.locateOnScreen(crosshair_image, region=(left_of_monitor, top_of_monitor, mainMonitor["width"], mainMonitor["height"]) , confidence=0.50) is not None:
                crosshair_location = pyautogui.locateOnScreen(crosshair_image, region=(left_of_monitor, top_of_monitor, mainMonitor["width"], mainMonitor["height"]) , confidence=0.50)

                # print(f"Image found at: {crosshair_location}")

                # The distance that the crosshair is from the right side of the main monitor will tell us the size of text
                crosshair_percentage_from_right = 100 - ((crosshair_location[0] / mainMonitor["width"]) * 100)
                # print(f"crosshair_percentage_from_right: {crosshair_percentage_from_right}")
                # im = pyautogui.screenshot('my_screenshot.png', region=(left_of_monitor, top_of_monitor, mainMonitor["width"], mainMonitor["height"]))
                
                text_width = (-1.89957 * crosshair_percentage_from_right) + 97.61061
            
                # print(f"Text width percentage: {text_width}")
            
                text_width = (text_width / 100) * mainMonitor["width"] + (0.03 * mainMonitor["width"])
                
                # This one is a doozy but makes sense. This is the horizontal position of the left side of the username text of the player that elimnated you.
                left_of_text = mainMonitor["width"] - text_width - ((crosshair_percentage_from_right / 100) * mainMonitor["width"]) - (0.006 * mainMonitor["width"]) 
                
                # print(f"Text width pixels: {text_width}")
                
                # The top of the enemy username text is about 87.25% down from the top of the monitor. Give 0.5% as tolerance.
                top_of_text = top_of_monitor + (0.874 * mainMonitor["height"] - (0.5 * text_height))
                
                # im2 = pyautogui.screenshot('my_screenshot_symbol.png', region=(1598, 1222, 89, 87))
                
                # Adjust region coordinates relative to the main monitor
                regionVar = {
                    "top": int(top_of_text),
                    "left": int(left_of_text),
                    "width": int(text_width),
                    "height": int(text_height)
                }
                print(f"Calculated Region: {regionVar}")
                return regionVar
        # Use pyautogui to get the position of the crosshair on the screen. The left edge of the crosshair is ALWAYS 46px the right of the right edge of the username text
        
        except pyautogui.ImageNotFoundException:
            return


# Function to capture the screen 
def capture_screen(regionPara):
    with mss.mss() as sct:
        screenshot = sct.grab(regionPara)  # Capture only the specified region
        img = np.array(screenshot)
        # img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)  # Convert to grayscale for better OCR
        # cv2.imwrite("captured_image.png", img)
        
        # Convert to grayscale (OCR likes grayscale better)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)  # 4x upscale
        # Apply threshold to make black and white
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Save for debugging if needed
        cv2.imwrite("preprocessed_image.png", thresh)
        
        return thresh

# Function to extract username of the player that brought you to your demise
def extract_text_from_screen(regionPara1):
    img = capture_screen(regionPara1)
    text = pytesseract.image_to_string(img, config='--oem 3 --psm 7')  # Extract text
    
    # Clean unwanted characters
    cleaned_text = text.strip()
    cleaned_text = cleaned_text.replace(' ', '').replace('~', '')

    return cleaned_text
    

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
while True:
        # if crosshair_position:
            region = get_region()
            if region is not None:
                detected_text: str = extract_text_from_screen(region)
                print("Detected Text:", detected_text)
                # Open a webpage if a username is detected in the chosen area 
                if detected_text != "" and detected_text != previous_text:
                    # webbrowser.open("https://fortnitetracker.com/profile/all/" + detected_text)
                    
                    # enemy_playtime, enemy_kd = 0, 0
                    # enemy_playtime, enemy_kd = get_player_data(detected_text)
                    enemy_stats = get_player_data(detected_text)
                    
                    # player_playtime, player_kd = 0, 0
                    # player_playtime, player_kd = get_player_data("StillSheisty")
                    player_stats = get_player_data("StillSheisty")
                    
                    if enemy_stats[0] != 0 and enemy_stats[1] != 0 and player_stats[0] != 0 and player_stats[1] != 0:
                        write_to_spreadsheet(enemy_stats[0], enemy_stats[1], player_stats[0], player_stats[1])
                    previous_text = detected_text
            else:
                time.sleep(1)





