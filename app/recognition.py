import cv2
import numpy as np
import pickle
from datetime import datetime, timedelta
import time
from deepface import DeepFace

# Flask imports must be handled carefully, but we include the required models and db here
from app.models import Student, Attendance # Import Student and Attendance models
from app import db # Assuming db is accessible
from sqlalchemy import func

# --- CONFIGURATION ---
DETECTOR_BACKEND = "opencv" 
MODEL_NAME = "VGG-Face"
# Threshold for Cosine Distance (usually 0.25 to 0.40 is common)
THRESHOLD = 0.40 

# --- DISTANCE METRIC FUNCTION ---
def find_cosine_distance(source_representation, test_representation):
    """
    Calculates Cosine Distance (1 - Cosine Similarity) manually and efficiently.
    """
    source_representation = source_representation.flatten()
    test_representation = test_representation.flatten()
    
    # Cosine Similarity Calculation: (A . B) / (||A|| * ||B||)
    a = np.dot(source_representation, test_representation)
    b = np.sqrt(np.sum(source_representation * source_representation))
    c = np.sqrt(np.sum(test_representation * test_representation))
    
    if b == 0 or c == 0:
        return 1.0 # Max distance for zero vectors
        
    similarity = a / (b * c)
    return 1 - similarity


# --- UTILITIES ---

def load_and_verify_all_embeddings(StudentModel):
    """Retrieves all registered students' data and embeddings."""
    students = StudentModel.query.filter(StudentModel.face_embedding.isnot(None)).all()
    
    known_embeddings = []
    known_metadata = []
    
    for student in students:
        try:
            # Deserialize the BLOB back into a NumPy array
            embedding_array = pickle.loads(student.face_embedding)
            known_embeddings.append(embedding_array)
            known_metadata.append({
                'id': student.id, 
                'name': student.name, 
                'roll_no': student.roll_no,
            })
        except Exception as e:
            print(f"Error loading embedding for student {student.id}: {e}")
            continue
            
    return np.array(known_embeddings), known_metadata

def calculate_attendance_status(AttendanceModel):
    """Calculates 'Present' or 'Late' status based on policy time."""
    current_time = datetime.now()
    late_hour, late_minute, _ = AttendanceModel.get_late_policy_time()
    
    # Create a datetime object for the cut-off time TODAY
    late_cut_off = current_time.replace(
        hour=late_hour, 
        minute=late_minute, 
        second=0, 
        microsecond=0
    )
    
    if current_time > late_cut_off:
        return 'Late', (0, 165, 255) # Orange
    else:
        return 'Present', (0, 255, 0) # Green

# --- MAIN ATTENDANCE LOOP (UPDATED) ---

def mark_attendance_loop(db, AttendanceModel, StudentModel, DeepFace):
    """
    Runs the live camera feed, performs recognition, and commits attendance.
    """
    known_embeddings_arr, known_metadata = load_and_verify_all_embeddings(StudentModel)
    
    if not known_embeddings_arr.size:
        print("[ERROR] No registered faces found. Cannot start attendance.")
        return 
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Failed to open camera.")
        return
        
    recognized_session = {} # {student_id: time} to prevent rapid commits
    PROCESS_FRAME_RATE = 5 
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame_count += 1
        
        if frame_count % PROCESS_FRAME_RATE != 0:
            cv2.imshow("Attendance Marker", frame)
            if cv2.waitKey(1) == ord('q'): break
            continue
            
        display_frame = frame.copy()
        identified_id = None
        identified_name = "Unknown"
        
        try:
            faces = DeepFace.extract_faces(img_path=frame, detector_backend=DETECTOR_BACKEND, enforce_detection=False)
            
            for face_data in faces:
                x, y, w, h = [face_data['facial_area'][k] for k in ['x', 'y', 'w', 'h']]
                face_crop = frame[y:y+h, x:x+w]
                
                live_embedding_results = DeepFace.represent(img_path=face_crop, model_name=MODEL_NAME, detector_backend='skip', enforce_detection=False)
                
                if not live_embedding_results: continue
                
                live_embedding_arr = np.array(live_embedding_results[0]['embedding'], dtype=np.float32)
                
                # --- 1. OPTIMIZED COSINE DISTANCE COMPARISON ---
                min_distance = 1.0
                best_match_index = -1
                
                for i, stored_embedding in enumerate(known_embeddings_arr):
                    distance = find_cosine_distance(stored_embedding, live_embedding_arr)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match_index = i
                
                # --- 2. LOGIC HANDLING ---
                if min_distance < THRESHOLD:
                    match_data = known_metadata[best_match_index]
                    identified_id = match_data['id']
                    identified_name = match_data['name']
                    
                    today = datetime.now().date()
                    current_time = datetime.now()
                    
                    # Check for existing record for today
                    existing_entry = db.session.query(AttendanceModel).filter(
                        AttendanceModel.student_id == identified_id,
                        func.date(AttendanceModel.time_in) == today 
                    ).first()

                    if not existing_entry:
                        # SCENARIO A: MARKING IN (Create New Record)
                        attendance_status, color = calculate_attendance_status(AttendanceModel)
                        
                        new_entry = AttendanceModel(
                            student_id=identified_id, 
                            time_in=current_time, 
                            status=attendance_status
                        )
                        db.session.add(new_entry)
                        db.session.commit()
                        
                        recognized_session[identified_id] = current_time.time()
                        label_text = f"{attendance_status} IN: {identified_name}"
                        print(f"[ENTRY] {identified_name} marked {attendance_status}")

                    elif existing_entry and existing_entry.time_out is None:
                        # SCENARIO B: MARKING OUT (Update Existing Record)
                        existing_entry.time_out = current_time 
                        db.session.commit()
                        
                        label_text = f"EXIT: {identified_name}"
                        color = (255, 100, 0) # Orange/Blue for exit
                        print(f"[EXIT] {identified_name} marked out")
                        
                    else:
                        # SCENARIO C: ALREADY MARKED IN AND OUT
                        label_text = f"{identified_name} (Completed)"
                        color = (150, 150, 150) # Gray/Neutral
                else:
                    label_text = f"Unknown (Dist: {min_distance:.2f})"
                    color = (0, 0, 255) # Red

                # Draw Visuals
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(display_frame, label_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
        except Exception as e:
            # print(f"Processing error: {e}") 
            pass

        cv2.imshow("Attendance Marker", display_frame)

        if cv2.waitKey(1) == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()
    return {"status": "session_closed"}