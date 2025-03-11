import random
import tkinter
from ctypes.wintypes import RGB
from io import BytesIO
from pathlib import Path
import PIL
import customtkinter
import pystray
import requests
import screeninfo
import spotipy
from customtkinter import *
from pystray import MenuItem
from spotipy import SpotifyOAuth
from PIL import Image, ImageFilter, ImageGrab
import ctypes
from ctypes import byref, c_int
from colorthief import ColorThief
from CTkMessagebox import CTkMessagebox

"""
-----------------------------------------------------------System Tray -----------------------------------------------------------
"""


# Define a function for quit the window
def quit_window(icon):
    icon.stop()
    root.quit()




# Define a function to show the window again
def show_window(icon):
    icon.stop()
    root.after(0, root.deiconify)


# Hide the window and show on the system taskbar
def hide_window():
    root.withdraw()
    image = Image.open(app_data_path("Images/Image1.png"))
    menu = (MenuItem('Show', show_window), MenuItem('Quit', quit_window))
    icon = pystray.Icon("name", image, "My System Tray Icon", menu)
    icon.run_detached()



"""
-----------------------------------------------------------Where files are stored -----------------------------------------------------------
"""


# Files are stored in %User/AppData/Roaming/WallpaperApp
def app_data_path(filename):
    temp = Path(os.path.join(os.getenv('APPDATA'), 'WallpaperApp', filename))
    temp.touch(exist_ok=True)
    return temp


"""
-----------------------------------------------------------This is Spotify Interactions -----------------------------------------------------------
"""


def get_id_from_file():
    # Stop if file is not found or if file is empty
    try:
        try:
            with open(app_data_path("Settings\\store.txt"), "r") as f:
                client_id = f.readline().split("=", 1)[1].strip()
                client_secret = f.readline().split("=", 1)[1].strip()
            return client_id, client_secret
        except IndexError:
            setting_id_handler()
            return get_id_from_file()
    except FileNotFoundError:
        setting_id_handler()
        return get_id_from_file()


def setting_id_handler():
    # These are input dialog boxes - popups
    dialog = customtkinter.CTkInputDialog(text="Client ID: ", title="Enter Client ID")
    c_id_temp = dialog.get_input()
    # None equates to cancel - so quit
    if c_id_temp is None:
        quit()
    elif c_id_temp != "":
        dialog2 = customtkinter.CTkInputDialog(text="Client Secret: ", title="Enter Client Secret")
        c_sec_temp = dialog2.get_input()
        if c_sec_temp is None:
            quit()
        elif c_sec_temp != "":
            client_id = c_id_temp
            client_secret = c_sec_temp
            save_id(client_id, client_secret)
        else:
            setting_id_handler()
    else:
        setting_id_handler()


def save_id(client_id, client_secret):
    with open(app_data_path("Settings\\store.txt"), "w") as f:
        f.write("Client_ID=" + client_id + "\n")
        f.write("Client_Secret=" + client_secret)


def get_top_50_images():
    list_of_top_artists = []
    data = sp.current_user_top_artists(50)
    for i in range(0, 50):
        list_of_top_artists.append(data['items'][i]['images'][0]['url'])
    return list_of_top_artists


def current_playback():
    # This returns a URL to an image associated with what we need
    current_playing = sp.current_user_playing_track()
    if current_playing is not None:
        album_art = current_playing['item']['album']['images'][0]['url']
        return album_art
    return None


def current_playback_id():
    # This just returns the ID to compare by
    current_playing = sp.current_user_playing_track()
    if current_playing is not None:
        id_current = current_playing['item']['id']
        return id_current
    return None


"""
-----------------------------------------------------------This is now UI -----------------------------------------------------------
"""


def popup_window(text):
    CTkMessagebox(master=root, message=text, icon="cancel", option_1="Ok")


def get_image_from_url():
    # Try catch for when no track is playing
    try:
        return Image.open(requests.get(current_playback(), stream=True).raw)
    except:
        return Image.open(app_data_path("Images\\Image1.png"))


def get_dominant_color(path):
    color_thief = ColorThief(path)
    return color_thief.get_color(quality=1)


