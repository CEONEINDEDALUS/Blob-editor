import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
from PIL import Image, ImageTk
import tkinter.font as tkFont
from ttkbootstrap import Style  # Using ttkbootstrap for modern themes
import threading

class DelusionalMotionVideoBlobEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Delusional Blob Extreme Pro")
        self.root.geometry("2200x1400")
        self.root.configure(bg="#0a0a0a")  # Darker background for modern feel

        # Core variables
        self.input_path = self.output_path = None
        self.video = self.writer = None
        self.running = False
        self.objects = {}
        self.object_id = self.frame_count = self.total_frames = 0
        self.prev_gray = None
        self.trail_buffer = []
        self.preview_photo = None

        # OpenCV constants
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (180, 180, 180)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.4
        self.line_thickness = 1
        self.shadow_offset = 2

        # Tkinter variables
        self.blob_size_scale = tk.DoubleVar(value=0.5)
        self.max_connection_distance = tk.IntVar(value=150)
        self.motion_threshold = tk.DoubleVar(value=1.0)
        self.min_area = tk.IntVar(value=50)
        self.trail_opacity = tk.DoubleVar(value=0.2)
        self.output_resolution = tk.StringVar(value="Match Input")
        self.bitrate = tk.IntVar(value=100000)

        # Initialize blob detector and GUI
        self._setup_blob_detector()
        self._apply_theme()
        self._setup_gui()

    def _apply_theme(self):
        # Apply a modern ttkbootstrap theme
        self.style = Style(theme="darkly")  # Darkly theme for a sleek look
        self.root.configure(bg=self.style.colors.bg)
        self.custom_font = tkFont.Font(family="Montserrat", size=14, weight="bold")
        self.header_font = tkFont.Font(family="Montserrat", size=28, weight="bold")

    def _setup_blob_detector(self):
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = 5
        params.maxThreshold = 250
        params.filterByArea = True
        params.minArea = self.min_area.get()
        params.maxArea = 25000
        params.filterByCircularity = False
        params.filterByConvexity = False
        params.filterByInertia = False
        self.blob_detector = cv2.SimpleBlobDetector_create(params)

    def _update_blob_detector(self):
        self._setup_blob_detector()

    def _setup_gui(self):
        # Header
        header = tk.Frame(self.root, bg=self.style.colors.primary, height=80)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(
            header,
            text="Delusional Blob Extreme Pro",
            font=self.header_font,
            bg=self.style.colors.primary,
            fg="#ff4d4d",
        ).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(
            header,
            text="Load Video",
            command=self._select_input,
            font=self.custom_font,
            bg=self.style.colors.secondary,
            fg="#ffffff",
            activebackground="#ff4d4d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            width=15,
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            header,
            text="Save As",
            command=self._select_output,
            font=self.custom_font,
            bg=self.style.colors.secondary,
            fg="#ffffff",
            activebackground="#ff4d4d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            width=15,
        ).pack(side=tk.LEFT, padx=10)

        # Main content area
        main_frame = tk.Frame(self.root, bg=self.style.colors.bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sidebar (Controls)
        sidebar = tk.Frame(main_frame, bg=self.style.colors.dark, width=500, relief=tk.RAISED, bd=2)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(
            sidebar,
            text="Control Panel",
            font=self.header_font,
            bg=self.style.colors.dark,
            fg="#ff4d4d",
        ).pack(pady=20)

        control_frame = tk.Frame(sidebar, bg=self.style.colors.dark)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Control sliders with tooltips
        controls = [
            ("Min Blob Area", self.min_area, 10, 200, "Set minimum blob area for detection"),
            ("Motion Threshold", self.motion_threshold, 0.1, 5.0, "Adjust sensitivity to motion"),
            ("Blob Size Scale", self.blob_size_scale, 0.1, 1.0, "Scale the size of detected blobs"),
            ("Connection Distance", self.max_connection_distance, 50, 300, "Max distance for blob connections"),
            ("Trail Opacity", self.trail_opacity, 0.1, 1.0, "Opacity of blob motion trails"),
            ("Bitrate (kbps)", self.bitrate, 5000, 200000, "Output video quality"),
        ]

        for text, var, from_, to_, tooltip in controls:
            frame = tk.Frame(control_frame, bg=self.style.colors.dark)
            frame.pack(fill=tk.X, pady=10)
            tk.Label(
                frame,
                text=text,
                font=self.custom_font,
                bg=self.style.colors.dark,
                fg="#e0e0e0",
            ).pack(side=tk.LEFT)
            scale = ttk.Scale(
                frame,
                from_=from_,
                to=to_,
                variable=var,
                style="Horizontal.TScale",
                length=350,
            )
            scale.pack(side=tk.LEFT, padx=10)
            # Add tooltip
            scale.bind("<Enter>", lambda e, t=tooltip: self._show_tooltip(e, t))
            scale.bind("<Leave>", self._hide_tooltip)
            if text == "Min Blob Area":
                scale.configure(command=lambda x: self._update_blob_detector())

        # Resolution dropdown
        tk.Label(
            control_frame,
            text="Output Resolution",
            font=self.custom_font,
            bg=self.style.colors.dark,
            fg="#e0e0e0",
        ).pack(pady=10)
        ttk.OptionMenu(
            control_frame,
            self.output_resolution,
            "Match Input",
            "Match Input",
            "1920x1080",
            "3840x2160",
            style="TMenubutton",
        ).pack(pady=5)

        # Process button
        self.process_button = tk.Button(
            control_frame,
            text="Unleash Blobs!",
            command=self._start_processing,
            font=self.header_font,
            bg="#ff4d4d",
            fg="#ffffff",
            activebackground="#ff6666",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            state=tk.DISABLED,
        )
        self.process_button.pack(pady=30, fill=tk.X)

        # Right panel (Preview and Log)
        right_panel = tk.Frame(main_frame, bg=self.style.colors.bg)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Preview area
        preview_frame = tk.Frame(right_panel, bg=self.style.colors.dark, relief=tk.FLAT, bd=2)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        self.preview_label = tk.Label(
            preview_frame,
            text="No Preview Available",
            font=self.custom_font,
            bg=self.style.colors.dark,
            fg="#999999",
        )
        self.preview_label.pack(expand=True)

        # Log area
        log_frame = tk.Frame(right_panel, bg=self.style.colors.dark, height=200)
        log_frame.pack(fill=tk.X, pady=10)
        tk.Label(
            log_frame,
            text="Activity Log",
            font=self.custom_font,
            bg=self.style.colors.dark,
            fg="#ff4d4d",
        ).pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Montserrat", 12),
            bg=self.style.colors.inputbg,
            fg="#ffffff",
            insertbackground="#ffffff",
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._log("Application initialized.")

        # Timeline and progress
        timeline = tk.Frame(self.root, bg=self.style.colors.primary, height=60)
        timeline.pack(side=tk.BOTTOM, fill=tk.X)
        self.progress = tk.DoubleVar()
        self.progress_scale = ttk.Scale(
            timeline,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress,
            length=1000,
            style="Horizontal.TScale",
        )
        self.progress_scale.pack(side=tk.LEFT, padx=20, pady=10)
        self.progress_label = tk.Label(
            timeline,
            text="Progress: 0%",
            font=self.custom_font,
            bg=self.style.colors.primary,
            fg="#e0e0e0",
        )
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Status bar
        status_bar = tk.Label(
            self.root,
            text="Ready to dominate the blob universe!",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=self.custom_font,
            bg=self.style.colors.dark,
            fg="#e0e0e0",
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Custom styles
        self.style.configure("Horizontal.TScale", background=self.style.colors.dark, troughcolor="#555555", slidercolor="#ff4d4d")
        self.style.configure("TMenubutton", font=("Montserrat", 12), background=self.style.colors.secondary)

        # Splash screen
        self._show_splash()

    def _show_splash(self):
        splash = tk.Toplevel(self.root)
        splash.geometry("1000x500")
        splash.overrideredirect(True)  # Remove window borders
        splash.configure(bg="#0a0a0a")
        canvas = tk.Canvas(splash, bg="#0a0a0a", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Gradient background effect
        for i in range(500):
            color = f"#{int(10 + (i/500)*20):02x}{int(10 + (i/500)*20):02x}{int(10 + (i/500)*50):02x}"
            canvas.create_line(0, i, 1000, i, fill=color)

        tk.Label(
            canvas,
            text="Delusional Blob Extreme Pro",
            font=("Montserrat", 60, "bold"),
            bg="#0a0a0a",
            fg="#ff4d4d",
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        splash.after(2000, splash.destroy)

    def _show_tooltip(self, event, text):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.overrideredirect(True)
        self.tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tk.Label(
            self.tooltip,
            text=text,
            bg=self.style.colors.info,
            fg="#ffffff",
            font=("Montserrat", 10),
            padx=5,
            pady=2,
        ).pack()

    def _hide_tooltip(self, event):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()

    def _log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def _update_preview(self, frame):
        preview_width, preview_height = 1280, 720
        h, w = frame.shape[:2]
        aspect_ratio = w / h
        if aspect_ratio > preview_width / preview_height:
            new_width = preview_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = preview_height
            new_width = int(new_height * aspect_ratio)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        self.preview_photo = ImageTk.PhotoImage(image)
        self.preview_label.config(image=self.preview_photo, text="")
        self.root.update()

    def _select_input(self):
        self.input_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        if self.input_path:
            self._log(f"Loaded: {os.path.basename(self.input_path)}")
            self._check_ready()

    def _select_output(self):
        self.output_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI files", "*.avi")])
        if self.output_path:
            self._log(f"Output set: {os.path.basename(self.output_path)}")
            self._check_ready()

    def _check_ready(self):
        self.process_button.config(state=tk.NORMAL if self.input_path and self.output_path else tk.DISABLED)

    def _start_processing(self):
        self.running = True
        self.process_button.config(state=tk.DISABLED, text="Blobbing...")
        self._log("Initiating blob domination...")
        threading.Thread(target=self._process_video, daemon=True).start()

    def _track_motion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        if self.prev_gray is None:
            self.prev_gray = gray
            return []

        flow = cv2.calcOpticalFlowFarneback(self.prev_gray, gray, None, 0.5, 3, 10, 3, 5, 1.1, 0)
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        motion_mask = cv2.threshold(magnitude, self.motion_threshold.get(), 255, cv2.THRESH_BINARY)[1].astype(np.uint8)
        motion_mask = cv2.dilate(motion_mask, np.ones((5, 5), np.uint8), iterations=1)

        masked_gray = cv2.bitwise_and(gray, gray, mask=motion_mask)
        masked_gray = cv2.GaussianBlur(masked_gray, (5, 5), 0)
        keypoints = self.blob_detector.detect(masked_gray)
        blob_objects = []
        for kp in keypoints:
            cx, cy = int(kp.pt[0]), int(kp.pt[1])
            size = kp.size * self.blob_size_scale.get()
            area = np.pi * (size / 2) ** 2
            blob_objects.append((cx, cy, size, area, None))

        self.prev_gray = gray
        return blob_objects

    def _assign_objects(self, tracked_objects):
        current_objects = {}
        for cx, cy, size, area, obj_id in tracked_objects:
            key = obj_id if obj_id is not None else (cx, cy)
            current_objects[key] = (cx, cy, size, area)

        updated_objects = {}
        for key, (cx, cy, size, area) in current_objects.items():
            matched = False
            if key in self.objects:
                prev_cx, prev_cy = self.objects[key]["center"]
                dist = ((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2) ** 0.5
                new_cx = int(cx * 0.5 + prev_cx * 0.5)
                new_cy = int(cy * 0.5 + prev_cy * 0.5)
                new_size = size * 0.6 + self.objects[key]["size"] * 0.4
                updated_objects[key] = {
                    "center": (new_cx, new_cy),
                    "size": new_size,
                    "area": area,
                    "age": min(self.objects[key]["age"] + 1, 50),
                    "activity": min(self.objects[key]["activity"] + dist * 0.3, 200),
                    "is_yolo": False,
                }
                matched = True
            elif isinstance(key, tuple):
                for oid, data in self.objects.items():
                    prev_cx, prev_cy = data["center"]
                    dist = ((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2) ** 0.5
                    if dist < 50 + size * 0.2:
                        new_cx = int(cx * 0.5 + prev_cx * 0.5)
                        new_cy = int(cy * 0.5 + prev_cy * 0.5)
                        new_size = size * 0.6 + data["size"] * 0.4
                        updated_objects[oid] = {
                            "center": (new_cx, new_cy),
                            "size": new_size,
                            "area": area,
                            "age": min(data["age"] + 1, 50),
                            "activity": min(data["activity"] + dist * 0.3, 200),
                            "is_yolo": False,
                        }
                        matched = True
                        break
            if not matched:
                self.object_id += 1
                updated_objects[self.object_id] = {
                    "center": (cx, cy),
                    "size": size,
                    "area": area,
                    "age": 0,
                    "activity": 0,
                    "is_yolo": False,
                }

        self.objects = {
            oid: data for oid, data in updated_objects.items()
            if data["age"] < 50 or data["activity"] > 5
        }

    def _draw_elements(self, frame):
        self.trail_buffer.append(frame.copy())
        if len(self.trail_buffer) > 5:
            self.trail_buffer.pop(0)
        trail_frame = np.zeros_like(frame)
        for i, past_frame in enumerate(self.trail_buffer):
            alpha = self.trail_opacity.get() * (i + 1) / len(self.trail_buffer)
            trail_frame = cv2.addWeighted(trail_frame, 1 - alpha, past_frame, alpha, 0)

        centers = [(data["center"], oid) for oid, data in self.objects.items()]
        for i, (center1, id1) in enumerate(centers):
            for j, (center2, id2) in enumerate(centers[i + 1:], start=i + 1):
                dist = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
                if dist < self.max_connection_distance.get():
                    cv2.line(frame, center1, center2, self.GRAY, 1)
                    cv2.line(
                        frame,
                        (center1[0] + 1, center1[1] + 1),
                        (center2[0] + 1, center2[1] + 1),
                        self.WHITE,
                        1,
                    )
        for obj_id, data in self.objects.items():
            cx, cy = data["center"]
            size = data["size"]
            radius = int(size / 2)
            cv2.circle(
                frame,
                (cx + self.shadow_offset, cy + self.shadow_offset),
                radius,
                self.GRAY,
                2,
            )
            cv2.circle(frame, (cx, cy), radius, self.WHITE, 2)
            text = f"#{obj_id}"
            text_size, _ = cv2.getTextSize(text, self.font, self.font_scale, 1)
            tx, ty = int(cx + size / 2 + 5), int(cy)
            cv2.rectangle(
                frame,
                (tx - 3, ty - text_size[1] - 3),
                (tx + text_size[0] + 3, ty + 3),
                self.BLACK,
                -1,
            )
            cv2.putText(
                frame,
                text,
                (tx + 1, ty + 1),
                self.font,
                self.font_scale,
                self.GRAY,
                1,
            )
            cv2.putText(
                frame,
                text,
                (tx, ty),
                self.font,
                self.font_scale,
                self.WHITE,
                1,
            )

        frame = cv2.addWeighted(frame, 0.7, trail_frame, 0.3, 0)
        status = f"Blobs: {len(self.objects)} | Frame: {self.frame_count}/{self.total_frames}"
        text_size, _ = cv2.getTextSize(status, self.font, self.font_scale, 1)
        cv2.rectangle(
            frame,
            (5, 5),
            (15 + text_size[0], 15 + text_size[1]),
            self.BLACK,
            -1,
        )
        cv2.putText(
            frame,
            status,
            (10, 10 + text_size[1]),
            self.font,
            self.font_scale,
            self.WHITE,
            1,
        )
        return frame

    def _process_frame(self, frame):
        self.frame_count += 1
        tracked_objects = self._track_motion(frame)
        self._assign_objects(tracked_objects)
        return self._draw_elements(frame)

    def _process_video(self):
        try:
            self.video = cv2.VideoCapture(self.input_path)
            if not self.video.isOpened():
                raise Exception("Failed to open video")
            self.frame_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

            if self.output_resolution.get() == "Match Input":
                w, h = self.frame_width, self.frame_height
            else:
                w, h = map(int, self.output_resolution.get().split("x"))
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self.writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, (w, h))
            if not self.writer.isOpened():
                raise Exception("Failed to initialize video writer")

            while self.running:
                ret, frame = self.video.read()
                if not ret:
                    break
                processed_frame = self._process_frame(frame)
                if (w, h) != (self.frame_width, self.frame_height):
                    processed_frame = cv2.resize(processed_frame, (w, h), interpolation=cv2.INTER_LANCZOS4)
                self.writer.write(processed_frame)
                if self.frame_count % 10 == 0:
                    self._update_preview(processed_frame)
                    progress = (self.frame_count / self.total_frames) * 100
                    self.progress.set(progress)
                    self.progress_label.config(text=f"Progress: {progress:.1f}% | Frame: {self.frame_count}/{self.total_frames}")
                    self.root.update()

            self._log("Blob domination complete!")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Video saved to: {self.output_path}"))
        except Exception as e:
            self._log(f"Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self._cleanup()
            self.root.after(0, lambda: self.process_button.config(state=tk.NORMAL, text="Unleash Blobs!"))
            self.running = False

    def _cleanup(self):
        if self.video and self.video.isOpened():
            self.video.release()
        if self.writer:
            self.writer.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = DelusionalMotionVideoBlobEditorApp(root)
    root.mainloop()