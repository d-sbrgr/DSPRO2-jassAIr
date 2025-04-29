from ultralytics import solutions

inf = solutions.Inference(
    model="artifacts/yolov11-finetuned-model-non-overlapping:v0/best.pt"
)
inf.inference()

# Needs to be run using command 'streamlit run path/to/file.py'