def combine_shadow_original():
    # Load the images
    img_for_centre = Image.open(app_data_path("Images\\Image1.png"))
    img_for_back = Image.open(app_data_path("Images\\Image2.png"))

    # Convert to RGBA (Files need to be PNG for this)
    img_for_centre = img_for_centre.convert("RGBA")
    img_for_back = img_for_back.convert("RGBA")

    bg_width, bg_height = img_for_back.size  # User screen resolution
    fg_width, fg_height = img_for_centre.size  # (640, 640)

    x_offset = (bg_width - fg_width) // 2
    y_offset = (bg_height - fg_height) // 2

    img_for_back.paste(img_for_centre, (x_offset, y_offset), img_for_centre)

    img_for_back.save(app_data_path("Images\\Image3.png"))


def generate_top_50():
    image_urls = get_top_50_images()
    screen = screeninfo.get_monitors()[0]  # Get primary monitor
    canvas_width, canvas_height = screen.width, screen.height

    # Create blank transparent canvas (RGBA mode)
    collage = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))

    # Number of images
    num_images = len(image_urls)

    # Define size range (largest to smallest)
    max_size = canvas_width // 6  # Reduce max size to decrease overlap
    min_size = canvas_width // 16  # Ensure smallest images are still visible

    # Generate decreasing sizes for images
    image_sizes = [max_size - (i * (max_size - min_size) // num_images) for i in range(num_images)]
    random.shuffle(image_sizes)  # Randomize order of sizes

    # Track placed positions to avoid overlap
    placed_positions = []

    # Function to check if a new image overlaps with existing ones
    def check_overlap(x, y, w, h):
        padding = 10  # Extra spacing to reduce clutter
        for px, py, pw, ph in placed_positions:
            if (x < px + pw + padding and x + w + padding > px and
                    y < py + ph + padding and y + h + padding > py):
                return True  # Overlapping
        return False  # No overlap

    # Load, resize, and place images with decreasing opacity
    for index, (url, size) in enumerate(zip(image_urls, image_sizes)):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")

            # Resize image while keeping aspect ratio
            img.thumbnail((size, size))

            # Randomly position the image, avoiding overlap
            attempts = 0
            x, y = 0, 0
            while attempts < 20:
                x = random.randint(0, canvas_width - size)
                y = random.randint(0, canvas_height - size)
                if not check_overlap(x, y, size, size):
                    placed_positions.append((x, y, size, size))
                    break
                size = max(size - 5, min_size)  # Reduce size slightly if no space
                attempts += 1
            collage.paste(img, (x, y), img)

        except Exception as e:
            print(f"Error processing image {index}: {e}")

    # Save final collage
    collage.save(app_data_path("Images\\Image4.png"), format="png")


def generate_back_shadow():
    img = get_image_from_url()
    img = img.filter(ImageFilter.BoxBlur(50))
    img = img.resize(ImageGrab.grab().size)
    img.save(app_data_path("Images\\Image2.png"))
    return None


def setting_wallpaper():
    img = get_image_from_url()
    img.save(app_data_path("Images\\Image1.png"))
    match radio_var.get():
        # Solid Color Option
        case 1:
            path = app_data_path("Images\\Image1.png")
            temp = get_dominant_color(path)
            color = RGB(temp[0], temp[1], temp[2])
            ctypes.windll.user32.SetSysColors(1, byref(c_int(1)), byref(c_int(color)))
            ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 1)

        # Shadowed Image
        case 2:
            generate_back_shadow()
            combine_shadow_original()
            path = app_data_path("Images\\Image3.png")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 1)
        case 3:
            generate_top_50()
            path = app_data_path("Images\\Image4.png")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 1)


def reenter_information():
    dialog = customtkinter.CTkInputDialog(text="Client ID: ", title="Enter Client ID")
    c_id_temp = dialog.get_input()
    if c_id_temp != "":
        dialog2 = customtkinter.CTkInputDialog(text="Client Secret: ", title="Enter Client Secret")
        c_sec_temp = dialog2.get_input()
        if c_sec_temp != "":
            client_id = c_id_temp
            client_secret = c_sec_temp
            save_id(client_id, client_secret)
        else:
            popup_window("No text was inputted")
    else:
        popup_window("No text was inputted")

def background_check():
    global image_id
    # Poll every second to run this function
    root.after(1500, background_check)
    # If new id
    if current_playback_id() != image_id:
        #Generate our new image for the application window
        my_image = customtkinter.CTkImage(light_image=get_image_from_url(),
                                          dark_image=get_image_from_url(),
                                          size=(330, 330))
        # Update image
        song_canvas.configure(image=my_image)
        root.update()
        #This is for active changing - change the background when we change
        if active_changing_tgl.get():
            setting_wallpaper()
            if radio_var.get() == 3:
                rd1_solid.select()
                active_changing_tgl.deselect()
        image_id=current_playback_id()


