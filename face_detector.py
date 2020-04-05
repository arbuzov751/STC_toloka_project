import cv2
from tqdm import tqdm


def videoStreamer(path, skip=None):
    # Загружаем видео.
    stream = cv2.VideoCapture(path)
    frames = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
    FPS = stream.get(cv2.CAP_PROP_FPS)
    print(f"frames = {frames}, FPS = {FPS}")
    if skip == None:
        skip = int(FPS)

    count = 0
    while True:
        # Пропускаем несколько кадров, и смотрим один из них.
        for i in tqdm(range(skip)/2):
            stream.grab()
        (grabbed, frame) = stream.read()

        if not grabbed:
            stream.release()
            return

        cv2.imwrite(r"frames\frame%d.jpg" % count, frame)
        count = count + 1


path = r'C:\STC_toloka_project\download\toloka1.webm'
videoStreamer(path)


