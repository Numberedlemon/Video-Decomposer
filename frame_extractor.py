import os
import argparse
import cv2
import time
import psutil
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def save_frame(frame, frame_filename):
    cv2.imwrite(frame_filename, frame)

def extract_frames(video_path, output_dir, max_workers, progress_callback=None):
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

            # Construct the output directory for the video frames
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            video_output_dir = os.path.join(output_dir, video_name)
            os.makedirs(video_output_dir, exist_ok=True)

            # Construct the output path for the frame
            frame_filename = os.path.join(video_output_dir, f'frame_{frame_count:04d}.png')

            # Submit the frame saving task to the executor
            future = executor.submit(save_frame, frame, frame_filename)

            # Increment the frame count
            frame_count += 1

            # Update progress
            if progress_callback:
                progress_callback((frame_count / total_frames) * 100)

    # Wait for all threads to complete
    for future in as_completed(futures):
        future.result()

    # Release the video capture object
    cap.release()

    total_time = time.time() - start_time

    # Calculate additional metrics
    initial_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    total_frames_size_mb = sum(os.path.getsize(os.path.join(video_output_dir, f)) for f in os.listdir(video_output_dir)) / (1024 * 1024)

    # Calculate compression ratio
    compression_ratio = total_frames_size_mb / initial_size_mb

    # Calculate average frame extraction time
    avg_frame_extraction_time = total_time / frame_count if frame_count > 0 else 0

    # Calculate frames per second (FPS)
    fps = frame_count / total_time if total_time > 0 else 0

    # Calculate CPU and memory utilization
    cpu_utilization = psutil.cpu_percent()
    memory_utilization = psutil.virtual_memory().percent

    # Save metadata to a JSON file
    metadata = {
        "frame_count": frame_count,
        "total_time": total_time,
        "total_frames_size_mb": total_frames_size_mb,
        "compression_ratio": compression_ratio,
        "avg_frame_extraction_time": avg_frame_extraction_time,
        "fps": fps,
        "cpu_utilization": cpu_utilization,
        "memory_utilization": memory_utilization
    }
    metadata_filename = os.path.join(video_output_dir, 'metadata.json')
    with open(metadata_filename, 'w') as f:
        json.dump(metadata, f)

    return True, metadata

def parse_args():
    parser = argparse.ArgumentParser(description="Decompose video files into individual frames.")
    parser.add_argument("input_dir", type=str, help="Path to the directory containing input video files.")
    parser.add_argument("output_dir", type=str, help="Path to the output directory.")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of worker threads.")
    return parser.parse_args()

def main():
    args = parse_args()

    # Get the list of video files in the input directory
    video_files = [f for f in os.listdir(args.input_dir) if f.endswith(('.avi', '.mp4'))]

    for video_file in video_files:
        video_path = os.path.join(args.input_dir, video_file)
        success, metadata = extract_frames(video_path, args.output_dir, args.max_workers)
        if success:
            print(f"Decomposed {video_path}  into {metadata['frame_count']} frames.")
            print(f"Total Time Taken: {metadata['total_time']:.2f}s")
            print(f"Decomposed Disk Space: {metadata['total_frames_size_mb']:.2f} MB")
            print(f"Decompression Ratio: {metadata['compression_ratio']:.2f}")
            print(f"Average Frame Decomposition Time: {metadata['avg_frame_extraction_time']:.6f}s")
            print(f"Frames per Second (FPS): {metadata['fps']:.2f}")
            print(f"CPU Utilization: {metadata['cpu_utilization']:.2f}%")
            print(f"Memory Utilization: {metadata['memory_utilization']:.2f}%")
            print()
        else:
            print(f"Decomposition failed for {video_file}.")

if __name__ == "__main__":
    main()