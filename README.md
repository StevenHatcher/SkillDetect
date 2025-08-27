# SkillDetect
[Python](https://www.python.org/) [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) [ChromeDrive & Selenium](https://developer.chrome.com/docs/chromedriver) [Pyautogui](https://pyautogui.readthedocs.io/en/latest/) [Pandas](https://pandas.pydata.org/)
 
 This program operates behind the scenes while you play Fortnite and collects data about the opponents that eliminate you if their profile is public.

When the crosshair icon (indicating the player has been eliminated) is present on the screen, its size and location are used to calculate the dimensions and position
of the username of the player who brought you to your demise. The webpage for this player's statistics is opened through chromedriver, and the JSON data
is stored & used to pull their K/D ratio and playtime. These values are then stored in a .xlsx spreadsheet, and the average of the statistics is displayed at the 
top of the spreadsheet.



#### Automatically view and track the statistics of enemies that defeat you in Fortnite the moment you are eliminated.

This Python program combines OCR (Optical Character Recognition) and ChromeDriver functionalities to detect when an icon is present on the screen, then uses its position to calculate the size and location of the text that will be positioned relative to the icon. This text is read with an OCR, and used to open a temporary, locally-hosted, instance of a webpage, where JSON data is stored & used to pull data using a proprietary library I created. These values are then stored in a new row of a .xlsx spreadsheet and the average of each column is written to the top of its respective column. Then, the program will once again wait in the background until the player is eliminated again.  
  
The primary intention is to have this program running in the backround whenever you are playing, allowing the statistics to be collected over time and allowing you to see the enemy's stats briefly after being eliminated.

Functionality
-------------

### Image recognition

The screen is scanned every second for crosshair icon which indicates the player has been eliminated.

The program waits until this icon is detected to begin.

<img width="89" height="87" alt="caseSpecificCH" src="https://github.com/user-attachments/assets/45a337a3-3146-44af-a08d-e0b7717a3015" />


### Locating and processing username

### Locating

The sizing and position of the enemy's username are dynamic based on its length. However, the crosshair icon's position is absolute in relation to the username. Using this information and a sufficient sample size, I was able to calculate the linear regression model of the username's dimensions and position as a percentage of the screen width.

<img width="651" height="483" alt="Regression_mode" src="https://github.com/user-attachments/assets/43e4b183-a22f-4a08-a565-c8a34f2a529b" />

<img width="1748" height="243" alt="username_screen_cropped" src="https://github.com/user-attachments/assets/8445da4e-5334-4ea6-9f56-a3e29dd7f948" />




### Processing

For more consistent results when extracting text from the screen, the screenshot taken of the enemy's username is ran through two steps of preprocessing.

1\. Original image:

<img width="750" height="126" alt="unprocessed_username" src="https://github.com/user-attachments/assets/b420ff8d-2436-46e7-b268-39500cdce708" />


2\. Grayscale: Color is removed from the photo.


3\. Threshhold

<img width="750" height="126" alt="processed_username" src="https://github.com/user-attachments/assets/405b8b30-5fff-4c24-828f-611f0dbc470c" />


### Data extraction

### Statistics

When the enemy's username has been extracted successfully from the processed image, a webbrowser instance of their stats page is opened. The JSON data of their stats is then obtained using the proprietary open-source library I created to do so, and used to get their playtime and KD ratio.

<img width="884" height="498" alt="profile_page" src="https://github.com/user-attachments/assets/217b47b2-f99a-4b10-94bb-f5273d5adbea" />


When the player's statistics are retrieved succesfully, they are added to a spreadsheet in the program directory and the average of the collected stats is updated in the second row.


<img width="159" height="161" alt="spreadsheet_full" src="https://github.com/user-attachments/assets/397ca586-6954-40e3-91e2-6411ada5e034" />

Notable Information
-------------------

### Additional features

1\. Function parameters are provided for the user to control if the window of the enemy's statistic page autocloses or not, and if they chose for it to autoclose, how many seconds the page remains open for.  
  
2\. A second branch is provided on GitHub if the user strictly wants the webpage to open without logging any data to the spreadsheet.  
  

### OCR Training

While developing this software, I faced a couple of problems with extracting the username text from the screen using an OCR. The first problem was that the font used in Fortnite is rather stylized, making it difficult for the OCR to read. Attempting to train the model using .tif line images with their respective ground-truth texts in a Linux subsystem proved to be futile. Training models were seeing some success, but ultimately ended up skewed. There were a few specific character pairs that the OCR had trouble distinguishing (e.g. I and 1, G and 6), so I focused on training the model on the characters that it struggled with the most. However, this led to overfitting within the model, developing a tendency to read those characters (this effect was notable regardless of the number of training iterations (100, 1K, 10K)).  
  
I attempted to use Paddle OCR, however, it ended up being even less consistent. Processing the photo before passing it through Tesseract OCR (untrained) yielded surprisingly accurate and consistent results

<img width="1068" height="595" alt="ocr_training" src="https://github.com/user-attachments/assets/036bc289-d5c9-4b21-91b5-8ca974c208f5" />

### Limitations

1\. While I have set up the OCR in a way that makes it reliable, it is still possible for it to misread text. Moreover, the lower-bound threshold value is 230, so values between 231-255 could be included unintentionally. However, the threshold can be adjusted easily.  
  
2\. Usernames can include non-English characters, which aren't accounted for in the chosen OCR configuration. The fail-safe in place is that the website won't retrieve the JSON and will return nothing.  
  
3\. I haven't yet tested if the software works when playing Fortnite on a resolution that isn't the monitor's native resolution. This may cause issues when detected the crosshair icon asset.  
  



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
3. Clone FortniteStats into the project:
> git clone https://github.com/StevenHatcher/SkillDetect.git
4. Run SkillDetect.py


# Functions
## init_monitor()
Initializes the main_monitor with its position and dimensions
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
Takes a screenshot of the given region (the enemy player's username), processes it to be more readable for the OCR, and returns what the OCR reads.
**Returns:** Processed image of the enemy's username
**Parameters:**
- <ins>region</ins>: The region of the user's name 

## get_username_from_screen(crosshair_location)
Extracts the username of the player that brought you to your demise using pytesseract from your screen
**Returns:** Enemy's username
**Parameters:**
- <ins>crosshair_location</ins>: The region of the crosshair icon

## player_eliminated()
Main functionality. Runs other functions when the player is eliminated.
**Returns:** Enemy's username


## init_spreadsheet(filename="fortnite_stats")
Initializes the spreadsheet for the stats of the enemies that have eliminated you
**Returns:** None
**Parameters:**
- <ins>filename</ins>: The name of the spreadsheet file in your directory, excluding file extension
    - (If the file in your directory is spreadsheet.xlsx, use the value "spreadsheet" in your function call.)
    - NOTE: This will not create a new file. You should create a new file in your directory with the chosen name, then call this function once, then don't call it again.
## update_averages(filename="fortnite_stats")
Calculates and updates the averages of the playtimes and K/D ratios in the spreadsheet
**Returns:** EnemyNone
- <ins>filename</ins>: What you want to name the spreadsheet file

## write_to_spreadsheet(e_playtime, e_kd)
Writes the playtime and K/D of the enemy that killed you (given through parameters) into the spreadsheet
**Returns:** None
- <ins>e_playtime</ins>: the playtime to be added to the spreadsheet
- <ins>e_kd</ins>: the KD to be added to the spreadsheet
