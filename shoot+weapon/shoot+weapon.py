import streamlit as st
import cv2
import tempfile
from pathlib import Path
from ultralytics import YOLO


WEAPON_MODEL_PATH = "/home/support/Desktop/shoot+weapon/train4/weights/best.pt"
POSE_MODEL_PATH = "/home/support/Desktop/shoot+weapon/runs/pose/train/weights/best.pt"


weapon_model = YOLO(WEAPON_MODEL_PATH)
pose_model = YOLO(POSE_MODEL_PATH)


POSE_CLASS_NAMES = {
    0: "shooter_pose",
    1: "non_shooter_pose",
}

st.set_page_config(page_title="Weapon + Shooter Pose Demo", layout="wide")
st.title("Weapon + Shooter Pose Demo")

weapon_conf = st.slider("Weapon confidence threshold", 0.05, 0.95, 0.25, 0.05)
pose_conf = st.slider("Pose confidence threshold", 0.05, 0.95, 0.25, 0.05)

uploaded = st.file_uploader(
    "Upload image or video",
    type=["jpg", "jpeg", "png", "mp4", "avi", "mov"]
)


def draw_pose_boxes_only(frame, result, shooter_class_id=0):
    """
    Рисует только bbox для shooter_pose, чтобы не захламлять картинку.
    """
    out = frame.copy()

    if result.boxes is None or len(result.boxes) == 0:
        return out, []

    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()
    confs = result.boxes.conf.cpu().numpy()

    detections = []

    for box, cls_id, score in zip(boxes, classes, confs):
        cls_id = int(cls_id)

        if cls_id != shooter_class_id:
            continue

        x1, y1, x2, y2 = map(int, box)
        label = f"shooter_pose {score:.2f}"

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(
            out,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        detections.append(
            {
                "class_id": cls_id,
                "class_name": POSE_CLASS_NAMES.get(cls_id, str(cls_id)),
                "conf": float(score),
                "bbox": [x1, y1, x2, y2],
            }
        )

    return out, detections


def draw_weapon_boxes(frame, result):
    """
    Рисует bbox оружия.
    """
    out = frame.copy()

    detections = []
    if result.boxes is None or len(result.boxes) == 0:
        return out, detections

    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()
    confs = result.boxes.conf.cpu().numpy()

    names = result.names if hasattr(result, "names") else {}

    for box, cls_id, score in zip(boxes, classes, confs):
        cls_id = int(cls_id)
        class_name = names.get(cls_id, f"class_{cls_id}")

        x1, y1, x2, y2 = map(int, box)
        label = f"{class_name} {score:.2f}"

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(
            out,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

        detections.append(
            {
                "class_id": cls_id,
                "class_name": class_name,
                "conf": float(score),
                "bbox": [x1, y1, x2, y2],
            }
        )

    return out, detections


def combine_visualizations(original_frame, weapon_result, pose_result):
    """
    Накладывает результаты двух моделей на один кадр.
    """
    frame1, weapon_dets = draw_weapon_boxes(original_frame, weapon_result)
    frame2, pose_dets = draw_pose_boxes_only(frame1, pose_result, shooter_class_id=0)
    return frame2, weapon_dets, pose_dets


if uploaded:
    suffix = Path(uploaded.name).suffix
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tfile.write(uploaded.read())
    tfile.close()

    if uploaded.type.startswith("image"):
        image = cv2.imread(tfile.name)

        weapon_results = weapon_model.predict(source=image, conf=weapon_conf, verbose=False)
        pose_results = pose_model.predict(source=image, conf=pose_conf, verbose=False)

        weapon_result = weapon_results[0]
        pose_result = pose_results[0]

        combined_img, weapon_dets, pose_dets = combine_visualizations(
            image, weapon_result, pose_result
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.image(combined_img, channels="BGR", caption="Detection result")

        with col2:
            st.subheader("Results")

            if len(weapon_dets) > 0:
                st.error(f"Weapon detected: {len(weapon_dets)}")
            else:
                st.success("No weapon detected")

            if len(pose_dets) > 0:
                st.warning(f"Shooter pose detected: {len(pose_dets)}")
            else:
                st.info("No shooter pose detected")

            if len(weapon_dets) > 0 and len(pose_dets) > 0:
                st.error("ALERT: weapon + shooter pose")
            elif len(weapon_dets) > 0:
                st.warning("Weapon only")
            elif len(pose_dets) > 0:
                st.warning("Shooter pose only")
            else:
                st.success("No threat pattern found")

            with st.expander("Weapon detections"):
                if weapon_dets:
                    st.json(weapon_dets)
                else:
                    st.write("Empty")

            with st.expander("Pose detections"):
                if pose_dets:
                    st.json(pose_dets)
                else:
                    st.write("Empty")

    else:
        st.write("Processing video...")

        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()
        status_box = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            weapon_results = weapon_model.predict(source=frame, conf=weapon_conf, verbose=False)
            pose_results = pose_model.predict(source=frame, conf=pose_conf, verbose=False)

            weapon_result = weapon_results[0]
            pose_result = pose_results[0]

            combined_frame, weapon_dets, pose_dets = combine_visualizations(
                frame, weapon_result, pose_result
            )

            stframe.image(combined_frame, channels="BGR")

            if len(weapon_dets) > 0 and len(pose_dets) > 0:
                status_box.error("ALERT: weapon + shooter pose")
            elif len(weapon_dets) > 0:
                status_box.warning("Weapon detected")
            elif len(pose_dets) > 0:
                status_box.warning("Shooter pose detected")
            else:
                status_box.success("No threat pattern found")

        cap.release()