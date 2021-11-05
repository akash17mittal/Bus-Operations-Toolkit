import streamlit as st
import pandas as pd
from multiprocessing import Process, Queue
from mainprog import computeThis
import base64

import time


def process_queue_message(col1, col2, col3, value):
    # -- Allow data download
    if value[0] == "intermediate_file_created":
        df = pd.read_excel(value[1])
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        fn = value[1].split('/')[-1]
        href = f'<a href="data:file/csv;base64,{b64}" download="{fn}">Download Intermediate Data as CSV File</a>'
        col1.markdown(href, unsafe_allow_html=True)


def main():
    apptitle = 'Bus Operation'

    st.set_page_config(page_title=apptitle, page_icon=":bus:", layout="wide")

    # Title the app
    st.markdown("<h1 style='text-align: center; color: Black;'>Bus Operations Toolkit</h1>", unsafe_allow_html=True)

    st.sidebar.title("Choose Configuration ")

    data_file = st.sidebar.file_uploader("Upload Current FORM-IV", type=['csv'])
    minimum_safety_headway = st.sidebar.text_input("Minimum Safety Headway (in minutes)", 5)
    max_running_time_bus = st.sidebar.text_input("Max Running Time of Bus (in hours)", 16)
    travel_time_between_stations = st.sidebar.text_input("Travel Time between Stations (in hours)", 1)

    col1, col2, col3 = st.columns((1, 1, 1))

    col1.markdown("<h2 style='text-align: center; color: Black;'>Processing Details</h2>", unsafe_allow_html=True)
    col2.markdown("<h2 style='text-align: center; color: Black;'>Route Analysis</h2>", unsafe_allow_html=True)
    col3.markdown("<h2 style='text-align: center; color: Black;'>Analysis Results</h2>", unsafe_allow_html=True)

    if st.sidebar.button("Process"):
        if data_file is not None:
            file_details = {"Filename": data_file.name, "FileType": data_file.type, "FileSize": data_file.size}
            col1.write("File Details:")
            col1.write(file_details)

            df = pd.read_csv(data_file)

            col1.write("Sample Data:")
            col1.dataframe(df.head())

            configD = {"attachment": df,
                       "maxDelay": float(minimum_safety_headway),
                       "maxRunning": float(max_running_time_bus),
                       "travelTime": float(travel_time_between_stations)}

            q = Queue()
            pr = Process(target=computeThis, args=(q, configD))
            pr.start()

            col1.write("Process Started...")

            progress_value = 5

            progress_bar = col1.progress(progress_value)

            while True:
                if not q.empty():
                    value = q.get(True)
                    progress_bar.progress(progress_value + 10)
                    if value[0] == "Done":
                        progress_bar.progress(100)

                        option = col2.selectbox('Choose Route', value[1]["route_name"])

                        col2.subheader("Before Optimization:")
                        col2.write(value[1][value[1]["route_name"] == str(option)].iloc[0]["before_opt"])

                        col2.subheader("After Optimization:")
                        col2.write(value[1][value[1]["route_name"] == str(option)].iloc[0]["after_opt"])

                        # Plot the analysis results
                        col3.pyplot(value[2])
                        col3.pyplot(value[3])
                        break
                    else:
                        process_queue_message(col1, col2, col3, value)
                else:
                    time.sleep(1)

            pr.join()


if __name__ == '__main__':
    main()
