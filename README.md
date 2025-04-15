# Video Compression Application

An easy-to-use video compression application with a modern interface. Using FFmpeg, you can adjust the quality and size of your videos to your desired level.

## Features

- Single or multiple video file selection
- 5 different quality levels (Very High - Very Low)
- Intuitive and modern interface
- Detailed result information (size savings, percentage info)
- Batch processing support
- Dark mode theme

## Requirements

- Python 3.6 or higher
- FFmpeg (must be added to PATH)
- The following Python packages:
  - tkinter
  - Pillow
  - subprocess

## Installation

1. Clone or download this repository
   ```bash
   git clone https://github.com/username/video-compressor.git
   cd video-compressor
   ```

2. Install required packages
   ```bash
   pip install pillow
   ```

3. Install [FFmpeg](https://ffmpeg.org/download.html) and add it to PATH
   - For Windows: [FFmpeg Windows Installation Guide](https://www.wikihow.com/Install-FFmpeg-on-Windows)
   - For macOS: `brew install ffmpeg`
   - For Linux: `apt-get install ffmpeg`

## Usage

1. Start the application
   ```bash
   python main.py
   ```

2. Video selection:
   - Add your videos using the "Select Single Video" or "Select Multiple Videos" buttons
   - You can remove selected videos from the list or clear the entire list

3. Quality settings:
   - Select the quality level from the dropdown menu (Very High, High, Medium, Low, Very Low)
   - Specify the output folder using the "Browse" button

4. Click the "Process Video" button to start the compression

5. Once completed, the result information will be displayed on the screen

## Technical Details

This application performs video compression using the H.264 codec with FFmpeg. Quality levels are adjusted with CRF (Constant Rate Factor) values:

| Quality Level | CRF Value | Description |
|---------------|-----------|-------------|
| Very High     | 17        | Almost lossless, large file size |
| High          | 20        | Good quality with no visible loss |
| Medium        | 23        | Balanced quality/size ratio (default) |
| Low           | 28        | Noticeable quality loss, small file size |
| Very Low      | 35        | Significant quality loss, very small file size |


## License

This project is licensed under the [MIT License](LICENSE) - see the license file for details.
