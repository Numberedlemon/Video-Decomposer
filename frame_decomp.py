import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
import os
import time

def extract_frames(video_path, output_dir, progress_var, progress_label, time_label, size_label):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        progress_label.config(text="Error: Could not open video.")
        return

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0

    start_time = time.time()

    while True:
        # Read the next frame
        ret, frame = cap.read()
        
        # If there are no more frames, break the loop
        if not ret:
            break

        # Construct the output path for the frame
        frame_filename = os.path.join(output_dir, f'frame_{frame_count:04d}.png')

        # Save the frame as an image file
        cv2.imwrite(frame_filename, frame)

        # Increment the frame count
        frame_count += 1

        # Update progress bar and estimated time
        elapsed_time = time.time() - start_time
        estimated_total_time = (elapsed_time / frame_count) * total_frames
        remaining_time = estimated_total_time - elapsed_time

        progress_var.set((frame_count / total_frames) * 100)
        progress_label.config(text=f"Processing: {frame_count}/{total_frames} frames")
        time_label.config(text=f"Elapsed Time: {elapsed_time:.2f}s, Estimated Time Left: {remaining_time:.2f}s")

        root.update_idletasks()

    # Release the video capture object
    cap.release()

    total_time = time.time() - start_time
    progress_label.config(text=f"Extracted {frame_count} frames to {output_dir}")
    time_label.config(text=f"Total Time Taken: {total_time:.2f}s")

    # Calculate the total size of decomposed frames
    total_frame_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in os.listdir(output_dir))
    total_frame_size_mb = total_frame_size / (1024 * 1024)

    # Calculate decompression ratio
    initial_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    decompression_ratio = total_frame_size_mb / initial_size_mb

    size_label.config(text=f"Total Frames Size: {total_frame_size_mb:.2f} MB (Decompression Ratio: {decompression_ratio:.2f})")

def select_file():
    # Open file dialog to select a video file
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
    if file_path:
        # Display the selected file name
        lbl_file_name.config(text=f"Selected File: {os.path.basename(file_path)}")
        
        # Display the initial file size
        initial_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        size_label.config(text=f"Initial File Size: {initial_size:.2f} MB")
        
        # Create an output directory
        output_dir = 'extracted_frames'
        os.makedirs(output_dir, exist_ok=True)
        
        # Reset progress bar and labels
        progress_var.set(0)
        progress_label.config(text="")
        time_label.config(text="")
        total_frame_size_label.config(text="")

        # Extract frames from the selected video
        extract_frames(file_path, output_dir, progress_var, progress_label, time_label, total_frame_size_label)

# Create the main window
root = tk.Tk()
root.title("Video Frame Extractor")
root.geometry("500x400")  # Set the window size to 500x400 pixels

# Create a label with instructions
lbl_instructions = tk.Label(root, text="Select a video file to extract frames:", font=("Arial", 14))
lbl_instructions.pack(pady=10)

# Create a button to open the file dialog
btn_select_file = tk.Button(root, text="Select Video File", command=select_file, font=("Arial", 12))
btn_select_file.pack(pady=10)

# Create a label to display the selected file name
lbl_file_name = tk.Label(root, text="No file selected", font=("Arial", 12))
lbl_file_name.pack(pady=10)

# Create a label to display the initial file size
size_label = tk.Label(root, text="", font=("Arial", 12))
size_label.pack(pady=5)

# Create a progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=10)

# Create a label to display the progress status
progress_label = tk.Label(root, text="", font=("Arial", 12))
progress_label.pack(pady=5)

# Create a label to display the time estimate
time_label = tk.Label(root, text="", font=("Arial", 12))
time_label.pack(pady=5)

# Create a label to display the total frames size
total_frame_size_label = tk.Label(root, text="", font=("Arial", 12))
total_frame_size_label.pack(pady=5)

# Start the GUI event loop
root.mainloop()