# Delusional Blob Extreme Pro
https://youtu.be/oL0vm4w4D3Y
![5472232224725266954](https://github.com/user-attachments/assets/1fc7e7ef-c733-48c7-a8f1-c0026d78b3b4)

**Delusional Blob Extreme Pro** is a modern, powerful video blob detection and visualization tool. It allows you to analyze and process videos, tracking moving blobs with advanced controls and beautiful, real-time GUI feedback. Designed for creatives, researchers, and anyone fascinated by motion and computer vision.

## Features

- **Modern GUI** with dark theme (ttkbootstrap)
- **Load and save videos** in various formats
- **Real-time motion and blob detection** using OpenCV
- **Customizable controls** for blob area, motion threshold, connection distance, trail opacity, and more
- **Live preview** of processing results
- **Activity log** and progress timeline
- **Splash screen** and professional UI
- **Fast, multi-threaded video processing**

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/CEONEINDEDALUS/Blob-editor.git
cd Blob-editor
```

### 2. Install dependencies

It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the application

```bash
python blobeditor.py
```

## Usage

1. Launch the app: `python blobeditor.py`
2. Click **Load Video** to select your input video.
3. Click **Save As** to set your output video location.
4. Use the **Control Panel** to adjust parameters:
   - **Min Blob Area:** Minimum area for detected blobs.
   - **Motion Threshold:** Sensitivity to motion.
   - **Blob Size Scale:** Size scaling for blobs.
   - **Connection Distance:** Distance for drawing lines between blobs.
   - **Trail Opacity:** Opacity of blob motion trails.
   - **Bitrate:** Output video quality.
   - **Output Resolution:** Size of the output video.
5. Click **Unleash Blobs!** to process.
6. Watch progress in the timeline and live preview.

## Requirements

- Python 3.8+
- See [requirements.txt](requirements.txt) for all dependencies

## Contributing

Pull requests, bug reports, and suggestions are welcome!

## License

[MIT](LICENSE)

---

**Delusional Blob Extreme Pro** - because every blob deserves a story.
