import mss # import mss for monitor data
import cv2
import numpy as np
import pytesseract # Import pytesseract to use the OCR for scanning the screencapped region for text and saving results in a variable
import pyautogui #Used to find the crosshair icon on the screen.
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd # Import pandas to store the data from the website into a spreadsheet
import  time # Import schedule and time to run every 30 seconds and check if text is on the screen
from FortniteStats.FortniteStats import * # Import all of the functions from the FortniteStats repo
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # (Optional) Set the Tesseract path if it's not in the system PATH

crosshair_image = 'imgs/crosshair_icon.png' # Store the crosshair image to determine when the player dies
main_monitor = None
left_of_monitor = 0
top_of_monitor = 0

# Function to initialize the monitors. We use the main_monitor variable for the screen region info.
def init_monitor():
    with mss.mss() as sct:
            monitors = sct.monitors
            global main_monitor 
            main_monitor = monitors[1]  # Create a monitor object of the primary monitor (monitors[1] is the the primary monitor)


# This function checks to see if the crosshair image is present on the screen. If it is, then calculate where the player's username will display.
def check_if_eliminated():
    try:    # Use pyautogui to get the position of the crosshair on the screen. The left edge of the crosshair is ALWAYS the same distance to the right of the right edge of the username text
        if pyautogui.locateOnScreen(crosshair_image, region=(left_of_monitor, top_of_monitor, main_monitor["width"], main_monitor["height"]) , confidence=0.75) is not None:
            return True
        else:
            return False
    except pyautogui.ImageNotFoundException: # if the crosshair image isn't found, return without doing anything.
        return False


# This function will calculate where the enemy's username will display on the screen based on where the crosshair is present on the screen  
def calculate_username_region(crosshair_location):

    crosshair_percentage_from_right = 100 - ((crosshair_location[0] / main_monitor["width"]) * 100) # The distance that the crosshair is from the right side of the main monitor will tell us the size of text
    
    text_height = int(main_monitor["height"] * 0.088) # The text height is ~8.75% of the height of the screen (Consider giving extra .5% tolerance)
    text_width = (-1.89957 * crosshair_percentage_from_right) + 97.61061 # Calculate the text width as a PERCENTAGE based on the crosshair's position
    text_width = (text_width / 100) * main_monitor["width"] + (0.03 * main_monitor["width"]) # Calculate the text width in PIXELS based on the crosshair's position (with tolerance)
    
    # This one is a doozy but makes sense. This is the horizontal position of the left side of the username text of the player that elimnated you.
    left_of_text = main_monitor["width"] - text_width - ((crosshair_percentage_from_right / 100) * main_monitor["width"]) - (0.006 * main_monitor["width"]) 
    
    top_of_text = top_of_monitor + (0.874 * main_monitor["height"] - (0.5 * text_height)) # The top of the enemy username text is about 87.25% down from the top of the monitor. Give 0.5% as tolerance.
    
    # Adjust region coordinates relative to the main monitor
    regionVar = {
        "top": int(top_of_text),
        "left": int(left_of_text),
        "width": int(text_width),
        "height": int(text_height)
    }
    
    if all(value > 0 for value in regionVar.values()): return regionVar # Had some issues when resizing a window, so we ensure region values are positive before returning the region
    else: return None

# Function to capture the screen. This function takes a screenshot of the given region (the enemy playert's username), processes it to be more readable for the OCR, then returns it
def screenshot_playername(region):
    with mss.mss() as sct:
        screenshot = sct.grab(region)  # Capture only the specified region
        img = np.array(screenshot)
        
        # UNCOMMENT IF YOU NEED TO SEE THE UNPROCESSED USERNAME SCREENSHOT
        # cv2.imwrite("generated/unpocessed_username.png", img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Convert the image to grayscale 
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)  # 4x upscale
        _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY) # Apply threshold to make black and white ADJUST MIN FROM 230 IF NEEDED
        # cv2.imwrite("generated/processed_username.png", thresh) # Save the processed image of the username screenshot for debugging purposes
        
        return thresh

# Function to extract username of the player that brought you to your demise using pytesseract
def get_username_from_screen(crosshair_location):
    username_region = calculate_username_region(crosshair_location)
    img = screenshot_playername(username_region) # Get processed image of the enemy player's username
    text = pytesseract.image_to_string(img, config='--oem 3 --psm 7')  # extract the text from the image using pytesseract OCR
    
    cleaned_text = text.strip()     # Clean unwanted characters - This might need some finetuning, 
    cleaned_text = cleaned_text.replace('', '').replace('~', '') # but I found spaces and ~ to improperly be read the most often

    return cleaned_text
  
