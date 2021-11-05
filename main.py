import streamlit as st
import pandas as pd
from multiprocessing import Process, Queue
from mainprog import computeThis
import base64

import time


def reinitialize_state(configuration):
    st.session_state.pop("final_results", None)
    st.session_state["config"] = configuration.copy()


def process_queue_message(col, value):
    # -- Allow data download
    if value[0] == "intermediate_file_created":
        df = pd.read_excel(value[1])
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        fn = value[1].split('/')[-1]
        href = f'<a href="data:file/csv;base64,{b64}" download="{fn}">Download Intermediate Data as CSV File</a>'
        col.markdown(href, unsafe_allow_html=True)


def main():
    apptitle = 'Bus Operation'

    st.set_page_config(page_title=apptitle, page_icon=":bus:", layout="wide")

    app_page = st.sidebar.selectbox('Choose Menu', ('Home', 'Results'))

    st.sidebar.image("./images/busopt.jpg")

    if app_page == 'Home':
        # Title the app
        st.title("Bus Operations Toolkit ")

        col1, col2 = st.columns((1, 1))

        opt_params_form = col1.form(key='opt_params')
        data_file = opt_params_form.file_uploader("Upload Current FORM-IV", type=['csv'])
        minimum_safety_headway = opt_params_form.number_input("Minimum Safety Headway (in minutes)", step=1)
        max_running_time_bus = opt_params_form.number_input("Max Running Time of Bus (in hours)", step=1)
        travel_time_between_stations = opt_params_form.number_input("Travel Time between Stations (in hours)", step=1)
        solve = opt_params_form.form_submit_button('Solve')

        if solve:
            if data_file is not None:

                configD = {"file_details": data_file.name,
                           "maxDelay": float(minimum_safety_headway),
                           "maxRunning": float(max_running_time_bus),
                           "travelTime": float(travel_time_between_stations)}

                reinitialize_state(configD)
                col2.markdown("<h2 style='text-align: center; color: Black;'>Processing Details</h2>",
                              unsafe_allow_html=True)
                file_details = {"Filename": data_file.name, "FileType": data_file.type, "FileSize": data_file.size}
                # col2.write("File Details:")
                # col2.write(file_details)
                df = pd.read_csv(data_file)
                col2.write("Sample Data:")
                col2.dataframe(df.head())
                configD["attachment"] = df
                q = Queue()
                pr = Process(target=computeThis, args=(q, configD))
                pr.start()

                col2.write("Process Started...")

                progress_value = 5

                progress_bar = col2.progress(progress_value)

                while True:
                    if not q.empty():
                        value = q.get(True)
                        progress_bar.progress(progress_value + 10)
                        if value[0] == "Done":
                            progress_bar.progress(100)
                            st.session_state["final_results"] = value[1]
                            col2.write("## Optimization Finished")
                            col2.write("Check Results!")
                            break
                        else:
                            process_queue_message(col2, value)
                    else:
                        time.sleep(1)

                pr.join()

    else:
        if 'final_results' in st.session_state:

            if 'config' in st.session_state:
                st.write("## Optimization Parameters")
                st.write(str(st.session_state["config"]))

            col1, col2 = st.columns((1, 1))
            col1.markdown("<h2 style='text-align: center; color: Black;'>Route Analysis</h2>", unsafe_allow_html=True)
            col2.markdown("<h2 style='text-align: center; color: Black;'>Analysis Results</h2>", unsafe_allow_html=True)

            routing_results = st.session_state["final_results"]['route_results']

            option = col1.selectbox('Choose Route', routing_results["route_name"])

            col1.subheader("Before Optimization:")
            col1.write("## " + str(routing_results[routing_results["route_name"] == str(option)].iloc[0]["before_opt"]))

            col1.subheader("After Optimization:")
            col1.write("## " + str(routing_results[routing_results["route_name"] == str(option)].iloc[0]["after_opt"]))

            col1.markdown("<h2 style='text-align: center; color: Black;'>Download Optimization Results</h2>",
                          unsafe_allow_html=True)

            with open(st.session_state["final_results"]['output1'], "rb") as fp:
                btn = col1.download_button(
                    label="Download Intermediate Analysis Results",
                    data=fp,
                    file_name=st.session_state["final_results"]['output1'].split('/')[-1],
                    mime="application/zip"
                )

            with open(st.session_state["final_results"]['output2'], "rb") as fp:
                btn2 = col1.download_button(
                    label="Download Final Results",
                    data=fp,
                    file_name=st.session_state["final_results"]['output2'].split('/')[-1],
                    mime="application/zip"
                )

            # Plot the analysis results
            col2.bar_chart(st.session_state["final_results"]["plot1"])
            col2.bar_chart(st.session_state["final_results"]["plot2"])


if __name__ == '__main__':
    main()
