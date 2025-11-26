import cv2
import pickle
import numpy as np
from deepface import DeepFace
from app.models import Student


# --- CONFIGURATION ---
DETECTOR_BACKEND = "opencv" 
MODEL_NAME = "VGG-Face"     
THRESHOLD = 0.7           



def capture_embedding():
        
    print("[INFO] Registering Student Face. Press 'c' to capture and 'q' to quit.")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret: 
            break

        cv2.putText(frame, "Press 'c' to Capture face", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Face Registration", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        
        elif key == ord('c'):
            try:
                # Generate Embedding
                results = DeepFace.represent(
                    img_path=frame, 
                    model_name=MODEL_NAME, 
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=True
                )
                
                if results:
                    
                    embedding_list = results[0]["embedding"]
                    embedding_array = np.array(embedding_list, dtype=np.float32)
                    
                    embedding_blob = pickle.dumps(embedding_array)
                    
                   
                    
                    break
                
            except ValueError:
                print("[ERROR] No face detected. Try again!")
            except Exception as e:
                print(f"[ERROR] {e}")

    cap.release()
    cv2.destroyAllWindows()      
    
    return embedding_blob



def check_face_duplicate(new_embedding_blob, roll_no):
    """
    Compares the new embedding against ALL students in the DB.
    Returns the Name of the existing student if a match is found, else None.
    """
    new_embedding = pickle.loads(new_embedding_blob)
    
    existing_students = Student.query.filter(Student.face_embedding.isnot(None)).all()
    
    THRESHOLD = 0.7

    for student in existing_students:
        if student.roll_no == roll_no:
            continue
            
        stored_embedding_blob = student.face_embedding
        if stored_embedding_blob is None:
            continue
        
        stored_embedding = pickle.loads(stored_embedding_blob)
        distance = np.linalg.norm(new_embedding - stored_embedding)
        
        if distance < THRESHOLD:
            return {student.name}
                   
    return None 