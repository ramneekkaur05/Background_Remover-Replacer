from PIL import Image, ImageTk
from rembg import remove
import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

def remove_bg_add_color(img, bg_color=(255, 255, 255)):
    try:
        # Convert image to RGBA if it's not
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Remove background
        output_image = remove(img)

        # Convert back to numpy array
        output_image = np.array(output_image)
        
        # Check if the image has an alpha channel
        if output_image.shape[2] != 4:  # Check for RGBA channels
            raise ValueError("Processed image does not have an alpha channel.")
        
        # Split the output image into RGB and alpha channels
        r, g, b, a = cv.split(output_image)
        rgb_img = cv.merge((r, g, b))
        
        # Create a solid color background
        bg_img = np.zeros_like(rgb_img, dtype=np.uint8)
        bg_img[:, :] = bg_color  # Set RGB
        
        # Normalize the alpha channel
        alpha_channel = a / 255.0
        
        # Blend the images using the alpha channel
        blended_img = np.zeros_like(rgb_img, dtype=np.uint8)
        for c in range(3):  # RGB channels
            blended_img[:, :, c] = (alpha_channel * rgb_img[:, :, c] + 
                                    (1 - alpha_channel) * bg_color[c])
        
        return Image.fromarray(blended_img)

    except Exception as e:
        raise ValueError(f"Error in remove_bg_add_color: {e}")

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return
    
    global img
    img = Image.open(file_path)
    img_tk = ImageTk.PhotoImage(img)
    original_label.config(image=img_tk)
    original_label.image = img_tk

def process_image():
    try:
        global processed_img
        bg_color_str = bg_color_entry.get()
        bg_color = tuple(map(int, bg_color_str.split(',')))
        if len(bg_color) != 3 or not all(0 <= val <= 255 for val in bg_color):
            raise ValueError
        
        processed_img = remove_bg_add_color(img, bg_color)
        processed_img_tk = ImageTk.PhotoImage(processed_img)
        
        processed_label.config(image=processed_img_tk)
        processed_label.image = processed_img_tk
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_image():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        processed_img.save(file_path)

# Tkinter app
root = tk.Tk()
root.title("Background Remover and Replacer")

# Open image button
open_btn = tk.Button(root, text="Open Image", command=open_image)
open_btn.pack()

# Original image label
original_label = tk.Label(root)
original_label.pack()

# Background color input
bg_color_label = tk.Label(root, text="Enter the background color as R,G,B (e.g., 255,0,0 for red):")
bg_color_label.pack()
bg_color_entry = tk.Entry(root)
bg_color_entry.pack()
bg_color_entry.insert(0, "255,255,255")

# Process image button
process_btn = tk.Button(root, text="Process Image", command=process_image)
process_btn.pack()

# Processed image label
processed_label = tk.Label(root)
processed_label.pack()

# Save image button
save_btn = tk.Button(root, text="Save Image", command=save_image)
save_btn.pack()

root.mainloop()
