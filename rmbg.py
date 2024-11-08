from rembg import remove
from PIL import Image
import os

def user_input():
    """Prompt the user for input and output paths."""
    inpath = input("Input image path: ")
    outpath = input("Output image path: ")
    return inpath, outpath

def remove_bg(inpath, outpath):
    """Remove the background from the image and save the output."""
    try:
        inp = Image.open(inpath)
        output = remove(inp)
        output.save(outpath)
        print("Image background removed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def go_again():
    """Ask the user if they want to open the image and/or manipulate another image."""
    open_choice = input("Open with default image viewer? (Y/N): ").strip().upper()
    if open_choice == 'Y':
        os.system(f'xdg-open "{outpath}"' if os.name == 'posix' else f'start {outpath}')

    restart_choice = input("Manipulate another image? (Y/N): ").strip().upper()
    return restart_choice == 'Y'

def main():
    """Main function to control the flow of the program."""
    while True:
        inpath, outpath = user_input()
        remove_bg(inpath, outpath)
        
        if not go_again():
            print("Exiting program.")
            break

if __name__ == "__main__":
    main()
