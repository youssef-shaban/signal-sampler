from turtle import position
import streamlit as st
from utils import download_signal, read_csv, read_wav, reconstructor, render_svg, sampled_signal_maxf, samplingRate, signal_sum, sampled_signal, add_noise
import numpy as np
import pandas as pd
import plotly.graph_objects as go



st.set_page_config(
    page_title="Signal Sampler",
    page_icon="📈",
    layout="wide"
)
render_svg("svg.svg")

with open("style.css") as design:
    st.markdown(f"<style>{design.read()}</style>", unsafe_allow_html=True)

# Initialization of Session State attributes (time,uploaded_signal)
if 'time' not in st.session_state:
    st.session_state.time =np.linspace(0,5,2000)
if 'uploaded_signal' not in st.session_state:
    st.session_state.uploaded_signal = np.sin(2*np.pi*st.session_state.time)


#function to add new signal
def add_simulated_signal():
    if st.session_state.signal_name in st.session_state.simulated_signal.keys():
        left_column.error("duplicated Name")
        return 
    if st.session_state.signal_name =="":
        st.session_state.signal_name="Signal_"+str(len(st.session_state.simulated_signal)+1)
    st.session_state.simulated_signal[st.session_state.signal_name]={
        "freq_value":st.session_state.freq_value,
        "mag_value":st.session_state.mag_value
    }
#function to edit selected signal
def edit_simulated_signal(signal_name,freq,mag):
    st.session_state.simulated_signal[signal_name]={
        "freq_value": freq,
        "mag_value": mag
    }

# Initialization of Session State attribute (simulated_signal)
if "simulated_signal" not in st.session_state:
    st.session_state.simulated_signal= {"signal_1":{"mag_value":1,"freq_value":1}}

if "choose_signal" not in st.session_state:
    st.session_state.choose_signal="Simulating"

ce, left_column,  middle_column, right_column, ce = st.columns([0.07, 1,  3.5, 1, 0.07])
#right_column responsible for : sampling rate slider , adding noise ,editing and removing signals , Downloading Signal
with right_column:
    st.header(" ")
    sampling_options=("10Hz","100Hz","1KHz","10KHz","100KHz")
    #sampling_rate_scale variable to store scale of frequency from selectbox
    sampling_rate_scale= st.selectbox("Scale of freq.",sampling_options,key="sampling_rate_scale")
    #getting maxV, minV,step,format values from samplingRate() function
    maxV, minV,step, format= samplingRate(sampling_rate_scale)
    #adding sampling rate slider to get sampling rate from user
    sampling_rate = st.slider(
            "sampling rate",
            min_value=minV,
            max_value=maxV,
            step=step,
            format=format,
            key="sampling_rate"
        )
    noise_checkbox=st.checkbox("Add Noise",key="noise_checkbox")
    if noise_checkbox:
        noise=st.slider("SNR",min_value=1,step=1,max_value=100,value=1,key="noise_slider")

    if st.session_state.simulated_signal and st.session_state.choose_signal=="Simulating":
        #Editing Expander
        # with st.expander("Edit Signal"):
        edit_option_radio_button= st.radio("Edit option",options=("Remove","Edit","View Table"),horizontal=True, key="edit_option_radio_button")
        selected_name= st.selectbox("choose a signal", st.session_state.simulated_signal.keys())
        frquency=st.session_state.simulated_signal[selected_name]["freq_value"]
        magnitude=st.session_state.simulated_signal[selected_name]["mag_value"]

        if edit_option_radio_button == "Remove":
            st.write('Frequency = ',frquency,'Hz')
            st.write('Amplitude = ',magnitude)
            remove_button=st.button("Remove")
            if remove_button:
                del st.session_state.simulated_signal[selected_name]
        elif edit_option_radio_button == "Edit":
            freq = st.number_input('Frequency',value=int(frquency))
            amp = st.number_input('Amplitude', value=int(magnitude))
            Save_button=st.button("Save")

            styl = f"""
            <style>
                .streamlit-expander button{{
                    border-color: green !important;
                    color: green;
                }}
                .streamlit-expander button:hover{{
                    border-color: rgb(255, 255, 255) !important;
                    color: rgb(255, 255, 255);
                    background-color: green;
                }}

                .streamlit-expander button:focus{{
                    box-shadow: rgb(0 128 0 / 50%) 0px 0px 0px 0.2rem;
                    outline: none;
                    color: rgb(255, 255, 255) !important;
                }}
            </style>
            """  
            st.markdown(styl, unsafe_allow_html=True)

            if Save_button:
                edit_simulated_signal(selected_name,freq,amp)
            
        #Table Expander 
        if edit_option_radio_button == "View Table": 
        # with st.expander("View Signals Table"):
            # st.table(df)
            df = pd.DataFrame(st.session_state.simulated_signal.values() , index = st.session_state.simulated_signal.keys())   
            st.dataframe(df,use_container_width=True, height=178)

#End of right_column

