# SkillDetect
 This program runs in the background while you play Fortnite and collects data about the opponents that eliminate you if their profile is public.

This program detects when the crosshair icon (indicating the player has been eliminated) is present on the screen, then calculates the size and location
of the username of the player that brought you to your demise. The webpage for this player's statistics is opened through chromedriver and the json data
is stored & used to pull their K/D ratio and playtime. These values are then stored in a .xlsx spreadsheet and the average of the statistics is displayed at the 
top of the spreadsheet.


# Installation
## Preliminaries
1. Get the latest version of Tesseract OCR
> https://tesseract-ocr.github.io/tessdoc/
2. Install the latest version of ChromeDriver
> https://developer.chrome.com/docs/chromedriver/downloads

## Setup
1. Clone the repository:
> git clone https://github.com/StevenHatcher/SkillDetect.git
2. Install required dependencies
> pip install -r requirements.txt
3. Clone FortniteStats into project:
> git clone https://github.com/StevenHatcher/FortniteStats.git
4. Run SkillDetect.py


# Functions
## init_monitor()
Initializes the main_monitor with it's position and dimensions
**Returns:** None

## check_if_eliminated()
Checks the screen for the crosshair icon to determine if the player has been eliminated
**Returns:** True or False


## calculate_username_region(crosshair_location)
Calculates where the enemy's username will display on the screen based on where the crosshair is present on the screen 
**Returns:** the region of the screen or None
**Parameters:**
- <ins>crosshair_location</ins>: The region of the crosshair icon

## screenshot_playername(region)
Takes a screenshot of the given region (the enemy playert's username), processes it to be more readable for the OCR, returns what the OCR reads.
**Returns:** Processed image of the enemy's username
**Parameters:**
- <ins>region</ins>: The region of the user's name 

## get_username_from_screen(crosshair_location)
Extracts the username of the player that brought you to your demise using pytesseract from your screen
**Returns:** Enemy's username
**Parameters:**
- <ins>crosshair_location</ins>: The region of the crosshair icon

## player_eliminated()
Main functionality. Runs other functions when player is eliminated.
**Returns:** Enemy's username


## init_spreadsheet(filename="fortnite_stats")
Initializes the spreadsheet for the stats of the enemies that have eliminated you
**Returns:** None
**Parameters:**
- <ins>filename</ins>: The name of the spreadsheet file in your directory excluding file extension
    - (If the file in your directory is spreadsheet.xlsx, use the value "spreadsheet" in your function call.)
    - NOTE: This will not create a new file. You should create a new file in your directory with the chosen name, then call this function once, then don't call it again.
## update_averages(filename="fortnite_stats")
Calculates and updates the averages off the playtimes and K/D ratios in the spreadhseet
**Returns:** EnemyNone
- <ins>filename</ins>: What you want to name the spreadsheet file

## write_to_spreadsheet(e_playtime, e_kd)
Writes the playtime and K/D of the enemy that killed you (given through parameters) into the spreadsheet
**Returns:** None
- <ins>e_playtime</ins>: the playtime to be added to the spreadsheet
- <ins>e_kd</ins>: the KD to be added to the spreadsheet