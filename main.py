from openai import OpenAI
import streamlit as st
from elevenlabs import generate
import time
from kittycad.client import Client

from functions.text_to_cad import text_to_cad_create, get_text_to_cad_model, decode_stl
from functions.img_to_text import describe_image

st.title('AI Modmatrix ✨')
st.subheader('This is a simple AI project prototyping tool, inspired by synthesizer modulation matrices.')
st.write('You can find the source code [in this public repository](https://github.com/chris-ernst/modmatrix-ai). Feel free to use it for your own projects.')
st.write('*Hint: To quickly spin up your own instance, use [Replit](https://replit.com/) and [import the repo](https://docs.replit.com/programming-ide/using-git-on-replit/import-repository). 🚀*')

# Session State Initialization for 'input_result_string'
if 'input_result_string' not in st.session_state:
    st.session_state.input_result_string = ''

# Session State Initialization for 'modifying_prompt'
if 'modifying_prompt' not in st.session_state:
    st.session_state.modifying_prompt = ''

# Session State Initialization for 'output_result_string'
if 'output_result_string' not in st.session_state:
    st.session_state.output_result_string = ''

# Settings in Sidebar
st.sidebar.header('Settings')
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')
if not openai_api_key.startswith('sk-'):
    st.sidebar.warning('Please enter your OpenAI API key!', icon='⚠')
st.sidebar.write(
    'This key is needed for all operations. Get yours [here](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key).')

st.sidebar.write('---')
st.sidebar.header('Optional Settings')

ELEVENLABS_API_KEY = st.sidebar.text_input('11Labs Text-To-Speech API Key (optional)', type='password')
st.sidebar.caption('This key is needed for the audio output. Get yours [here](https://elevenlabs.io/api).')

ZOO_CAD_API_KEY = st.sidebar.text_input('Zoo CAD API Key (optional)', type='password')
st.sidebar.caption('This key is needed for the 3D CAD model output. Get yours [here](https://zoo.dev/docs/api/authentication).')

openAI_client = OpenAI(api_key=openai_api_key)


def check_openai_key():
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key in the sidebar! This key is needed for all operations. Get yours [here](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key).', icon='⚠')
        return False
    else:
        return True

if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key in the sidebar. Get yours [here](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key).')

# Inputs
st.write('---')
st.header('Inputs')

input_type = st.radio(
    "How would you like to provide your input?",
    [":rainbow[Image Upload]", "Webcam Capture", "Text", "Audio (Speech)", ":grey[Microcontroller Data]"],
    index=None, horizontal=True, label_visibility='collapsed'
)

# Image Upload
if input_type == ":rainbow[Image Upload]":
    image_upload = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if image_upload:
        if check_openai_key(): # Key Checker
            st.image(image_upload)
            if st.button('Describe Image'):
                with st.spinner('Processing...'):
                    st.session_state.input_result_string = describe_image(image_upload, openai_api_key)
                st.success('Done!')


# Webcam Capture
elif input_type == "Webcam Capture":
    webcam_capture = st.camera_input("Take a webcam_capture")
    if webcam_capture:
        if check_openai_key(): # Key Checker
            st.image(webcam_capture)
            if st.button('Describe Image'):
                with st.spinner('Processing...'):
                    st.session_state.input_result_string = describe_image(webcam_capture)
                st.success('Done!')


# Text Input
elif input_type == "Text":
    with st.form('text_input_form'):
        text_input = st.text_area("Enter text", placeholder="Write a nice text here!")
        text_input_submitted = st.form_submit_button('Enter')
        if text_input_submitted and text_input != '':
            st.session_state.input_result_string = text_input
        elif text_input_submitted and text_input == '':
            st.warning("Please enter a text")


# Audio Upload
elif input_type == "Audio (Speech)":
    audio_input = st.file_uploader("Upload an audio file", type=["mp3", "wav"])
    if audio_input is not None:
        if check_openai_key():  # Key Checker
            client = OpenAI(api_key=openai_api_key)
            with st.spinner('Processing...'):
                st.session_state.input_result_string = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_input,
                    response_format="text"
                )
            st.success('Done!')


# Microcontroller Data TODO: Implement
elif input_type == ":grey[Microcontroller Data]":
    st.error("This is not yet implemented. Please select another input type.")
    # microcontroller_container = st.container(border=True)
    # microcontroller_container.write(
    #     "Please connect your microcontroller and press the button below to download the connection script.")
    # microcontroller_container.download_button("Download Arduino Script", "microcontroller_script goes here",
    #                                           "Click here to download the microcontroller connection script")
    # microcontroller_container.button("Connect", type="primary")


# No input type selected
else:
    if openai_api_key.startswith('sk-'):
        st.info("Start here by selecting an input type")

# Intermediate Printing
st.write('---')
st.header('🖨️')
st.write(st.session_state.input_result_string)

