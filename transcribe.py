import openai
import os

def audio_transcribe(filename):
  # Set your API key
  openai_api_key = os.environ['openai_api_key']
  client = openai.OpenAI(api_key=openai_api_key)

  with open(filename, 'rb') as audio_file:
      response = client.audio.transcriptions.create(
          model="whisper-1",
          file=audio_file,
          response_format="json"  # Ensure response is in JSON format
      )

  print("Transcription completed")
  try:
      result = response.text # Assuming the response has a 'text' key with the transcription
      print("Your feedback:", result)
      return result
  except KeyError:
      print("Error: 'text' key not found in the response")
      return None