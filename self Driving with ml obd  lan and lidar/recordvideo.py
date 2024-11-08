#!/usr/bin/python3
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

def record_video():
    """
    Records video using the PiCamera2 with an H264 encoder and saves it to 'ml.mp4'.
    Recording stops when the user presses Ctrl+C.
    """
    picam2 = Picamera2()
    # Configure video settings
    config = picam2.create_video_configuration(
        main={"size": (2048, 1536)},
        lores={"size": (480, 240)},
        encode="lores"
    )
    picam2.configure(config)

    # Initialize encoder and output
    encoder = H264Encoder(10000000)
    output = FfmpegOutput('ml.mp4')

    try:
        # Start recording
        picam2.start_recording(encoder, output)
        print("Recording started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)  # Keep recording until interrupted

    except KeyboardInterrupt:
        # Handle Ctrl+C to stop recording gracefully
        print("Recording stopped by user.")

    except Exception as e:
        # Handle unexpected errors
        print(f"An error occurred: {e}")

    finally:
        # Ensure recording stops and resources are freed
        picam2.stop_recording()
        print("Recording has been properly stopped.")

if __name__ == "__main__":
    record_video()
