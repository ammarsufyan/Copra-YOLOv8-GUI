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

# Serial initialization
ser = serial.Serial('COM3', 115200)

# Load the model
os.makedirs(os.path.dirname("models/"), exist_ok=True)
model = YOLO('../models/segmentation/testing_edible_last.pt')
model.fuse()

# Declare variables
get_datetime_file = datetime.now()
csv_file_path = "logs/log_copra_{}.csv".format(get_datetime_file.strftime("%Y-%m-%d-%S"))

# Declare label left/right line
line = "None"

total_counter = 0
edible_counter = 0
reguler_counter = 0
reject_counter = 0
edibleT_counter = 0
regulerT_counter = 0
rejectT_counter = 0
notDefined_counter = 0
crossed_objects_line_1 = {}

total2_counter = 0
edible2_counter = 0
reguler2_counter = 0
reject2_counter = 0
edibleT2_counter = 0
regulerT2_counter = 0
rejectT2_counter = 0
notDefined2_counter = 0
crossed_objects_line_2 = {}

isRunning = False

video_capture = None

def update_frame(video_capture):
    global line
    
    global total_counter
    global edible_counter
    global reguler_counter
    global reject_counter
    global edibleT_counter
    global regulerT_counter
    global rejectT_counter
    global notDefined_counter
    global crossed_objects_line_1

    global total2_counter
    global edible2_counter
    global reguler2_counter
    global reject2_counter
    global edibleT2_counter
    global regulerT2_counter
    global rejectT2_counter
    global notDefined2_counter
    global crossed_objects_line_2
    
    while isRunning:
        # Read the video frame
        success, frame = video_capture.read()
        point_y = 360 # Atur point_y size sesuai kebutuhan

        # Atur point untuk line_1
        point_x1 = 10 
        point_x2 = 330

        # Atur point untuk line_2
        point2_x1 = 850
        point2_x2 = 1270

        if success:
            # Convert the frame to RGB format
        
            cv2.line(frame, (point_x1, point_y), (point_x2, point_y), (0, 255, 0), 2)
            cv2.line(frame, (point2_x1, point_y), (point2_x2, point_y), (0, 255, 0), 2)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an ImageTk object
            image_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the label with the new image
            image_label.configure(image=image_tk)
            image_label.image = image_tk

            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname("capture_img/"), exist_ok=True)
            # Draw the line on the frame
            
            # Automatically capture the frame
            img_name = "capture_img/capture_img.jpg"
            img_result_name = "capture_img/capture_img_result.jpg"

            # Save the frame as an image file
            cv2.imwrite(img_name, frame)

            results = model.track(img_name, persist=True,conf=0.3, iou=0.5, verbose=False)

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
                    track_ids = r.boxes.id.int().cpu().tolist()
                    class_ids = r.boxes.cls.int().cpu().tolist()
                    confidences = r.boxes.conf.cpu().tolist()
                
                    # Plot the tracks and count objects crossing the line
                    for box, track_id, class_id, confidence in zip(boxes, track_ids, class_ids, confidences):
                        x, y, w, h = box

                        # Convert pixel to cm
                        object_width = int(w) * 0.026458
                        object_height = int(h) * 0.026458

                        # Convert accuracy to percentage
                        accuracy = confidence * 100

                        # Round decimals
                        object_width = round(object_width, 2)
                        object_height = round(object_height, 2)
                        accuracy = round(accuracy, 2)
                        
                        print("Class ID:", class_id)

                        # Check if the object crosses the line 1
                        if point_x1 < x < point_x2 and abs(y - point_y) < 100:
                            if track_id not in crossed_objects_line_1:
                                crossed_objects_line_1[track_id] = True

                                # Get the current datetime
                                get_datetime_now = datetime.now()
                                # Format the datetime as desired
                                formatted_datetime = get_datetime_now.strftime("%Y-%m-%d-%S.%f")          
                                # Mark the line left
                                line = "Left"  
                                
                                if class_id == 0:
                                    edible_counter += 1
                                    total_counter += 1
                                    quality = "Edible"

                                    # Update the text area
                                    update_text(formatted_datetime, quality, accuracy, object_width, object_height, edible_counter, total_counter, line)

                                    # Save to CSV
                                    save_to_csv()

                                    # SERIAL ACTIONS
                                    ser.write("l".encode())
                                elif class_id == 1:
                                    reguler_counter += 1
                                    total_counter += 1
                                    quality = "Reguler"
                                    # Update the text area
                                    update_text(formatted_datetime, quality, accuracy, object_width, object_height, reguler_counter, total_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                                elif class_id == 2:
                                    reject_counter += 1
                                    total_counter += 1
                                    quality = "Reject"
                                    # Update the text area
                                    update_text(formatted_datetime, quality, accuracy, object_width, object_height, reject_counter, total_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                                elif class_id == 3:
                                    edibleT_counter += 1
                                    total_counter += 1
                                    quality = "Edible Telungkup"
                                    # Update the text area
                                    update_text(formatted_datetime, quality, accuracy, object_width, object_height, edibleT_counter, total_counter, line)

                                    # Save to CSV
                                    save_to_csv()

                                    # SERIAL ACTIONS
                                    ser.write("l".encode())
                                elif class_id == 4:
                                    regulerT_counter += 1
                                    total_counter += 1
                                    quality = "Reguler Telungkup"
                                    # Update the text area
                                    update_text(formatted_datetime, quality, accuracy, object_width, object_height, regulerT_counter, total_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                                elif class_id == 5:
                                    rejectT_counter += 1
                                    total_counter += 1
                                    quality = "Reject Telungkup"
                                    # Update the text area
                                    update_text(formatted_datetime, quality, accuracy, object_width, object_height, rejectT_counter, total_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                        # Check if the object crosses the line 2
                        if point2_x1 < x < point2_x2 and abs(y - point_y) < 100:
                            if track_id not in crossed_objects_line_2:
                                crossed_objects_line_2[track_id] = True

                                # Get the current datetime
                                get_datetime_now = datetime.now()
                                # Format the datetime as desired
                                formatted_datetime = get_datetime_now.strftime("%Y-%m-%d-%S.%f")
                                # Mark the line left
                                line = "Right" 

                                if class_id == 0:
                                    edible2_counter += 1
                                    total2_counter += 1
                                    quality = "Edible"

                                    # Update the text area
                                    update_text2(formatted_datetime, quality, accuracy, object_width, object_height, edible2_counter, total2_counter, line)

                                    # Save to CSV
                                    save_to_csv()

                                    # SERIAL ACTIONS
                                    ser.write("r".encode())
                                elif class_id == 1:
                                    reguler2_counter += 1
                                    total2_counter += 1
                                    quality = "Reguler"

                                    # Update the text area
                                    update_text2(formatted_datetime, quality, accuracy, object_width, object_height, reguler2_counter, total2_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                                elif class_id ==2:
                                    reject2_counter += 1
                                    total2_counter += 1
                                    quality = "Reject"

                                    # Update the text area
                                    update_text2(formatted_datetime, quality, accuracy, object_width, object_height, reject2_counter, total2_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                                elif class_id ==3:
                                    edibleT2_counter += 1
                                    total2_counter += 1
                                    quality = "Edible Telungkup"

                                    # Update the text area
                                    update_text2(formatted_datetime, quality, accuracy, object_width, object_height, edibleT2_counter, total2_counter, line)

                                    # Save to CSV
                                    save_to_csv()

                                    # SERIAL ACTIONS
                                    ser.write("r".encode())
                                elif class_id == 4:
                                    regulerT2_counter += 1
                                    total2_counter += 1
                                    quality = "Reguler Telungkup"

                                    # Update the text area
                                    update_text2(formatted_datetime, quality, accuracy, object_width, object_height, regulerT2_counter, total2_counter, line)

                                    # Save to CSV
                                    save_to_csv()
                                elif class_id ==5:
                                    rejectT2_counter += 1
                                    total2_counter += 1
                                    quality = "Reject Telungkup"

                                    # Update the text area
                                    update_text2(formatted_datetime, quality, accuracy, object_width, object_height, rejectT2_counter, total2_counter, line)

                                    # Save to CSV
                                    save_to_csv()
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
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
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

def update_text(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter, line):
    text_area.configure(state='normal')
    text_area.insert("end", "\n Time: {} \n Quality: {} \n Accuracy: {}% \n Width: {} cm \n Height: {} cm \n Class_Counter: {} \n Total_Counter: {} \n Line: {} \n"
                     .format(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter, line))
    text_area.configure(state='disabled')
    text_area.see("end")

def update_text2(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter, line):
    text_area2.configure(state='normal')
    text_area2.insert("end", "\n Time: {} \n Quality: {} \n Accuracy: {}% \n Width: {} cm \n Height: {} cm \n Class_Counter: {} \n Total_Counter: {} \n Line: {} \n"
                     .format(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter, line))
    text_area2.configure(state='disabled')
    text_area2.see("end")

def save_to_csv():
    # Get the current contents of the text_area widget
    text_contents = text_area.get("1.0", "end-1c")
    text2_contents = text_area2.get("1.0", "end-1c")

    # Extract the values from the text contents
    lines = text_contents.split("\n")
    lines2 = text2_contents.split("\n")
    data = [line.split(": ")[1] for line in lines if line]
    data2 = [line.split(": ")[1] for line in lines2 if line]

    # Define the header row and data rows
    header_row = ["Time", "Quality", "Accuracy", "Width", "Height", "Class_Counter", "Total_Counter", "Line"]
    data_rows = [data[i:i+8] for i in range(0, len(data), 8)] 
    data2_rows = [data2[i:i+8] for i in range(0, len(data), 8)] 
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname("logs/"), exist_ok=True)

    # Write the contents to the CSV file
    with open(csv_file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header_row) 
        writer.writerows(data_rows)
        writer.writerows(data2_rows)

# Create the main window
window = tk.Tk()
window.title("Copra Detection GUI")

# Create the left frame
left_frame = ttk.Frame(window)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create the right frame
right_frame = ttk.Frame(window)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

line_frame = ttk.Frame(left_frame)
line_frame.pack(fill=tk.BOTH, expand=True)

text_frame = ttk.Frame(left_frame)
text_frame.pack(fill=tk.BOTH, expand=True)

# Create a label for Line L
line_label_left = ttk.Label(line_frame, text="LEFT", font=("TkDefaultFont", 15))
line_label_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.NONE, expand=True)

# Create a text area in the left frame
text_area = tk.Text(text_frame, width=30, height=15)
text_area.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.NONE, expand=True)

# Create a label for Line R
line_label_right = ttk.Label(line_frame, text="RIGHT", font=("TkDefaultFont", 15))
line_label_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.NONE, expand=True)

# Create a text area in the right frame
text_area2 = tk.Text(text_frame, width=30, height=15)
text_area2.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.NONE, expand=True)

# Increase the font size of the text area
text_font = font.Font(size=15)  # Adjust the font size as desired
text_area.configure(font=text_font, state='disabled')
text_area2.configure(font=text_font, state='disabled')

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