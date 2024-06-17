import streamlit as st
import os

#for audio transcription
import transcribe
import openai
from st_audiorec import st_audiorec

#for text2image
import requests
from PIL import Image
from streamlit_pannellum import streamlit_pannellum

#for map
from streamlit_folium import folium_static
import folium

#for upscale
import replicate


# Initialize the OpenAI client
openai_api_key = os.environ['openai_api_key']
client = openai.OpenAI(api_key=openai_api_key)

# Authenticate the SD client using the environment variable
sd_api_key = os.environ['sd_api_key']

#Replicate API
REPLICATE_API_TOKEN = os.environ['REPLICATE_API_TOKEN']

# Set page theme
page_bg_color = "#000ff0"
font_color = "#ffffff"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {page_bg_color};
        secondary-background-color: {page_bg_color};
        font-family: monospace;
        color: {font_color};
    }}
    .st-audiorec-button {{
        background-color: {page_bg_color};
        color: {font_color};
        border: 1px solid {page_bg_color};
        border-radius: 5px;
    }}
    </style>
    """,
            unsafe_allow_html=True)

st.image("logo.png")

#title
st.markdown("""
    </style>
    <h1 class="title">Creating cities of tomorrow, together.</h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    <style>
    .title {
        text-align: center;      /* Center align the text */
        color: white;            /* Set the text color to white */
        font-size: 3em;          /* Adjust the font size as needed */
        margin-bottom: 0px;
        margin-bottom: 80px;     /* Add space below the title */
    }
    """,
            unsafe_allow_html=True)

#subheaders

st.markdown("""
    </style>
    <h1 class="subheader"> Click on the on the <span style="color: red;">red pin</span> to see SSUAVE 3000's street now. </h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    </style>
    <h1 class="subheader">
    Click on the <span style="color: black;">blue pin</span> to see the possible impact of the Barcelona Nature Plan on SSUAVE 3000's street in 2030. </h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    <style>
    .subheader {
        text-align: center;      /* Center align the text */
        color: white;            /* Set the text color to white */
        font-size: 2em;          /* Adjust the font size as needed */
    }
    """,
            unsafe_allow_html=True)

# center on Ssuave 3000
m = folium.Map(location=[41.41199168509924, 2.179774535965951],
               zoom_start=17,
               width='100%',
               height='1000px')

# Define the iframe with the provided URL
iframe1 = folium.IFrame(
    '''<span style="font-family: 'Arial', sans-serif;">SSUAVE 3000</span> 
 <iframe src="https://momento360.com/e/u/16e4c653eea14e7491aac5d4d0919165?utm_campaign=embed&utm_source=other&heading=0&pitch=0&field-of-view=75&size=medium&display-plan=false&allowfullscreen=true&hide-cardboard=true&display-mode=mp" width="550" height="330" style="border:0;" allowfullscreen=true></iframe>''',
    width=570,
    height=370)
# Create a Popup with the iframe
popup1 = folium.Popup(iframe1)
# Add a marker with the popup on the map
folium.Marker(
    location=[41.41199168509924,
              2.179774535965951],  # Change this location as needed
    popup=popup1,
    icon=folium.Icon(color='red')).add_to(m)

iframe2 = folium.IFrame(
    '''<span style="font-family: 'Arial', sans-serif;">Future SSUAVE 3000</span> 
 <iframe src="https://momento360.com/e/u/9c9ecbad0fcc4e57bd665f23945e25ad?utm_campaign=embed&utm_source=other&heading=0&pitch=0&field-of-view=75&size=medium&display-plan=false&allowfullscreen=true&hide-cardboard=true&display-mode=mp" width="550" height="330" style="border:0;" allowfullscreen=true></iframe>''',
    width=570,
    height=370)

popup2 = folium.Popup(iframe2)
# Add a marker with the popup on the map
folium.Marker(
    location=[41.411833183626136,
              2.1796909997706426],  # Change this location as needed
    popup=popup2,
    icon=folium.Icon(color='blue')).add_to(m)
# Display the map in Streamlit
folium_static(m)

#modification

st.markdown("""
    </style>
    <h1 class="subheader"> HAVE YOUR SAY!
    </h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    </style>
    <h1 class="subheader"> Tell us how you'd like to modify this possible future:<br><br>
    Record your answer in the box below.

    Example: "add trees and bicycles on streets and flowers on buildings."
    </h1>
    """,
            unsafe_allow_html=True)


def get_next_audio_filename(directory,
                            base_filename="audio",
                            extension=".wav"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = os.listdir(directory)
    matching_files = [
        f for f in files
        if f.startswith(base_filename) and f.endswith(extension)
    ]
    numbers = [
        int(f[len(base_filename):-len(extension)]) for f in matching_files
        if f[len(base_filename):-len(extension)].isdigit()
    ]
    next_number = max(numbers, default=0) + 1
    return os.path.join(directory, f"{base_filename}{next_number}{extension}")


audio_directory = 'docs/audio'
file_path = get_next_audio_filename(audio_directory)

# Inject JavaScript directly for Audio Worklet Node
st.markdown("""
<script>
if (typeof AudioWorkletNode !== 'undefined') {
    const audioContext = new AudioContext();
    audioContext.audioWorklet.addModule('processor.js').then(() => {
        const audioWorkletNode = new AudioWorkletNode(audioContext, 'processor');
        // Connect the node and start processing
        console.log('AudioWorkletNode is working');
    }).catch(error => {
        console.error('Error loading AudioWorklet module:', error);
    });
} else {
    console.warn('AudioWorkletNode is not supported in this browser.');
}
</script>
""", unsafe_allow_html=True)

#Record and transcribe

st.markdown('''<style>.stAudio {height: 45px; color: #000ff00
} 
</style>''',
            unsafe_allow_html=True)

wav_audio_data = st_audiorec()
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
        init_image_path = "base_image.png"
        resized_image_path = "base_image_resized.png"

        with Image.open(init_image_path) as img:
            resized_img = img.resize((2048, 1024))
            resized_img.save(resized_image_path)

        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "authorization": sd_api_key,
                "accept": "image/*"
            },
            files={"image": open(resized_image_path, "rb")},
            data={
                "prompt": transcription,
                "image": resized_image_path,
                "seed": None,
                "strength": [0.6],
                "mode": "image-to-image",
                "output_format": "png",
                "model": "sd3"
            },
        )

        if response.status_code == 200:

            def get_next_image_filename(directory,
                                        base_filename="modifed",
                                        extension=".png"):
                if not os.path.exists(directory):
                    os.makedirs(directory)
                files = os.listdir(directory)
                matching_files = [
                    f for f in files
                    if f.startswith(base_filename) and f.endswith(extension)
                ]
                numbers = [
                    int(f[len(base_filename):-len(extension)])
                    for f in matching_files
                    if f[len(base_filename):-len(extension)].isdigit()
                ]
                next_number = max(numbers, default=0) + 1
                return os.path.join(
                    directory, f"{base_filename}{next_number}{extension}")

            image_directory = 'static/images' # MINNIE: Changed folder name to 'static/images'
            os.makedirs(image_directory, exist_ok=True)

            image_path = get_next_image_filename(image_directory)
            with open(image_path, 'wb') as new_image:
                new_image = new_image.write(response.content)
            print("New image saved")
            print(image_path)  # debug line by minnie

            if image_path is not None:
                image_content = open(image_path, "rb")
                upscaled = replicate.run(
                    "mv-lab/swin2sr:a01b0512004918ca55d02e554914a9eca63909fa83a29ff0f115c78a7045574f",
                    input={
                        "task": "real_sr",
                        "image": image_content
                    }
                )
                print(upscaled)
                if upscaled is not None:
                    def get_next_upscale_filename(directory, base_filename="upscaled", extension=".png"):
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        files = os.listdir(directory)
                        matching_files = [f for f in files 
    
                        if f.startswith(base_filename) and f.endswith(extension)]
                        numbers = [int(f[len(base_filename):-len(extension)]) for f in matching_files if f[len(base_filename):-len(extension)].isdigit()]
                        next_number = max(numbers, default=0) + 1
                        return os.path.join(directory, f"{base_filename}{next_number}{extension}")
    
                    image_directory = 'static/images'
                    os.makedirs(image_directory, exist_ok=True)
    
                    upscaled_image_path = get_next_upscale_filename(image_directory)
                    with open(upscaled_image_path, 'wb') as file:
                        file.write(response.content)
                    print("Upscaled image saved")
                    st.write("Your chosen future:")
                    st.image(upscaled_image_path)

                    resized_upscaled_image_path = upscaled_image_path
                    with Image.open(upscaled_image_path) as img:
                        resized_img = img.resize((4096, 2048))
                        resized_img.save(resized_upscaled_image_path)

                    st.write("Your chosen future in 360:")

                    streamlit_pannellum(
                        config={
                            "default": {
                                "firstScene": "localScene",
                                "autoLoad": True
                            },
                            "scenes": {
                                "localScene": {
                                    "title": "Your chosen future in 360",
                                    "type": "equirectangular",
                                    "panorama": f'/app/{resized_upscaled_image_path}', # # MINNIE: Changed path
                                    "autoLoad": True,
                                }
                            }
                        })