# Modifying Prompt
st.write('---')
st.header('Optional Modifying Prompt')

with st.form('modifying_prompt_input_form'):
    modifying_prompt_text = st.text_area("Enter text",
                                         placeholder="Your optional modifying prompt here. Can be left empty if not needed, but you will still need to submit it.")
    modifying_prompt_submitted = st.form_submit_button('Enter')
    if modifying_prompt_submitted and modifying_prompt_text != '':
        if check_openai_key():  # Key Checker
            st.session_state.modifying_prompt = modifying_prompt_text

            completion = openAI_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": st.session_state.input_result_string},
                    {"role": "user", "content": st.session_state.modifying_prompt}
                ]
            )

            print(completion.choices[0].message.content)
            st.session_state.output_result_string = completion.choices[0].message.content

    elif modifying_prompt_submitted and modifying_prompt_text == '':
        st.info("Skipping modifying prompt.")
        st.session_state.output_result_string = st.session_state.input_result_string

# Intermediate Printing
st.write('---')
st.header('🖨️')
st.write(st.session_state.output_result_string)

# Outputs
st.write('---')
st.header('Outputs')

output_type = st.radio(
    "How would you like to provide your output?",
    [":rainbow[Image]", "Text", "Audio (Speech)", ":grey[Microcontroller Data]", "CAD Model (Experimental)"],
    index=None, horizontal=True, label_visibility='collapsed'
)

# Image Upload
if output_type == ":rainbow[Image]":
    if st.button('Generate Image'):
        if check_openai_key():  # Key Checker
            with st.spinner('Processing...'):
                response = openAI_client.images.generate(
                    model="dall-e-3",
                    prompt=st.session_state.output_result_string,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
            st.success('Done!')
            st.image(image_url)
            st.link_button("Download Image", image_url)

# Text Input
elif output_type == "Text":
    st.write(st.session_state.output_result_string)

# Audio Text to Speech
elif output_type == "Audio (Speech)":
    if ELEVENLABS_API_KEY == '':
        st.warning("Please enter your **paid** 11Labs API Key in the settings to generate the audio.")
    if ELEVENLABS_API_KEY != '':
        from elevenlabs import set_api_key

        set_api_key(ELEVENLABS_API_KEY)
        if st.button('Generate Audio'):
            audio_output_char_count = len(st.session_state.output_result_string)
            if audio_output_char_count > 2500:
                st.warning(
                    f"Your text is {audio_output_char_count} characters long. The maximum character count for the free tier is 2500. Shortening text.")
                st.session_state.output_result_string = st.session_state.output_result_string[:2500]

            with st.spinner('Processing...'):
                elevenlabs_audio = generate(
                    text=st.session_state.output_result_string,
                    voice="George",
                    model="eleven_multilingual_v2"
                )
            st.success('Done!')
            st.audio(elevenlabs_audio, format='audio/mpeg')


# Microcontroller Data TODO: Implement
elif output_type == ":grey[Microcontroller Data]":
    st.error("This is not yet implemented. Please select another output type.")

# CAD Model
elif output_type == "CAD Model (Experimental)":
    if ZOO_CAD_API_KEY is None or ZOO_CAD_API_KEY == '':
        st.warning("Please enter your ZOO CAD API Key in the settings to generate the 3D model.")
    else:
        client = Client(token=ZOO_CAD_API_KEY)
        st.info(
            '**Straight from their [API documentation](https://zoo.dev/docs/api/ai/generate-a-cad-model-from-text?lang=python):** "This is an alpha endpoint. It will change in the future. The current output is honestly pretty bad. So if you find this endpoint, you get what you pay for, which currently is nothing. But in the future will be made a lot better."')
        cad_prompt_submitted = st.button("Submit")

        if cad_prompt_submitted:
            with st.status("Generating 3D Model", expanded=True) as status:

                # Sending Query
                st.write("Sending Query...")
                cad_gen_id = text_to_cad_create(st.session_state.output_result_string)
                st.write(200, f"CAD Gen ID: {cad_gen_id}")
                st.write("Fetching 3D Model...")

                # Fetching Model
                while True:
                    cad_response_body = get_text_to_cad_model(cad_gen_id)
                    if cad_response_body.status == 'failed':
                        st.write(500, f'Generation {cad_response_body.status}, aborting')
                        break
                    if cad_response_body.status == 'completed':
                        st.write(200, f'Generation {cad_response_body.status}, Model fetched!')
                        break
                    st.write(100, f'Generation {cad_response_body.status}, waiting...')
                    time.sleep(0.1)

                # Converting Model
                st.write("Converting Model...")
                stl_binary = decode_stl(cad_response_body)
                st.write(200, "Model converted!")
                st.download_button(
                    label="Download STL",
                    data=stl_binary,
                    file_name="model.stl",
                    mime="model/stl"
                )
                status.update(label="Generation complete", state="complete")
