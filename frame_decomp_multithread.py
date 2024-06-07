import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
import os
import time
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed

def save_frame(frame, frame_filename):
    cv2.imwrite(frame_filename, frame)

def extract_frames(video_path, output_dir, max_workers):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        return False, "Error: Could not open video."

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0

    start_time = time.time()

    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            # Read the next frame
            ret, frame = cap.read()
            
            # If there are no more frames, break the loop
            if not ret:
                break

            # Construct the output path for the frame
            frame_filename = os.path.join(output_dir, f'frame_{frame_count:04d}.png')

            # Submit the frame saving task to the executor
            futures.append(executor.submit(save_frame, frame, frame_filename))

            # Increment the frame count
            frame_count += 1

    # Wait for all threads to complete
    for future in as_completed(futures):
        future.result()

    # Release the video capture object
    cap.release()

    total_time = time.time() - start_time

    # Calculate additional metrics
    initial_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    total_frames_size_mb = sum(os.path.getsize(os.path.join(output_dir, f)) for f in os.listdir(output_dir)) / (1024 * 1024)

    # Calculate compression ratio
    compression_ratio = total_frames_size_mb / initial_size_mb

    # Calculate average frame extraction time
    avg_frame_extraction_time = total_time / frame_count if frame_count > 0 else 0

    # Calculate frames per second (FPS)
    fps = frame_count / total_time if total_time > 0 else 0

    # Calculate CPU and memory utilization
    cpu_utilization = psutil.cpu_percent()
    memory_utilization = psutil.virtual_memory().percent

    return True, {
        "frame_count": frame_count,
        "total_time": total_time,
        "total_frames_size_mb": total_frames_size_mb,
        "compression_ratio": compression_ratio,
        "avg_frame_extraction_time": avg_frame_extraction_time,
        "fps": fps,
        "cpu_utilization": cpu_utilization,
        "memory_utilization": memory_utilization
    }

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

        # Get the number of threads from the entry widget
        try:
            max_workers = int(entry_threads.get())
        except ValueError:
            max_workers = 1  # Default to 1 thread if invalid input

        # Extract frames from the selected video
        extract_frames(file_path, output_dir, progress_var, progress_label, time_label, total_frame_size_label, max_workers)

# Create the main window
root = tk.Tk()
root.title("Video Frame Extractor")
root.geometry("500x400")  # Set the window size to 500x500 pixels

# Create a label with instructions
lbl_instructions = tk.Label(root, text="Select a video file to decompose:", font=("Arial", 14))
lbl_instructions.pack(pady=10)

# Create a button to open the file dialog
btn_select_file = tk.Button(root, text="Select Video File", command=select_file, font=("Arial", 12))
btn_select_file.pack(pady=10)

# Create a label and entry widget to input the number of threads
lbl_threads = tk.Label(root, text="Number of Threads:", font=("Arial", 12))
lbl_threads.pack(pady=5)
entry_threads = tk.Entry(root, font=("Arial", 12), width=3)
entry_threads.pack(pady=5)
entry_threads.insert(0, "4")  # Default to 4 threads

# Create a label to display the selected file name
lbl_file_name = tk.Label(root, text="No file selected", font=("Arial", 12))
lbl_file_name.pack(pady=10)

# Create a label to display the initial file size
size_label = tk.Label(root, text="", font=("Arial", 12))
size_label.pack(pady=5)

# Create a progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=5)

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