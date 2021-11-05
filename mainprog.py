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

    df = configD['attachment']

    df.to_excel(os.path.join(Intermediate_directory, "sample_intermediate.xlsx"), index=False)

    queue.put(("intermediate_file_created", os.path.join(Intermediate_directory, "sample_intermediate.xlsx")))

    max_delay_allowed_in_minuts = configD["maxDelay"]
    max_travel_time_allowed = configD["travelTime"]
    max_running_time = configD["maxRunning"]

    d2=1
    if d2 == 0:
        queue.put(("error", "Current Form Four do not have any AC Bus trips"))
        return

    df.to_excel(os.path.join(Results_directory, "Output_FORM-IV.xlsx"), index=False)
    df.to_excel(os.path.join(Results_directory, "Saved_AC-Buses.xlsx"), index=False)
    end_code = time.time()
    total_time_taken = (end_code-begin_code)/3600


    values = np.array([2,5,3,6,4,7,1])
    idx = np.array(list('abcdefg'))

    fig1 = plt.figure(figsize=(12, 5))
    plt.xticks(rotation=80)
    plt.ticklabel_format(style="plain")
    plt.bar(idx, values)
    plt.xlabel("X - Label")
    plt.ylabel("Y - Label")
    plt.title("Optimization Results 1")

    fig2 = plt.figure(figsize=(12, 5))
    plt.xticks(rotation=80)
    plt.ticklabel_format(style="plain")
    plt.bar(idx, list(range(7)))
    plt.xlabel("X - Label")
    plt.ylabel("Y Label")
    plt.title("Optimization Results 2")

    before_opt = np.arange(10, 15)
    after_opt = before_opt - 2

    route_names = [f"Route {i}" for i in range(1,6)]

    route_results = pd.DataFrame({"route_name": route_names, "before_opt": before_opt, "after_opt": after_opt})

    queue.put(["Done", route_results, fig1, fig2])
    # logs.append(k)
    # #ourdummy code
    # # zipping outputs
    # root_dir1 = root if len(root) else os.curdir
    # cf.logmessage("root_dir:", root_dir1)
    # #logs.append(f"Zipping outputs.. root_dir: {root_dir1}")
    # o1Filename = 'Intermediate_analysis_output'
    # o2Filename = 'Results_output'
    # shutil.make_archive(base_name=os.path.join(root,o1Filename),
    #     format='zip', root_dir=root_dir1, base_dir='Intermediate_analysis' )
    # shutil.make_archive(base_name=os.path.join(root,o2Filename),
    #     format='zip', root_dir=root_dir1, base_dir='Results' )
    #
    # returnD = { 'message': 'completed', 'logs':logs, 'output1': f"{o1Filename}.zip", 'output2': f"{o2Filename}.zip" }
    #
    # return returnD