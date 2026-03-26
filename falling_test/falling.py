import streamlit as st
import cv2
import tempfile
from pathlib import Path
from ultralytics import YOLO

# Модель для распознавания лежачих поз
model = YOLO("/home/support/Desktop/Meduza_1/falling_test/runs/detect/train2/weights/best.pt")

st.title("Lying Pose Detection Demo")

conf = st.slider("Confidence threshold", 0.05, 0.9, 0.25, 0.05)

uploaded = st.file_uploader(
    "Upload image or video",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
)

if uploaded:

    suffix = Path(uploaded.name).suffix
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tfile.write(uploaded.read())
    tfile.close()

    if uploaded.type.startswith("image"):

        results = model(tfile.name, conf=conf)
        res_img = results[0].plot()

        st.image(res_img, caption="Detection result")

        if len(results[0].boxes) > 0:
            st.error("LYING POSE DETECTED")
        else:
            st.success("No lying pose detected")

    else:
        st.write("Processing video...")

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, conf=conf)
            frame = results[0].plot()

            stframe.image(frame, channels="BGR")

        cap.release()