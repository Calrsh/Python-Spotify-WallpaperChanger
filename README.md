![image](https://github.com/user-attachments/assets/90c907e2-12c6-4c75-b3bc-7a949edc0977)This is a personal project that I have been wanting to do - the objective was to make a wallpaper changer for windows.

This project uses CustomTkinter for its UI setup, as well as pystray for sending the application to the tray.

There are three options for generating a wallpaper, solid colour, shadow and a collage.
![image](https://github.com/user-attachments/assets/133b9570-50b2-490d-8f21-4037fb4547ed)
_Solid color_
![image](https://github.com/user-attachments/assets/8a9ea9d4-0f40-4c78-827e-53376fd09fb4)
_Shadowed Image_
![image](https://github.com/user-attachments/assets/6feb851f-7af4-4fdc-8a57-948cab666e81)
_Collage of top 50 artists_


This project is avaliable as its source code or as an exe.

The distribution file was made with: "pyinstaller --onefile --noconsole  --contents-directory "." --add-data "Images/*.png:Images/", Main.py"

This program requires windows and spotify.

To use:
1. Startup the program - it will ask for your client ID and client secret
2. Go to your spotify dashboard: https://developer.spotify.com/dashboard
3. Make a new app with any name, any description - IMPORTANT - redirect URL should be: "http://127.0.0.1:1234"
4. Select Webapi and webplaybacksdk as your api and save.
5. Navigate to your new app -> Settings -> Basic information
6. Copy your client ID and client secret into the application box.
7. You should now get a request from spotify asking to confirm usage - agree and use the app


 
