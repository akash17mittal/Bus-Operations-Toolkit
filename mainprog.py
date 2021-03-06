import os
import time
import shutil
# import commonfuncs as cf
import pandas as pd
import numpy as np
import os
import time
import sys
import matplotlib.pyplot as plt
import cv2


def computeThis(queue, configD):
    """
    To check what this prints

    """

    begin_code = time.time()

    root = os.path.dirname(__file__)  # needed for tornado
    inputFolder = os.path.join(root, 'input')

    Intermediate_directory = os.path.join(root, 'Intermediate_analysis')
    Results_directory = os.path.join(root, 'Results')

    os.makedirs(Intermediate_directory, exist_ok=True)
    os.makedirs(Results_directory, exist_ok=True)

    time.sleep(1)

    df = configD['attachment']

    df.to_excel(os.path.join(Intermediate_directory, "sample_intermediate.xlsx"), index=False)

    queue.put(("intermediate_file_created", os.path.join(Intermediate_directory, "sample_intermediate.xlsx")))

    max_delay_allowed_in_minuts = configD["maxDelay"]
    max_travel_time_allowed = configD["travelTime"]
    max_running_time = configD["maxRunning"]

    time.sleep(1)

    d2 = 1
    if d2 == 0:
        queue.put(("error", "Current Form Four do not have any AC Bus trips"))
        return

    df.to_excel(os.path.join(Results_directory, "Output_FORM-IV.xlsx"), index=False)
    df.to_excel(os.path.join(Results_directory, "Saved_AC-Buses.xlsx"), index=False)
    end_code = time.time()
    total_time_taken = (end_code - begin_code) / 3600

    values = np.array([2, 5, 3, 6, 4, 7, 1])
    idx = np.array(list('abcdefg'))

    plot1 = pd.Series(index=idx, data=values)

    before_opt = np.arange(10, 15)
    after_opt = before_opt - 2

    route_names = [f"Route {i}" for i in range(1, 6)]

    route_results = pd.DataFrame({"route_name": route_names, "before_opt": before_opt, "after_opt": after_opt})

    root_dir1 = root if len(root) else os.curdir
    o1Filename = 'Intermediate_analysis_output'
    o2Filename = 'Results_output'
    shutil.make_archive(base_name=os.path.join(root, o1Filename), format='zip', root_dir=root_dir1,
                        base_dir='Intermediate_analysis')
    shutil.make_archive(base_name=os.path.join(root, o2Filename), format='zip', root_dir=root_dir1, base_dir='Results')
    #

    IMAGE_HEIGHT = 200
    IMAGE_WIDTH = 700
    sample = np.zeros(shape=(IMAGE_HEIGHT, IMAGE_WIDTH, 4))
    CENTER = (int(IMAGE_WIDTH/2), int(IMAGE_HEIGHT/2))
    CIRCLE_COLOR = (0, 165, 255, 255)
    sample = cv2.circle(sample, CENTER, 80, CIRCLE_COLOR, -1)

    TEXT_FACE = cv2.FONT_HERSHEY_DUPLEX
    TEXT_SCALE = 1
    TEXT_THICKNESS = 1
    TEXT = "50000"
    TEXT_COLOR = (0, 0, 0, 255)
    text_size, _ = cv2.getTextSize(TEXT, TEXT_FACE, TEXT_SCALE, TEXT_THICKNESS)
    text_origin = (int(CENTER[0] - text_size[0] / 2), int(CENTER[1] + text_size[1] / 2))
    sample = cv2.putText(sample, TEXT, text_origin, TEXT_FACE, TEXT_SCALE, TEXT_COLOR, TEXT_THICKNESS, cv2.LINE_AA)

    sample = sample/255.0

    final_results = {'route_results': route_results,
                     'output1': f"{os.path.join(root, o1Filename)}.zip",
                     'output2': f"{os.path.join(root, o2Filename)}.zip",
                     "plot1": sample,
                     "plot2": plot1}
    queue.put(["Done", final_results])