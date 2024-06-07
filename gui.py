import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
import threading
import frame_extractor

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
        compression_ratio_label.config(text="")
        avg_extraction_time_label.config(text="")
        fps_label.config(text="")
        cpu_utilization_label.config(text="")
        memory_utilization_label.config(text="")

        # Get the number of threads from the entry widget
        try:
            max_workers = int(entry_threads.get())
        except ValueError:
            max_workers = 1  # Default to 1 thread if invalid input

        # Start frame extraction in a separate thread
        threading.Thread(target=extract_frames_thread, args=(file_path, output_dir, max_workers)).start()

def extract_frames_thread(video_path, output_dir, max_workers):
    success, result = frame_extractor.extract_frames(video_path, output_dir, max_workers, update_progress)
    if success:
        progress_label.config(text=f"Extracted {result['frame_count']} frames to {output_dir}")
        time_label.config(text=f"Total Time Taken: {result['total_time']:.2f}s")
        total_frame_size_label.config(text=f"Total Frames Size: {result['total_frames_size_mb']:.2f} MB")
        compression_ratio_label.config(text=f"Compression Ratio: {result['compression_ratio']:.2f}")
        avg_extraction_time_label.config(text=f"Average Extraction Time: {result['avg_frame_extraction_time']:.6f}s")
        fps_label.config(text=f"Frames per Second (FPS): {result['fps']:.2f}")
        cpu_utilization_label.config(text=f"CPU Utilization: {result['cpu_utilization']:.2f}%")
        memory_utilization_label.config(text=f"Memory Utilization: {result['memory_utilization']:.2f}%")
    else:
        progress_label.config(text=result)

def update_progress(progress):
    progress_var.set(progress)

# Create the main window
root = tk.Tk()
root.title("Video Frame Extractor")
root.geometry("600x500")  # Set the window size

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

# Create labels for additional metrics
time_label = tk.Label(root, text="", font=("Arial", 12))
time_label.pack(pady=5)

total_frame_size_label = tk.Label(root, text="", font=("Arial", 12))
total_frame_size_label.pack(pady=5)

compression_ratio_label = tk.Label(root, text="", font=("Arial", 12))
compression_ratio_label.pack(pady=5)

avg_extraction_time_label = tk.Label(root, text="", font=("Arial", 12))
avg_extraction_time_label.pack(pady=5)

fps_label = tk.Label(root, text="", font=("Arial", 12))
fps_label.pack(pady=5)

cpu_utilization_label = tk.Label(root, text="", font=("Arial", 12))
cpu_utilization_label.pack(pady=5)

memory_utilization_label = tk.Label(root, text="", font=("Arial", 12))
memory_utilization_label.pack(pady=5)

# Create a label and entry widget to input the number of threads
lbl_threads = tk.Label(root, text="Number of Threads:", font=("Arial", 12))
lbl_threads.pack(pady=5)
entry_threads = tk.Entry(root, font=("Arial", 12), width=5)  # Adjust width as needed
entry_threads.pack(pady=5)
entry_threads.insert(0, "4")  # Default to 4 threads

# Start the GUI event loop
root.mainloop()