#left_column responsible for : uploading ot simulating signals , selecting seginal period , add signals ,selecting type of graph 
with left_column:
    st.header(" ") 
    #radio buttons to select to upload or simulate signal
    choose_signal= st.radio("Choose Signal",options=("Uploaded Signal","Simulating"),horizontal=True, key="choose_signal")
    if choose_signal=="Simulating":
        #slider to select signal period
        signal_period= st.slider("Signal Period",min_value=0.1,max_value=10.0,step=0.1,value=1.0,format="%fsec",key="signal_period");
        #button to add signal
        add_signal=st.button("Add Signal")
        if add_signal:
            #form to take added signal values(Signal Name, Signal Frequency, Signal Magnitude) from user
            with st.form("add_signal_form"):
                signal_name= st.text_input("Enter Signal Name", key="signal_name")
                # sampling_rate_scale= st.selectbox("Scale of freq.",("100Hz","100KHz"),key="add_signal_freq_scale")
                signal_freq = st.slider(
                        "Choose Signal freqency",
                        min_value=1,
                        max_value=100,
                        step=1,
                        value=1,
                        key="freq_value",
                        format=format
                    )
                signal_mag= st.slider("Choose Signal magnitude",value=1,min_value=1,max_value=100,step=1,key="mag_value")
                add_button=st.form_submit_button("Add Signal",on_click=add_simulated_signal)
    elif choose_signal=="Uploaded Signal":
        file=st.file_uploader(label="Upload Signal File", key="uploaded_file",type=["csv","wav"])
        browseButton_style = f"""
        <style>
            .css-1plt86z .css-186ux35{{
            display: none !important;
        }}

        .css-1plt86z{{
            cursor: pointer !important;
            user-select: none;
        }}

        .css-u8hs99{{
            flex-direction: column !important;
            text-align: center;
            margin-right: AUTO;
            margin-left: auto;
        }}

        .css-1m59kx1{{
            margin-right: 0rem !important;
        }}
        </style>
        """  
        st.markdown(browseButton_style, unsafe_allow_html=True)
        if file:
            if file.name.split(".")[-1]=="wav":
                signal, time=read_wav(file)
                st.session_state.uploaded_signal=signal
                st.session_state.time= time
            elif file.name.split(".")[-1]=="csv":
                try:
                    signal, time=read_csv(file)
                    st.session_state.uploaded_signal=signal
                    st.session_state.time= time
                except:
                    st.error("Import a file with X as time and Y as amplitude")
    # selected_graphs= st.selectbox("Select type of graph",("Signal with Samples","Samples Only","Signal Only","Reconstructed Signal","Display All"),key="graph_type")
    Signal = st.checkbox('Signal', value= True)  
    Samples = st.checkbox('Samples')  
    Reconstructed = st.checkbox('Reconstructed')  


#End of left_column

#middle_column responsible for viewing signals graphs(Original and Reconstructed)
with middle_column:
    signal_flag=False
    sample_flag=False
    reconstruction_flag=False

    if(Signal):
        signal_flag=True
    if(Samples):
        sample_flag=True
    if(Reconstructed):
        reconstruction_flag=True

    time=np.linspace(0,5,2000)
    full_signals=np.zeros(time.shape)
    if st.session_state.choose_signal =="Uploaded Signal":
        full_signals, time= st.session_state.uploaded_signal, st.session_state.time
    
    else:
        time= np.linspace(0, st.session_state.signal_period, int(st.session_state.signal_period*500))
    
        full_signals=signal_sum(st.session_state.simulated_signal,time)

    if st.session_state.noise_checkbox:
        full_signals=add_noise(full_signals,st.session_state.noise_slider)
    fig = go.Figure()
    if signal_flag:
        fig.add_trace(go.Scatter(x=time,
                                y=full_signals,
                                mode='lines',
                                name='Signal'))
    if sample_flag:
        if st.session_state.sampling_rate_scale=="F(max)Hz":
            sampled_x, sampled_time=sampled_signal_maxf(full_signals,time, st.session_state.sampling_rate, st.session_state.maxf)
        else:
            sampled_x, sampled_time=sampled_signal(full_signals,time, st.session_state.sampling_rate, st.session_state.sampling_rate_scale)
        
        fig.add_trace(go.Scatter(x=sampled_time,
                                y=sampled_x,
                                mode='markers',
                                name='Samples', marker={"color":"black", 'size' : 17}))    
    if reconstruction_flag:
        if st.session_state.sampling_rate_scale=="F(max)Hz":
            sampled_x, sampled_time=sampled_signal_maxf(full_signals,time, st.session_state.sampling_rate, st.session_state.maxf)
        else:
            sampled_x, sampled_time=sampled_signal(full_signals,time, st.session_state.sampling_rate, st.session_state.sampling_rate_scale)
        if len(sampled_time) != 1:
            recon_signal=reconstructor(time, sampled_time,sampled_x)
            fig.add_trace(go.Scatter(x=time, y=recon_signal,
                    mode='lines',
                    name='reconstructed signal', line={"color":"orange"}))
            
    fig.update_xaxes(showgrid=True, zerolinecolor='black', gridcolor='lightblue', range = (-0.1,st.session_state.signal_period))
    fig.update_yaxes(showgrid=True, zerolinecolor='black', gridcolor='lightblue', range = (-1*(max(full_signals)+0.1*max(full_signals)),(max(full_signals)+0.1*max(full_signals))))
    fig.update_layout(
            font = dict(size = 20),
            xaxis_title="Time (sec)",
            yaxis_title="Amplitude",
            height = 600,
            margin=dict(l=0,r=0,b=5,t=0),
            legend=dict(orientation="h",
                        yanchor="bottom",
                        y=0.92,
                        xanchor="right",
                        x=0.99,
                        font=dict(size= 18, color = 'black'),
                        bgcolor="LightSteelBlue"
                        ),
            paper_bgcolor='rgb(4, 3, 26)',
            plot_bgcolor='rgba(255,255,255)'
        )
    fig.update_yaxes(automargin=True)
    st.plotly_chart(fig,use_container_width=True)

    

    
#End of middle_column

with right_column:
    st.download_button(label="Download data as CSV", data=download_signal(full_signals,time),file_name="signal_data.csv",mime='text/csv')
