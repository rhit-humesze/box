import os

msg = "kNNm1vmZei9NlljvAAAB_black.png"

filepath = f"images"
path = os.path.join(os.curdir, filepath)
for drawing in os.listdir(path):
    if(drawing != msg):
        drawingPath = os.path.join(filepath, drawing)
        os.remove(drawingPath)