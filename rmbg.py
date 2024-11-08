from rembg import remove
from PIL import Image
import os

def user_input():
    """Prompt the user for input: single image or folder."""
    choice = input("Would you like to manipulate a single image or a folder of images? (Enter 'image' or 'folder'): ").strip().lower()
    if choice == 'image':
        inpath = input("Input image path: ")
        outpath = input("Output image path (will be saved as PNG): ")
        return 'image', inpath, outpath
    elif choice == 'folder':
        in_folder = input("Input folder path: ")
        out_folder = input("Output folder path (images will be saved as PNG): ")
        return 'folder', in_folder, out_folder
    else:
        print("Invalid input. Please enter 'image' or 'folder'.")
        return user_input()

def remove_bg_image(inpath, outpath):
    """Remove the background from a single image and save as PNG."""
    try:
        inp = Image.open(inpath)
        output = remove(inp)
        
        # Ensure the output path has a .png extension
        if not outpath.lower().endswith('.png'):
            outpath = os.path.splitext(outpath)[0] + '.png'
        
        output.save(outpath, "PNG")
        print(f"Background removed for image: {inpath}, saved as {outpath}")
    except Exception as e:
        print(f"An error occurred with {inpath}: {e}")

def remove_bg_folder(in_folder, out_folder):
    """Remove the background for all images in a folder and save as PNG."""
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
        
    for filename in os.listdir(in_folder):
        inpath = os.path.join(in_folder, filename)
        outpath = os.path.join(out_folder, os.path.splitext(filename)[0] + '.png')  # Save all images as PNG
        
        if os.path.isfile(inpath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            remove_bg_image(inpath, outpath)
        else:
            print(f"Skipping non-image file: {filename}")

def go_again():
    """Ask the user if they want to manipulate another image or folder."""
    restart_choice = input("Would you like to manipulate another image or folder? (Y/N): ").strip().upper()
    return restart_choice == 'Y'

def main():
    """Main function to control the flow of the program."""
    while True:
        mode, inpath, outpath = user_input()
        
        if mode == 'image':
            remove_bg_image(inpath, outpath)
        elif mode == 'folder':
            remove_bg_folder(inpath, outpath)
        
        if not go_again():
            print("Exiting program.")
            break

if __name__ == "__main__":
    main()
