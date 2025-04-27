# SweatDetect
 Run this program in the background while you play Fortnite to collect data about your opponents if their profile is public.
 After a recent update, I found myself struggling every match. I began looking up the profiles of the players that would
 eliminate me and I found that their playtime was often 3000+ hours... wow.

This program detects when the crosshair icon (indicating the player has been eliminated) is present on the screen, then calculates the size and location
of the username of the player that brought you to your demise. The webpage for this player's statistics is opened through chromedriver and the json data
is used to pull their K/D ratio and playtime. These values are then stored in a .xlsx spreadsheet and the average of the statistics is displayed at the 
top of the spreadsheet.
