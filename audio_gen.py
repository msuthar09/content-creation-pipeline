import os
import pathlib
import magenta
import note_seq
import tensorflow
from dotenv import load_dotenv
from pydub import AudioSegment
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel

# Load environment variables from `.env` file
load_dotenv(verbose=True, override=True)

# print('Copying checkpoint from GCS. This will take less than a minute...')
# # This will download the mel_2bar_big checkpoint. There are more checkpoints that you
# # can use with this model, depending on what kind of output you want
# # See the list of checkpoints: https://github.com/magenta/magenta/tree/main/magenta/models/music_vae#pre-trained-checkpoints
# !gsutil -q -m cp -R gs://download.magenta.tensorflow.org/models/music_vae/colab2/checkpoints/ ./pre-trained/

pre_trained_paths = pathlib.Path("./pre-trained/checkpoints/").glob("*.index")

for i, pre_trained_path in enumerate(pre_trained_paths):
    # Initialize the model.
    print(f"{i}. Initializing Music VAE...")
    try:
        config = "cat-" + pathlib.Path(pre_trained_path).stem.split(".")[0]
        checkpoint_path = os.path.splitext(pre_trained_path)[0]
        music_vae = TrainedModel(
            configs.CONFIG_MAP[config],  # 'cat-mel_2bar_big'
            batch_size=4,
            checkpoint_dir_or_path="./" + checkpoint_path,
        )

        generated_sequences = music_vae.sample(n=4, length=500, temperature=1.5)

        for n, ns in enumerate(generated_sequences):
            # print(ns)
            note_seq.plot_sequence(ns)
            # note_seq.play_sequence(ns, synth=note_seq.fluidsynth)
            note_seq.note_sequence_to_midi_file(
                ns, f"./bg-music/{config}_generated_{n}.mid"
            )

            # Read MIDI File
            sound = AudioSegment.from_file(
                f"./bg-music/{config}_generated_{n}.mid", format="mid"
            )

            # simple export
            file_handle = sound.export(
                f"./bg-music/{config}_generated_{n}.mp3", format="mp3"
            )
    except KeyError as ke:
        print(f"KeyError for {ke}")

print("🎉 Done!")
