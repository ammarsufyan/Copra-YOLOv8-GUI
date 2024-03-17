import csv
import os
import threading
import tkinter as tk
from datetime import datetime
from time import sleep
from tkinter import font, messagebox, ttk
import cv2
import serial
from PIL import Image, ImageTk
from ultralytics import YOLO
from itertools import zip_longest

# Serial initialization
ser = serial.Serial('COM14', 115200)
infrared = serial.Serial('COM4', 115200)

# Load the model
os.makedirs(os.path.dirname("../models/"), exist_ok=True)
model = YOLO('../models/KopraV11_YOLOv8m_Segmentation_Epoch100/weights/best.pt')
model.fuse()

# Declare variables
get_datetime_file = datetime.now()
csv_file_path = "logs/log_copra_{}.csv".format(get_datetime_file.strftime("%Y-%m-%d-%S"))

total_counter = 0
edible_counter = 0
non_edible_counter = 0

isRunning = False

video_capture = None

def update_frame(video_capture):
    
    global total_counter
    global edible_counter
    global non_edible_counter
    
    while isRunning:
        # Read the video frame
        success, frame = video_capture.read()

        if success:
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an ImageTk object
            image_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the label with the new image
            image_label.configure(image=image_tk)
            image_label.image = image_tk
            
            if infrared.inWaiting() > 0:
                # Trigger 'OBSTACLE' from Serial
                baca = infrared.readline()
                if baca == b'OBSTACLE\r\n':
                    # Check
                    print("Terdeteksi")
                    # Create the directory if it doesn't exist
                    os.makedirs(os.path.dirname("capture_img/"), exist_ok=True)
                    
                    # Automatically capture the frame
                    img_name = "capture_img/capture_img.jpg"
                    img_result_name = "capture_img/capture_img_result.jpg"

                    # Save the frame as an image file
                    cv2.imwrite(img_name, frame)

                    results = model.track(img_name, persist=True, conf=0.5, iou=0.5, verbose=False)
                    for r in results:
                        im_array = r.plot()
                        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
                        im.save(img_result_name)  # save image

                        # Show it to the GUI
                        image_tk = ImageTk.PhotoImage(Image.open(img_result_name))
                        # Update the label with the new image
                        image_label.configure(image=image_tk)
                        image_label.image = image_tk

                        if r.boxes.id is not None:
                            # Get the boxes, track IDs and classes
                            boxes = r.boxes.xywh.cpu()
                            class_ids = r.boxes.cls.int().cpu().tolist()
                            confidences = r.boxes.conf.cpu().tolist()
                        
                            # Plot the tracks and count objects crossing the line
                            for box, class_id, confidence in zip_longest(boxes, class_ids, confidences):
                                if box is not None and class_id is not None and confidence is not None:
                                    _, _, w, h = box

                                    # Convert pixel to cm
                                    object_width = int(w) * 0.026458
                                    object_height = int(h) * 0.026458

                                    # Convert accuracy to percentage
                                    accuracy = confidence * 100

                                    # Round decimals
                                    object_width = round(object_width, 2)
                                    object_height = round(object_height, 2)
                                    accuracy = round(accuracy, 2)

                                    # Get the current datetime
                                    get_datetime_now = datetime.now()
                                    
                                    # Format the datetime as desired
                                    formatted_datetime = get_datetime_now.strftime("%Y-%m-%d-%S.%f")          
                                    
                                    if class_id == 0 or class_id == 1:
                                        edible_counter += 1
                                        total_counter += 1
                                        quality = "Edible"

                                        # Update the text area
                                        update_text(formatted_datetime, quality, accuracy, object_width, object_height, edible_counter, total_counter)

                                        # Save to CSV
                                        save_to_csv()

                                        # SERIAL ACTIONS
                                        ser.write("r".encode())
                                    if class_id == 2 or class_id == 3:
                                        non_edible_counter += 1
                                        total_counter += 1
                                        quality = "Non-Edible"

                                        # Update the text area
                                        update_text(formatted_datetime, quality, accuracy, object_width, object_height, non_edible_counter, total_counter)

                                        # Save to CSV
                                        save_to_csv()
                                        
                                        # SERIAL ACTIONS
                                        ser.write("l".encode())
                else:
                    print("Tidak Terdeteksi")
            
def black_screen():
    sleep(0.5)
    image_label.configure(image=placeholder_image)
    image_label.image = placeholder_image

def start_detection():
    global video_capture, isRunning
    if video_capture is None:
        isRunning = True
        # Start the camera (Use 0 for the default camera)
        video_capture = cv2.VideoCapture(0)
        # Start the thread
        x = threading.Thread(target=update_frame, args=[video_capture], daemon=True)
        x.start()
    else:
        show_alert("Information", "Detection is already running")

def stop_detection():
    global video_capture, isRunning
    if video_capture is not None:
        isRunning = False
        # Stop the camera
        video_capture.release()
        video_capture = None
        # Start the thread
        x = threading.Thread(target=black_screen, daemon=True)
        x.start()
    else:
        show_alert("Information", "Detection is not running")

def show_alert(subject, message):
    messagebox.showinfo(subject, message)

def update_text(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter):
    text_area.configure(state='normal')
    text_area.insert("end", "\n Time: {} \n Quality: {} \n Accuracy: {}% \n Width: {} cm \n Height: {} cm \n Class_Counter: {} \n Total_Counter: {} \n"
                     .format(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter))
    text_area.configure(state='disabled')
    text_area.see("end")


def save_to_csv():
    # Get the current contents of the text_area widget
    text_contents = text_area.get("1.0", "end-1c")

    # Extract the values from the text contents
    lines = text_contents.split("\n")
    data = [line.split(": ")[1] for line in lines if line]

    # Define the header row and data rows
    header_row = ["Time", "Quality", "Accuracy", "Width", "Height", "Class_Counter", "Total_Counter", "Line"]
    data_rows = [data[i:i+8] for i in range(0, len(data), 8)] 
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname("logs/"), exist_ok=True)

    # Write the contents to the CSV file
    with open(csv_file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header_row) 
        writer.writerows(data_rows)

# Create the main window
window = tk.Tk()
window.title("Copra Detection GUI")

# Create the left frame
left_frame = ttk.Frame(window)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create the right frame
right_frame = ttk.Frame(window)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a text area in the left frame
text_area = tk.Text(left_frame, width=30, height=10)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Increase the font size of the text area
text_font = font.Font(size=20)  # Adjust the font size as desired
text_area.configure(font=text_font, state='disabled')

# Create the start button
start_button = ttk.Button(left_frame, text="Start", command=start_detection)
start_button.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

# Create a label to display the OpenCV frame
image_label = ttk.Label(right_frame)
image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create the stop button
stop_button = ttk.Button(right_frame, text="Stop", command=stop_detection)
stop_button.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

# Start with the placeholder image
placeholder_image = ImageTk.PhotoImage(Image.new('RGB', (640, 480)))
image_label.configure(image=placeholder_image)
image_label.image = placeholder_image

# Start the GUI event loop
window.mainloop()