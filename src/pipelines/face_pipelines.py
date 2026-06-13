import numpy as np
import streamlit as st

from src.database.db import get_all_students

FACE_MODEL_NAME = "VGG-Face"
FACE_DETECTOR_BACKEND = "opencv"
FACE_DISTANCE_THRESHOLD = 0.8
DLIB_DISTANCE_THRESHOLD = 0.6


def _coerce_embedding(embedding):
    try:
        arr = np.asarray(embedding, dtype=float)
    except (TypeError, ValueError):
        return None

    if arr.ndim != 1 or arr.size == 0:
        return None

    return arr


def _student_rows(records):
    rows = []
    for record in records or []:
        student = record.get("students") if isinstance(record, dict) else None
        if student is None and isinstance(record, dict):
            student = record
        if isinstance(student, dict):
            rows.append(student)
    return rows


def _build_model_data(student_records):
    from sklearn.svm import SVC

    X = []
    y = []

    for student in _student_rows(student_records):
        embedding = _coerce_embedding(student.get("face_embedding"))
        student_id = student.get("student_id")
        if embedding is not None and student_id is not None:
            X.append(embedding)
            y.append(student_id)

    if len(X) == 0:
        return 0

    clf = SVC(kernel="linear", probability=True, class_weight="balanced")

    try:
        if len({embedding.size for embedding in X}) == 1:
            clf.fit(X, y)
        else:
            clf = None
    except ValueError:
        clf = None

    return {"clf": clf, "X": X, "y": y}


@st.cache_resource
def load_face_model():
    from deepface import DeepFace

    return DeepFace.build_model(FACE_MODEL_NAME)


@st.cache_resource
def load_dlib_models():
    import dlib
    import face_recognition_models

    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector, sp, facerec


def get_dlib_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
        encodings.append(np.array(face_descriptor))
    return encodings


def get_face_embeddings(image_np):
    try:
        from deepface import DeepFace
    except ModuleNotFoundError:
        try:
            return get_dlib_face_embeddings(image_np)
        except ModuleNotFoundError:
            st.error(
                "Face recognition dependencies are not installed. "
                "Install requirements.txt, then restart Streamlit."
            )
            return []

    load_face_model()

    try:
        faces = DeepFace.represent(
            img_path=image_np,
            model_name=FACE_MODEL_NAME,
            detector_backend=FACE_DETECTOR_BACKEND,
            enforce_detection=False,
        )
    except Exception as exc:
        st.error(f"Error processing face image: {exc}")
        return []

    encodings = []
    for face in faces:
        embedding = face.get("embedding")
        facial_area = face.get("facial_area") or {}
        area = facial_area.get("w", 0) * facial_area.get("h", 0)
        if embedding and area > 0:
            encodings.append(np.array(embedding))

    if not encodings and faces:
        embedding = faces[0].get("embedding")
        if embedding:
            encodings.append(np.array(embedding))

    return encodings


@st.cache_data(ttl=60, show_spinner=False)
def get_trained_model():
    student_db = get_all_students()

    if not student_db:
        return None

    return _build_model_data(student_db)


def train_classifier():
    get_trained_model.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np, candidate_students=None):
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    model_data = (
        _build_model_data(candidate_students)
        if candidate_students is not None
        else get_trained_model()
    )

    if not model_data:
        return {}, [], len(encodings)
        
    X_all = model_data['X']
    y_all = model_data['y']
    target_dim = encodings[0].size if encodings else None
    compatible = [
        (embedding, student_id)
        for embedding, student_id in zip(X_all, y_all)
        if target_dim is not None and embedding.size == target_dim
    ]

    if not compatible:
        return {}, [], len(encodings)

    X = np.array([embedding for embedding, _ in compatible])
    y = [student_id for _, student_id in compatible]
    distance_threshold = (
        FACE_DISTANCE_THRESHOLD if X.shape[1] != 128 else DLIB_DISTANCE_THRESHOLD
    )

    all_students = sorted(list(set(y)))

    for encoding in encodings:
        distances = np.linalg.norm(X - encoding, axis=1)
        min_dist_idx = np.argmin(distances)
        min_dist = distances[min_dist_idx]
        predicted_id = int(y[min_dist_idx]) if min_dist <= distance_threshold else None

        if predicted_id is not None:
            try:
                student_index = y.index(predicted_id)
                student_embedding = X[student_index]
                best_match_score = np.linalg.norm(student_embedding - encoding)
                resemblance_threshold = distance_threshold

                if best_match_score <= resemblance_threshold:
                    detected_student[predicted_id] = True
            except (ValueError, IndexError):
                pass

    return detected_student, all_students, len(encodings)


predict_attendence = predict_attendance
