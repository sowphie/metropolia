
import streamlit as st
import openai
import os
from st_audiorec import st_audiorec
from streamlit_pannellum import streamlit_pannellum
from PIL import Image

#for audio transcription
import transcribe

#for text2image
import requests
from PIL import Image

# Initialize the OpenAI client
openai_api_key = os.environ['openai_api_key']
client = openai.OpenAI(api_key=openai_api_key)

# Authenticate the Replicate client using the environment variable
sd_api_key = os.environ['sd_api_key']

# Set page background color
page_bg_color = "#000ff0"
font_url = "https://fonts.google.com/specimen/Questrial?query=qu"
font_color = "#ffffff"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {page_bg_color};
        secondary-background-color: {page_bg_color};
        font-family: monospace ;
        color: {font_color};
    }}
    .stText {{
        font-family: monospace ;
        color: {font_color}
    }}
    </style>
    """,
unsafe_allow_html=True)

st.image("logo.png")
st.write('Click on a pin to view the 360 photo.')

# Embed the Google Map
st.markdown(
    '''
    <iframe src="https://momento360.com/e/uc/4dcf0b8f1f704da686ae80fe02884c06?utm_campaign=embed&utm_source=other&size=medium&display-plan=true&open-plan=true" width="640" height="480"></iframe>
    ''',
    unsafe_allow_html=True
)

st.write("How would you like to modify this future?")
    
st.write("Hold the microphone to record your answer.")

#Record and transcribe
       
wav_audio_data = st_audiorec()

def get_next_audio_filename(directory, base_filename="audio", extension=".wav"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = os.listdir(directory)
    matching_files = [f for f in files if f.startswith(base_filename) and f.endswith(extension)]
    numbers = [int(f[len(base_filename):-len(extension)]) for f in matching_files if f[len(base_filename):-len(extension)].isdigit()]
    next_number = max(numbers, default=0) + 1
    return os.path.join(directory, f"{base_filename}{next_number}{extension}")

audio_directory = 'docs/audio'
file_path = get_next_audio_filename(audio_directory)

#file_path = 'docs/audio/audio.wav'

if wav_audio_data is not None:
    #st.audio(wav_audio_data, format='audio/wav') #display audio player
    with open(file_path, 'wb') as new_file:
        new_file.write(wav_audio_data)

    result_transcription = transcribe.audio_transcribe(file_path)
    transcription = str(result_transcription)
    st.write("Transcription:", transcription)

# text2image

    if transcription is not None:
    
    # Load and resize the image
        init_image_path = "Espanya1.png"
        resized_image_path = "Espanya1_resized.png"

        with Image.open(init_image_path) as img:
            resized_img = img.resize((2048, 1024))
            resized_img.save(resized_image_path)

        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "authorization": sd_api_key,
                "accept": "image/*"
            },
            files={
                "image": open(resized_image_path, "rb")
            },
            data={
                "prompt": transcription,
                "image": resized_image_path,
                "seed": None,
                "strength": [0.6],
                "mode": "image-to-image",
                "output_format": "png",
                "model": "sd3-turbo"
            },
        )
            
        if response.status_code == 200:
            def get_next_image_filename(directory, base_filename="modifed", extension=".png"):
                if not os.path.exists(directory):
                    os.makedirs(directory)
                files = os.listdir(directory)
                matching_files = [f for f in files if f.startswith(base_filename) and f.endswith(extension)]
                numbers = [int(f[len(base_filename):-len(extension)]) for f in matching_files if f[len(base_filename):-len(extension)].isdigit()]
                next_number = max(numbers, default=0) + 1
                return os.path.join(directory, f"{base_filename}{next_number}{extension}")
            image_directory = 'docs/images'
            image_path = get_next_image_filename(image_directory)
            with open(image_path, 'wb') as new_image:
                new_image = new_image.write(response.content)
            print("New image saved")

#generated_image_path = "docs/images/modified.png"



        streamlit_pannellum(
            config={
                "default": {
                    "firstScene": "generated",
                    "autoLoad": True
                },
                "scenes": {
                    "generated": {
                        "title": "Generated Panoramic Image",
                        "type": "equirectangular",
                        "panorama": image_path,
                        "autoLoad": True,
                    }
                }
            }
        )

st.markdown(
    '''
    <iframe width="600" height="400" allowfullscreen style="border-style:none;"                            src="https://cdn.pannellum.org/2.5/pannellum.htm#panorama=https://imgur.com/EsVeC9N"></iframe>
    ''',
    unsafe_allow_html=True
)

