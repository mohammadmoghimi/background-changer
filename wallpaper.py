import ctypes
import os
import keyboard
import itertools
from PIL import Image
from io import BytesIO
import threading
import time

def change_wallpaper(image_path):
    # Convert the image path to a byte string
    image_path = os.path.abspath(image_path).encode('utf-16le')
    # Call the SystemParametersInfo function to change the wallpaper
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

def set_wallpaper_from_image(image):
    # Save the image to a temporary in-memory file
    with BytesIO() as img_buffer:
        image.save(img_buffer, format='BMP')
        img_buffer.seek(0)
        image_path = os.path.abspath('current_wallpaper.bmp')
        with open(image_path, 'wb') as f:
            f.write(img_buffer.read())
    # Set the wallpaper using the temporary file
    change_wallpaper(image_path)
    os.remove(image_path)

def get_images_from_folder(folder_path):
    # Get list of image files in the folder
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(image_extensions)]

def rotate_image(image_path):
    # Rotate the image 180 degrees on the y-axis (flip horizontally)
    with Image.open(image_path) as img:
        rotated_img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return rotated_img

def change_wallpaper_periodically(image_iterator, interval):
    while True:
        current_image = next(image_iterator)
        change_wallpaper(current_image)
        print("Wallpaper automatically changed to", current_image)
        time.sleep(interval)

def main():
    # Set the folder path containing the images
    folder_path = ""  # Change this to the path of your images folder

    # Get the list of images
    images = get_images_from_folder(folder_path)
    if not images:
        print(f"No images found in {folder_path}")
        return

    # Create an iterator to loop over the images
    image_iterator = itertools.cycle(images)
    current_image = next(image_iterator)  # Set the initial image
    is_rotated = False  # Flag to track the rotation state

    # Start the automatic wallpaper changer thread
    interval = 30  # Change interval in seconds
    threading.Thread(target=change_wallpaper_periodically, args=(image_iterator, interval), daemon=True).start()

    def on_keyboard_event(e):
        nonlocal current_image, is_rotated
        if e.name == 'space':  # Change wallpaper to the next image
            current_image = next(image_iterator)
            change_wallpaper(current_image)
            is_rotated = False  # Reset rotation state when changing to the next image
            print("Wallpaper changed to", current_image)
        elif e.name == 'alt':  # Rotate the current image
            if is_rotated:
                change_wallpaper(current_image)  # Set back to the original image
                is_rotated = False
                print("Wallpaper reset to original", current_image)
            else:
                rotated_image = rotate_image(current_image)
                set_wallpaper_from_image(rotated_image)
                is_rotated = True
                print("Wallpaper rotated and changed")

    keyboard.on_press(on_keyboard_event)

    print("Press Space to change the wallpaper, Alt to toggle the current wallpaper rotation.")
    keyboard.wait('esc')  # Change 'esc' to any key you want to use to exit the script

if __name__ == "__main__":
    main()