"""
-----------------------------------------------------------This is file handling-----------------------------------------------------------
"""


def export_settings():
    #Writing our data to the settings file
    with open(app_data_path("Settings\\settings.txt"), "w") as f:
        f.write(str(int(active_changing_tgl.get())) + "\n")
        f.write(str(radio_var.get()))


def import_settings():
    # Try read the file - select options that have been enabled
    try:
        with open(app_data_path("Settings\\settings.txt"), "r") as f:
            line = bool(int(f.readline()))
            if line:
                active_changing_tgl.select()
            else:
                active_changing_tgl.deselect()
            line = int(f.readline())
            match line:
                case 1:
                    rd1_solid.select()
                case 2:
                    rd2_shdw.select()
                case 3:
                    rd3_collage.select()
                    active_changing_tgl.deselect()

    except FileNotFoundError:
        return None
    except ValueError:
        return None


"""
-----------------------------------------------------------This is now startup behaviour -----------------------------------------------------------
"""
# Ensure the file is present - if not generate a white image
try:
    first_image = Image.open(app_data_path("Images\\Image1.png"))
except PIL.UnidentifiedImageError:
    image = Image.new('RGB', (200, 200))
    image.save(app_data_path("Images\\Image1.png"))
    first_image = Image.open(app_data_path("Images\\Image1.png"))
image_id = 'N/A'

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.iconbitmap()
root.title("My Wallpaper App")
root.geometry("600x500")
root.resizable(width=False, height=False)

#######################################################################################################################
# All UI elements
my_image = customtkinter.CTkImage(light_image=first_image,
                                  dark_image=first_image,
                                  size=(330, 330))

song_canvas = customtkinter.CTkLabel(master=root, text="", image=my_image)
song_canvas.pack(pady=10)

# Frame for buttons
button_frame = customtkinter.CTkFrame(master=root, width=100, height=100, fg_color="grey")
button_frame.pack(expand=False, fill=BOTH)

set_wallpaper_btn = customtkinter.CTkButton(master=button_frame, text="Set as wallpaper", command=setting_wallpaper)
set_wallpaper_btn.pack(padx=10, pady=10, side="left")

input_id_btn = customtkinter.CTkButton(master=button_frame, text="Input IDs", command=reenter_information)
input_id_btn.pack(padx=10, pady=10, side="right")

minimise_btn = customtkinter.CTkButton(master=button_frame, text="Quit", command=root.destroy)
minimise_btn.pack(padx=10, pady=10, side="top")

check_var = customtkinter.BooleanVar()

radio_frame = customtkinter.CTkFrame(master=root, width=100, height=100, fg_color="grey")
radio_frame.pack(expand=False, fill=BOTH)

active_changing_tgl = customtkinter.CTkCheckBox(master=radio_frame, text="Active Changing", variable=check_var,
                                                onvalue=True,
                                                offvalue=False)
active_changing_tgl.pack(padx=10, pady=10, side="right")

radio_var = tkinter.IntVar(value=0)
rd1_solid = customtkinter.CTkRadioButton(master=radio_frame, text="Solid Color", variable=radio_var, value=1)
rd2_shdw = customtkinter.CTkRadioButton(master=radio_frame, text="Shadow Image", variable=radio_var, value=2)
rd3_collage = customtkinter.CTkRadioButton(master=radio_frame, text="Top 50 Collage",
                                           command=active_changing_tgl.deselect,
                                           variable=radio_var, value=3)
rd1_solid.select()
radio_text = customtkinter.CTkLabel(master=radio_frame, text="Image options")
radio_text.pack(padx=10, pady=10, side="top")
rd1_solid.pack(pady=10, padx=10, side="left")
rd2_shdw.pack(pady=10, padx=10, side="left")
rd3_collage.pack(pady=10, padx=10, side="left")

root.protocol('WM_DELETE_WINDOW', hide_window)
# Import the settings - for example if the user had previously selected to keep active changing on then it will start as such
import_settings()

# Make sure keys are present, will continue until app is quit or keys inputted
error = True
while error:
    id_pair = get_id_from_file()
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=id_pair[0],
                                                       client_secret=id_pair[1],
                                                       redirect_uri="http://127.0.0.1:1234",
                                                       scope="user-read-currently-playing user-top-read"))
        error = False
    except spotipy.exceptions.SpotifyOauthError as e:

        setting_id_handler()

background_check()
root.mainloop()
# Export current settings so that they can be reloaded in
export_settings()
