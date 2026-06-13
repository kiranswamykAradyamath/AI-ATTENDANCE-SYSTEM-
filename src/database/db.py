import base64
import hashlib
import hmac
import os

import httpx

from src.database.config import supabase


class DatabaseConnectionError(RuntimeError):
    pass


PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260000


def _get_bcrypt():
    try:
        import bcrypt
    except ModuleNotFoundError:
        return None
    return bcrypt


def _execute_query(query):
    try:
        return query.execute()
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
        raise DatabaseConnectionError(
            "Could not connect to Supabase. Check your internet connection, DNS, "
            "and SUPABASE_URL in .streamlit/secrets.toml."
        ) from exc


def hash_pass(password):
    bcrypt = _get_bcrypt()
    if bcrypt:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "$".join(
        [
            PBKDF2_PREFIX,
            str(PBKDF2_ITERATIONS),
            base64.b64encode(salt).decode(),
            base64.b64encode(password_hash).decode(),
        ]
    )

def check_pass(password, hash_password):
    if not hash_password:
        return False

    if hash_password.startswith(PBKDF2_PREFIX + "$"):
        try:
            _, iterations, salt, stored_hash = hash_password.split("$", 3)
            calculated_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(),
                base64.b64decode(salt),
                int(iterations),
            )
            return hmac.compare_digest(
                base64.b64encode(calculated_hash).decode(),
                stored_hash,
            )
        except (ValueError, TypeError):
            return False

    bcrypt = _get_bcrypt()
    if not bcrypt:
        return False

    return bcrypt.checkpw(password.encode(), hash_password.encode())


def check_teacher_exists(username):
    # check for unique username, returns false when username is already taken 
    response = _execute_query(
        supabase.table("teachers").select("username").eq("username", username)
    )
    return len(response.data) > 0


def find_subject_by_code(subject_code):
    code = (subject_code or "").strip().upper()
    if not code:
        return None

    response = _execute_query(
        supabase.table("subjects")
        .select("subject_id, name, subject_code, section")
        .eq("subject_code", code)
    )
    return response.data[0] if response.data else None


def is_student_enrolled(student_id, subject_id):
    response = _execute_query(
        supabase.table("subject_students")
        .select("*")
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
    )
    return bool(response.data)


def create_teacher(username, password, name ):

    data = { "username": username, "password": hash_pass(password), "name": name }
    response = _execute_query(supabase.table("teachers").insert(data))
    return response.data

def teacher_login(username,password):
    response = _execute_query(
        supabase.table("teachers").select("*").eq("username",username)
    )

    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher

        return None
    

def get_all_students():
    response = _execute_query(supabase.table("students").select("*"))
    return response.data

def create_student(new_name, face_embedding, voice_embedding):
    data = {
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }
    response = _execute_query(supabase.table("students").insert(data))
    return response.data



def create_subject(subject_code, name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }
    response = _execute_query(supabase.table("subjects").insert(data))
    return response.data

def get_teacher_subjects(teacher_id):
    response = _execute_query(
        supabase.table("subjects")
        .select("*, subject_students(count), attendance_logs(timestamp)")
        .eq("teacher_id", teacher_id)
    )
    subject = response.data

    for sub in subject:
        sub['total_students'] = sub.get('subject_students', [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs',[])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        
        sub['total_sessions'] = unique_sessions
        sub['total_classes'] = unique_sessions

        

        sub.pop('subject_students', None)
        sub.pop('attendance_logs', None)


    return response.data

def enroll_student_to_subject(student_id, subject_id):
    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }
    response = _execute_query(supabase.table("subject_students").insert(data))
    return response.data

def unenroll_student_to_subject(student_id, subject_id):
   
    response = _execute_query(
        supabase.table("subject_students")
        .delete()
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
    )
    return response.data

def get_student_subjects(student_id):
    response = _execute_query(
        supabase.table("subject_students")
        .select('*, subjects(*)')
        .eq("student_id", student_id)
    )
    return response.data

def get_subject_students(subject_id):
    response = _execute_query(
        supabase.table("subject_students")
        .select("*, students(*)")
        .eq("subject_id", subject_id)
    )
    return response.data


def get_enrolled_students_for_subject(subject_id):
    return get_subject_students(subject_id)

def get_student_attendance(student_id):
    response = _execute_query(
        supabase.table("attendance_logs")
        .select("*, subjects(*)")
        .eq("student_id", student_id)
    )
    return response.data


def create_attendance(logs):
    response = _execute_query(supabase.table('attendance_logs').insert(logs))
    return response

def get_attendance_for_teacher(teacher_id):
    response = _execute_query(
        supabase.table('attendance_logs')
        .select("*, subjects!inner(*)")
        .eq('subjects.teacher_id', teacher_id)
    )
    return response.data
