import mss # import mss for monitor data
import cv2
import numpy as np
import pytesseract # Import pytesseract to use the OCR for scanning the screencapped region for text and saving results in a variable
import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import json
from bs4 import BeautifulSoup
import re

import pandas as pd # Import pandas to store the data from the website into a spreadsheet

import sched, time # Import schedule and time to run every 30 seconds and check if text is on the screen
import webbrowser # Used to open the webrowser and see the information of the player that eliminated you
# import requests




# (Optional) Set the Tesseract path if it's not in the system PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# This function will return the values of the users monitors, including the resolution of main and other monitors **as well as which is the user's main monitor. 
## Use it to universally find a) where the main window is and b) where the text will be displayed within that window (probably use percentages) 

#create a variable to store the crosshair image
crosshair_image = 'imgs/caseSpecificCH.png'
crosshair_location = None
players_username = "StillSheisty"


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
        
        # UNCOMMENT IF YOU NEED TO SEE THE UNPROCESSED USERNAME SCREENSHOT
        # img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)  # Convert to grayscale for better OCR
        # cv2.imwrite("captured/captured_image.png", img)
        
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Convert to grayscale (OCR likes grayscale better)
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)  # 4x upscale
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY) # Apply threshold to make black and white

        
        cv2.imwrite("generated/processed_username.png", thresh) # Save the processed image of the username screenshot
        
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
    url = f"https://fortnitetracker.com/profile/all/{username}"

    chrome_options = Options()
    chrome_options.add_argument("--start-minimized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # less detection
    
    

    driver = webdriver.Chrome(options=chrome_options) # Chrome isntance to scrape the data (Can't just use requests - Get status code 403 even with headers)
    driver.minimize_window() # Can't scrape it in headerless, so just minimize the window when it opens lol

    try:
        driver.get(url)

        # Wait for an element we know is needed (play time area)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "trn-card__annotation"))
        )

        time.sleep(2)  # optional: extra wait for full JavaScript rendering

        # Once fully loaded, get page source
        html = driver.page_source
       
        # Search for the JSON block that contains the player's stats
        profile_json_text = re.search(r'const profile = ({.*?});', html, re.DOTALL)

        if not profile_json_text:
            print("Could not find profile JSON in page.")
            return 0, 0

        profile_raw = profile_json_text.group(1)
        profile_raw = profile_raw.replace("undefined", "null")  # Fix invalid JS if necessary
        profile_data = json.loads(profile_raw)

        # Now navigate through the JSON to the "all" section
        kd_ratio = 0
        kd_ratio = profile_data["stats"][0]["stats"]["all"][2]["value"]

        total_hours = 0
        total_minutes = profile_data["stats"][0]["stats"]["all"][6]["value"]
        total_hours = round(total_minutes / 60, 2)

        
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

    finally:
        driver.quit()

    print(f"Total Play Time: {total_hours:.2f} hours")
    print(f"K/D Ratio: {kd_ratio:.2f}")

    return total_hours, kd_ratio

def init_spreadsheet():
        # Check if the file exists
        # if not os.path.exists(generated/fortnite_stats.xlsx): # Import OS if you want to use this
        # Create a new DataFrame with headers and a reserved row for averages
            df = pd.DataFrame(columns=["K/D", "Playtime"])
            df.loc[0] = [None, None]  # Row 0 for averages
            df.to_excel("generated/fortnite_stats.xlsx", index=False)

# Save to Excel
def write_to_spreadsheet(e_playtime, e_kd):#, p_playtime, p_kd):
    # Load the existing spreadsheet
    df = pd.read_excel("generated/fortnite_stats.xlsx")

    # Append the new stats
    new_row = {"K/D": e_kd, "Playtime": e_playtime}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save back to Excel
    df.to_excel("generated/fortnite_stats.xlsx", index=False)
    print(f"Added: K/D = {e_kd}, Playtime = {e_playtime} hours")


def update_averages():
    
    
    # if not os.path.exists(filename):
    #     print("The spreadsheet does not exist yet.")
    #     return

    # Load spreadsheet
    df = pd.read_excel("fortnite_stats.xlsx")

    if len(df) <= 2:
        print("Not enough data to calculate averages yet.")
        return

    # Calculate averages only from data rows AFTER the reserved average row (starting from index 2)
    data_rows = df.iloc[2:]
    
    avg_kd = data_rows["K/D"].mean()
    avg_playtime = data_rows["Playtime"].mean()

    # Update the reserved second row (index 1)
    df.loc[1, "K/D"] = avg_kd
    df.loc[1, "Playtime"] = avg_playtime

    # Save back to Excel
    df.to_excel("fortnite_stats.xlsx", index=False)

    print(f"Updated Averages: Avg K/D = {avg_kd:.2f}, Avg Playtime = {avg_playtime:.2f} hours")


previous_text = ""
# Loop indefinitely and check if the crosshair icon is on the screen - if it is, then you've been eliminated and we need to do the rest of the stuff that I wrote this program for
while True:
        region = get_region()
        if region is not None:
            detected_text: str = extract_text_from_screen(region)
            print("Detected Text:", detected_text)
            # Open a webpage if a username is detected in the chosen area and the username is a new name
            # I understand that this can create a problem if the same player eliminates you twice in a row... If that happens, I'll just uninstall the game and not worry about stats anymore.
            if detected_text != "" and detected_text != previous_text:
                # webbrowser.open("https://fortnitetracker.com/profile/all/" + detected_text)
                
                enemy_hours, enemy_kd = get_player_data(detected_text) # Get the enemy player's stats
                # player_hours, player_kd = get_player_data(players_username) # Get your stats (Optional)
                
                if enemy_hours != 0 and enemy_kd != 0: #and player_hours != 0 and player_kd != 0:
                    write_to_spreadsheet(enemy_hours, enemy_kd)#, player_hours, player_kd)
                    update_averages() # Update the average K/D and Playtime of enemies in the first row.
                previous_text = detected_text
        else:
            time.sleep(1)





