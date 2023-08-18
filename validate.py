# %% [markdown]
# ## Global Imports And Library Setup

# %%
# # Uncomment below to install missing packages
# !python -m pip install --upgrade --requirement ./requirements.txt

# %% [markdown]
# ### Login to Azure CLI

# %%
# # Login to Azure CLI
# !az login --use-device-code --tenant "38b2262e-92fe-4b71-a4d0-ebf91a3e2909"
# !az account set --subscription "47c2af6c-fe2f-4dbd-9193-9b50a99044b7"

# %% [markdown]
# ### Import Python libraries

# %%
from dotenv import load_dotenv
from tqdm.auto import tqdm
import json
import ast
import logging
import os
import pandas as pd
import re
import sys
import requests
import time
from PIL import Image
from io import BytesIO
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("output.log"), logging.StreamHandler(sys.stdout)],
)

# Load environment variables from `.env` file
load_dotenv(verbose=True, override=True)

# %% [markdown]
# ### Setup environment constants

# %%
# Azure container name
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "gujarati-picture-puzzle")

try:
    SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD = ast.literal_eval(
        os.environ.get("SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD", "False")
    )
except:
    SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD = False

# %% [markdown]
# ## Setup Azure Libraries

# %%
account_url = "https://rakhdelstudioapps.blob.core.windows.net"
default_credential = DefaultAzureCredential(
    exclude_environment_credential=True,
    exclude_managed_identity_credential=True,
    exclude_visual_studio_code_credential=True,
    exclude_shared_token_cache_credential=True,
    interactive_browser_tenant_id="38b2262e-92fe-4b71-a4d0-ebf91a3e2909",
)

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url, credential=default_credential)

# %% [markdown]
# ## Sync `data` from `blob` to `local` folder

# %%
if SYNC_BLOB_TO_LOCAL_FORCE_DOWNLOAD:
    # Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#azure-storage-blob-blobserviceclient-get-container-client
    container_client = blob_service_client.get_container_client(
        container=CONTAINER_NAME
    )

    for blob_name in tqdm(
        iterable=container_client.list_blob_names(name_starts_with="data")
    ):
        # Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#azure-storage-blob-blobserviceclient-get-blob-client
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=blob_name
        )
        blob_name_dirname = os.path.dirname(blob_name)
        os.makedirs(name=blob_name_dirname, exist_ok=True)
        if not os.path.exists(blob_name):
            with open(blob_name, "wb") as local_file:
                download_stream = blob_client.download_blob()
                local_file.write(download_stream.readall())

# %% [markdown]
# ## Prepare Word List

# %%
# Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#azure-storage-blob-blobserviceclient-get-blob-client
blob_client = blob_service_client.get_blob_client(
    container=CONTAINER_NAME, blob=f"data/word_list.json"
)

word_list_local_file_path = "./data/word_list.json"

if not os.path.exists(word_list_local_file_path):
    try:
        with open(file=word_list_local_file_path, mode="wb") as data:
            download_stream = blob_client.download_blob()
            data.write(download_stream.readall())

        print("\nDownloading from Azure Storage as blob: word_list.json\n\t")
    except:
        print("Download failed")
else:
    print(f"File '{word_list_local_file_path}' already exists!")

# %%
with open(file="./data/word_list.json") as f:
    wordList = json.load(f)

# %%
# Convert in-memory Python object to Pandas DataFrame
wordListDf = pd.DataFrame.from_records(
    data=[{"type": "noun", "english": w["noun"]} for w in wordList],
)

# Create an empty column of type string to store Gujarati translations
wordListDf["gujarati"] = ""

# Show some sample data
wordListDf.sample(n=3)

# %%
validationDf = pd.DataFrame()


def get_pandas_series_from_data(index: int) -> pd.Series:

    data_file_path = f"./data/{index}/data.json"

    if os.path.exists(data_file_path):
        with open(file=data_file_path) as f:
            data = json.load(f)

        if "extraCharacters" not in data.keys() or any(
            [(c in ["'", " ", ".", "-"]) for c in data["extraCharacters"]]
        ):
            raise Exception(f"Found issues with data at index {index}")
    else:
        data = {
            "englishTranslation": wordListDf.at[index, "english"],
            "puzzleSolution": [],
            "gujaratiDefinition": "",
            "extraCharacters": [],
            "credits": [],
        }

    return {
        "english_word": wordListDf.at[index, "english"],
        "english_word_replacement": data["englishTranslation"]
        if wordListDf.at[index, "english"] != data["englishTranslation"]
        else "",
        "gujarati_one_word_translation": "".join(data["puzzleSolution"]),
        "gujarati_definition": data["gujaratiDefinition"],
    }


logging.info("Processing data...")

validationDf = pd.DataFrame.from_records(
    data=[
        get_pandas_series_from_data(index) for index in range(0, wordListDf.shape[0])
    ],
)

logging.info("Saving CSV file locally...")

validation_file_path = "./data/validation.csv"
validationDf.to_csv(
    path_or_buf=validation_file_path, index=True, index_label="index", encoding="utf-16"
)

logging.info("Uploading CSV file to blob...")

if False:
    try:
        # Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#azure-storage-blob-blobserviceclient-get-blob-client
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=validation_file_path
        )

        # print("\nUploading to Azure Storage as blob:\n\t" + file.name)
        # logging.info("\nUploading to Azure Storage as blob:\n\t" + file.name)

        # Upload the created file
        with open(file=validation_file_path, mode="rb") as csv_file:
            # Function reference: https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-upload-blob
            blob_client.upload_blob(data=csv_file, overwrite=True)
    except Exception as ex:
        logging.exception(ex)

logging.info("Printing sample data to ipykernel console output...")

validationDf.sample(n=3)

# %%
