# %% [markdown]
#  ## Global Imports And Library Setup

# %%
# # Uncomment below to install missing packages
# !python -m pip install --upgrade --requirement ./requirements.txt


# %% [markdown]
#  ### Login to Azure CLI

# %%
# # Login to Azure CLI
# !az login --use-device-code --tenant "38b2262e-92fe-4b71-a4d0-ebf91a3e2909"
# !az account set --subscription "47c2af6c-fe2f-4dbd-9193-9b50a99044b7"


# %% [markdown]
#  ### Import Python libraries

# %%
import os
import re
import ast
import json
import time
import uuid
import openai
import logging
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
from pathlib import Path
from tqdm.auto import tqdm
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Load environment variables from `.env` file
load_dotenv(verbose=True, override=True)


# %% [markdown]
#  ### Setup environment constants

# %%
# Azure container name
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "content-creation-pipeline")

try:
    SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD = ast.literal_eval(
        os.environ.get("SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD", "False")
    )
except:
    SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD = False


# %% [markdown]
#  ## Clean Azure Data (If Needed)

# %%
# # Used to clean up the blob if doing a bulk-delete
# ################################################################################################
# container_client = blob_service_client.get_container_client(container=CONTAINER_NAME)
# for n in container_client.list_blob_names():
#     if not n.startswith("data"):
#         continue
#     folderSplits = n.split("/")
#     if len(folderSplits) != 3:
#         continue
#     try:
#         puzzleId = int(n.split("/")[1], base=10)
#         if puzzleId > 12:
#             print(f"Deleting blob = {n}")
#             blob_service_client.get_blob_client(container=container_name, blob=n).delete_blob()
#     except ValueError as ex:
#         if ex.args[0].startswith("invalid literal for int() with base 10"):
#             # This is an ad-hoc file. And not a puzzle folder
#             continue
#         else:
#             print(ex)
#             break


# %% [markdown]
#  ## Setup Azure Libraries

# %%
# account_url = "https://rakhdelstudioapps.blob.core.windows.net"
# default_credential = DefaultAzureCredential(
#     exclude_environment_credential=True,
#     exclude_managed_identity_credential=True,
#     exclude_visual_studio_code_credential=True,
#     exclude_shared_token_cache_credential=True,
#     interactive_browser_tenant_id="38b2262e-92fe-4b71-a4d0-ebf91a3e2909",
# )

# # Create the BlobServiceClient object
# blob_service_client = BlobServiceClient(account_url, credential=default_credential)


# %%
import azure.cognitiveservices.speech as speechsdk
import wave

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"),
    region=os.environ.get("SPEECH_REGION"),
    speech_recognition_language="gu-IN-DhwaniNeural",
)

language = "gu-IN"
speech_config.speech_synthesis_language = language
# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name = "gu-IN-DhwaniNeural"


def generate_transcription(text: str, output_wave_file: str) -> None:
    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=output_wave_file,
    )

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    ssml = (
        """
    <!--ID=B7267351-473F-409D-9765-754A8EBCDE05;Version=1|{
        "VoiceNameToIdMapItems":[
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (gu-IN, DhwaniNeural)",
                "ShortName": "gu-IN-DhwaniNeural",
                "Locale": "gu-IN",
                "Id": "97ebc7c6-1e92-4764-806b-ad61201a60a5",
                "VoiceType": "StandardVoice"
            }
        ]
    }-->
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
        xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml"
        xml:lang="gu-IN">
        <voice name="gu-IN-DhwaniNeural">
            """
        + text
        + """
        </voice>
    </speak>
    """
    )

    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml=ssml).get()

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        pass
        # print(f"Audio transcription was successful!")
        # with wave.open(output_wave_file, "wb") as out_f:
        #     out_f.setnchannels(1)
        #     out_f.setsampwidth(2) # number of bytes
        #     out_f.setframerate(44100)
        #     out_f.writeframesraw(speech_synthesis_result.audio_data)
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


# %% [markdown]
#  ## Sync `data` from `blob` to `local` folder

# %%
# if SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD:
#     # Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#azure-storage-blob-blobserviceclient-get-container-client
#     container_client = blob_service_client.get_container_client(
#         container=CONTAINER_NAME
#     )

#     for blob_name in tqdm(
#         iterable=container_client.list_blob_names(name_starts_with="data")
#     ):
#         # Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#azure-storage-blob-blobserviceclient-get-blob-client
#         blob_client = blob_service_client.get_blob_client(
#             container=CONTAINER_NAME, blob=blob_name
#         )
#         blob_name_dirname = os.path.dirname(blob_name)
#         os.makedirs(name=blob_name_dirname, exist_ok=True)
#         if not os.path.exists(blob_name):
#             with open(blob_name, "wb") as local_file:
#                 download_stream = blob_client.download_blob()
#                 local_file.write(download_stream.readall())


# %% [markdown]
# ## Content Creation Pipeline

# %% [markdown]
# ### Steps
#
# 1. Get a Gujarati Kahevat in Gujarati with English Meaning
# 2. Get a Background Image from ...
# 3. Get a Background Music from ...

# %%
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Popular Gujarati Kahevat in Gujarati with Meaning in English",
    temperature=0.7,
    max_tokens=999,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
)

# %%
print(response)

# %% [markdown]
# ## Prepare Content List

# %% [markdown]
# ### Steps
#
# 1. Put the Text on Image
# 2. Create a animation of text on Image
# 3. Put Music in background
# 4. Save the video as a mp4

# %%


# %% [markdown]
# ## Process Content List

# %% [markdown]
# ### Steps
#
# 1. Upload to the blob
# 2. Upload to social network
#

# %%
