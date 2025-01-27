import streamlit as st
import os
from PIL import Image

#for text2image
import requests
from PIL import Image
from streamlit_pannellum import streamlit_pannellum

#for map
from streamlit_folium import folium_static
import folium

# Authenticate the SD client using the environment variable
sd_api_key = os.environ['sd_api_key']

#Replicate API
REPLICATE_API_TOKEN = os.environ['REPLICATE_API_TOKEN'] #only needed for image upscaling

# Set page theme
primaryColor="#000ff0"
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
        font-size: 2em;          /* Adjust the font size as needed */
        margin-bottom: 0px;
        margin-bottom: 80px;     /* Add space below the title */
    }
    """,
            unsafe_allow_html=True)

#subheaders
st.markdown("""
    </style>
    <h1 class="subheader"> Click on the on the <span style="color: red;">red pin</span> to see Elisava's street now. </h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    </style>
    <h1 class="subheader">
    Click on the <span style="color: black;">blue pin</span> to see the possible impact of the Barcelona Nature Plan on Elisava's street in 2030. </h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    <style>
    .subheader {
        text-align: center;      /* Center align the text */
        color: white;            /* Set the text color to white */
        font-size: 1em;          /* Adjust the font size as needed */
    }
    """,
            unsafe_allow_html=True)

# center on Elisava
m = folium.Map(location=[41.378442, 2.176321],
               zoom_start=17,
               width='100%',
               height='1000px')

# Define the iframe with the provided URL
iframe1 = folium.IFrame(
    '''<span style="font-family: 'Arial', sans-serif;">Elisava now</span> 
 <iframe src="https://momento360.com/e/u/710553a13e174892a2fa93026416e218?utm_campaign=embed&utm_source=other&heading=0&pitch=0&field-of-view=75&size=medium&display-plan=false&allowfullscreen=true&hide-cardboard=true&display-mode=mp" width="550" height="330" style="border:0;" allowfullscreen=true></iframe>''',
    width=570,
    height=370)

# Create a Popup with the iframe
popup1 = folium.Popup(iframe1)

# Add a marker with the popup on the map
folium.Marker(
    location=[41.378552325993844, 2.1764863545405206],  # Change this location as needed
    popup=popup1,
    icon=folium.Icon(color='red')).add_to(m)

iframe2 = folium.IFrame(
    '''<span style="font-family: 'Arial', sans-serif;">Future Elisava</span> 
 <iframe src="https://momento360.com/e/u/247b028c265e4e4290bf902845b26b1a?utm_campaign=embed&utm_source=other&heading=0&pitch=0&field-of-view=75&size=medium&display-plan=false&allowfullscreen=true&hide-cardboard=true&display-mode=mp" width="550" height="330" style="border:0;" allowfullscreen=true></iframe>''',
    width=570,
    height=370)

# Create a second Popup with the iframe
popup2 = folium.Popup(iframe2)

# Add a marker with the popup on the map
folium.Marker(
    location=[41.378442, 2.176321],  # Change this location as needed
    popup=popup2,
    icon=folium.Icon(color='blue')).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Feedback

## Text input


st.markdown("""
    <h1 class="title"> HAVE YOUR SAY!
    </h1>
    """,
            unsafe_allow_html=True)

st.markdown("""
    <h1 class="subheader"> Tell us how you'd like to modify this possible future:<br><br>
   Type your answer in the box below in English.
   <br>
   Example: "add bicycles on streets and flowers on buildings."
    </h1>
    """,
            unsafe_allow_html=True)
    
text = st.text_area(label= "", value="", height=None, max_chars=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Type your answer here.", disabled=False, label_visibility="visible")

if st.button("Click here to send your feedback", type= 'primary'):
    st.write(f'Feedback received: {text}')
    print(text)
    

    def get_next_text_filename(directory,
                                base_filename="text",
                                extension=".txt"):
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
    
    text_directory = 'docs/text'
    text_path = get_next_text_filename(text_directory)
    with open(text_path, 'w') as text_file:
        text_file.write(text)
    print("Text saved to: {text_path}")
    print(text_path)

# text2image
    if text is not None:
    
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
                "prompt": "Do not change the word ELISAVA on the front building. " + text,
                "image": resized_image_path,
                "seed": None,
                "strength": [0.6],
                "mode": "image-to-image",
                "output_format": "png",
                "model": "sd3-turbo"
            },
        )
    
        if response.status_code == 200:
            def get_next_image_filename(directory,
                                        base_filename="modified",
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
    
         
            if new_image is not None:
            
                st.write("Your chosen future for Elisava:")
                st.image(image_path)
        
                st.write("Your chosen future for Elisava in 360 view:")
            
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
                                "panorama": f'/app/{image_path}', # # MINNIE: Changed path
                                "autoLoad": True,
                             }
                            }
                        }
                    )
    