# Function for when the player is eliminated. Returns the username of the enemy
def player_eliminated(): 
    try:    # Use pyautogui to get the position of the crosshair on the screen. The left edge of the crosshair is ALWAYS the same distance to the right of the right edge of the username text
        if pyautogui.locateOnScreen(crosshair_image, region=(left_of_monitor, top_of_monitor, main_monitor["width"], main_monitor["height"]) , confidence=0.75) is not None:
            crosshair_location = pyautogui.locateOnScreen(crosshair_image, region=(left_of_monitor, top_of_monitor, main_monitor["width"], main_monitor["height"]) , confidence=0.75)
            username_text = get_username_from_screen(crosshair_location)
            return username_text
        else:
            return None
    except pyautogui.ImageNotFoundException: # if the crosshair image isn't found, return without doing anything.
        return
    
#--------------------------------- SPREADSHEET FUNCTIONS ---------------------------------#

#function to initialize the spreadsheet if you don't have a blank one. This expects there to be a clean fortnite_stats.xlsx in generated to work.
def init_spreadsheet(filename="fortnite_stats"):
      # Create a new DataFrame with headers and a reserved row for averages
            df = pd.DataFrame(columns=["K/D", "Playtime"])
            df.loc[0] = [None, None]  # Row 0 for averages
            df.to_excel(f"generated/{filename}.xlsx", index=False)

# function to update the average of the stats of players that have eliminated in the spreadsheet
def update_averages(filename="fortnite_stats"):
    df = pd.read_excel(f"generated/{filename}.xlsx") # Load the spreadsheet

    if len(df) <= 2: # If there arent two or more values in the spreadsheet, you cant really take an average lol
        print("Not enough data to calculate averages yet.")
        return

    # Calculate averages only from data rows AFTER the reserved average row (starting from index 2)
    data_rows = df.iloc[2:]
    avg_kd = data_rows["K/D"].mean()
    avg_playtime = data_rows["Playtime"].mean()
    avg_playtime =  round(avg_playtime, 2)
    avg_kd = round(avg_kd, 2)
    # Update the reserved second row (index 0 when we don't consider the title as an indexed row) 
    df.loc[0, "K/D"] = avg_kd
    df.loc[0, "Playtime"] = avg_playtime

    # Save back to Excel
    df.to_excel(f"generated/{filename}.xlsx", index=False)

# Write the enemy's kd and playtime to the spreadsheet.
def write_to_spreadsheet(e_playtime, e_kd):#, p_playtime, p_kd):
    if enemy_hours == 0 and enemy_kd == 0: return
    # Load the existing spreadsheet
    df = pd.read_excel("generated/fortnite_stats.xlsx")

    # Append the new stats
    new_row = {"K/D": e_kd, "Playtime": e_playtime}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save back to Excel
    df.to_excel("generated/fortnite_stats.xlsx", index=False)
    print(f"Added: K/D = {e_kd}, Playtime = {e_playtime} hours")
    update_averages() # Update the average K/D and Playtime of enemies in the first row.


# main_screen, left_of_monitor, top_of_monitor = calculate_screen_region() # Get the region of the user's main screen
previous_text = "" # This variable will hold the name of the player that eliminated you previously.
init_monitor()
# Loop indefinitely and check if the crosshair icon is on the screen - if it is, then you've been eliminated and we need to do the rest of the stuff that I wrote this program for
while True:
        is_player_eliminated = check_if_eliminated() # Check if the player has been eliminated (if the crosshair icon is present).
        if is_player_eliminated:        
            enemy_name: str = player_eliminated() # Get the username of the enemy that eliminated you
            # I understand that this can create a problem if the same player eliminates you twice in a row... If that happens, I'll just uninstall the game and not worry about stats anymore lol.
            if enemy_name != "" and enemy_name != previous_text:
                enemy_data = get_player_data(username=enemy_name, maximize=True, auto_close=True) # Get JSON of the enemy player's stats
                if enemy_data: # If enemy data was successfully acquired, calculate their kd and playtime then write them to the spreadhseet
                    enemy_kd = get_player_stats(enemy_data, gamemode="all", data="KD", option="value") 
                    enemy_hours = round(get_player_stats(enemy_data, gamemode="all", data="MinutesPlayed", option="value") / 60, 2) # Get the player's playtime and convert it to hours

                    write_to_spreadsheet(enemy_hours, enemy_kd) # Write the data to the spreadsheet, this will update the average at the top of the sheet as a side effect
                
                previous_text = enemy_name
                update_averages() # Update the average K/D and Playtime of enemies in the first row.
            is_player_eliminated = False
            time.sleep(120) # Sleep for 2 minutes after getting killed and running program. Feel free to adjust this.
        else:
            time.sleep(1)
