# %%
print("Installing dependencies...")
# !apt-get update -qq && apt-get install -qq libfluidsynth2 fluid-soundfont-gm build-essential libasound2-dev libjack-dev
# %pip install -qU pyfluidsynth pretty_midi

# %pip install -qU magenta

# Hack to allow python to pick up the newly-installed fluidsynth lib.
# This is only needed for the hosted Colab environment.
# import ctypes.util
# orig_ctypes_util_find_library = ctypes.util.find_library
# def proxy_find_library(lib):
#   if lib == 'fluidsynth':
#     return 'libfluidsynth.so.1'
#   else:
#     return orig_ctypes_util_find_library(lib)
# ctypes.util.find_library = proxy_find_library

print("Importing libraries and defining some helper functions...")
# from google.colab import files

import magenta
import note_seq
import tensorflow

print("🎉 Done!")
print(magenta.__version__)
print(tensorflow.__version__)

# %%
print("Copying checkpoint from GCS. This will take less than a minute...")
# This will download the mel_2bar_big checkpoint. There are more checkpoints that you
# can use with this model, depending on what kind of output you want
# See the list of checkpoints: https://github.com/magenta/magenta/tree/main/magenta/models/music_vae#pre-trained-checkpoints
# !gsutil -q -m cp -R gs://download.magenta.tensorflow.org/models/music_vae/colab2/checkpoints/mel_2bar_big.ckpt.* /content/

# Import dependencies.
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel

# Initialize the model.
print("Initializing Music VAE...")
music_vae = TrainedModel(
    configs.CONFIG_MAP["cat-mel_2bar_big"],
    batch_size=4,
    checkpoint_dir_or_path="/content/mel_2bar_big.ckpt",
)

print("🎉 Done!")

# %%
generated_sequences = music_vae.sample(n=2, length=80, temperature=1.0)

for ns in generated_sequences:
    # print(ns)
    note_seq.plot_sequence(ns)
    note_seq.play_sequence(ns, synth=note_seq.fluidsynth)

# %%
# # We're going to interpolate between the Twinkle Twinkle Little Star
# # NoteSequence we defined in the first section, and one of the generated
# # sequences from the previous VAE example

# # How many sequences, including the start and end ones, to generate.
# num_steps = 8;

# # This gives us a list of sequences.
# note_sequences = music_vae.interpolate(
#       twinkle_twinkle,
#       teapot,
#       num_steps=num_steps,
#       length=32)

# # Concatenate them into one long sequence, with the start and
# # end sequences at each end.
# interp_seq = note_seq.sequences_lib.concatenate_sequences(note_sequences)

# note_seq.play_sequence(interp_seq, synth=note_seq.fluidsynth)
# note_seq.plot_sequence(interp_seq)

# %% [markdown]
# RNN

# %%
# print('Downloading model bundle. This will take less than a minute...')
# note_seq.notebook_utils.download_bundle('basic_rnn.mag', '/content/')

# # Import dependencies.
# from magenta.models.melody_rnn import melody_rnn_sequence_generator
# from magenta.models.shared import sequence_generator_bundle
# from note_seq.protobuf import generator_pb2
# from note_seq.protobuf import music_pb2

# # Initialize the model.
# print("Initializing Melody RNN...")
# bundle = sequence_generator_bundle.read_bundle_file('/content/basic_rnn.mag')
# generator_map = melody_rnn_sequence_generator.get_generator_map()
# melody_rnn = generator_map['basic_rnn'](checkpoint=None, bundle=bundle)
# melody_rnn.initialize()

# print('🎉 Done!')

# %%
# # Model options. Change these to get different generated sequences!

# input_sequence = twinkle_twinkle # change this to teapot if you want
# num_steps = 128 # change this for shorter or longer sequences
# temperature = 1.0 # the higher the temperature the more random the sequence.

# # Set the start time to begin on the next step after the last note ends.
# last_end_time = (max(n.end_time for n in input_sequence.notes)
#                   if input_sequence.notes else 0)
# qpm = input_sequence.tempos[0].qpm
# seconds_per_step = 60.0 / qpm / melody_rnn.steps_per_quarter
# total_seconds = num_steps * seconds_per_step

# generator_options = generator_pb2.GeneratorOptions()
# generator_options.args['temperature'].float_value = temperature
# generate_section = generator_options.generate_sections.add(
#   start_time=last_end_time + seconds_per_step,
#   end_time=total_seconds)

# # Ask the model to continue the sequence.
# sequence = melody_rnn.generate(input_sequence, generator_options)

# note_seq.plot_sequence(sequence)
# note_seq.play_sequence(sequence, synth=note_seq.fluidsynth)

# %%
# import magenta
# from magenta.models.music_vae import configs
# from magenta.models.music_vae.trained_model import TrainedModel

# # Load the MusicVAE model
# config = configs.CONFIG_MAP['cat-mel_2bar_big']
# model = TrainedModel(config, 10, checkpoint_dir_or_path='./checkpoint')

# # Generate a new MIDI file
# generated_sequence = model.generate(length=16, temperature=1.0)
# magenta.music.sequence_proto_to_midi_file(generated_sequence, 'generated.mid')

# %%
# from music21 import *

# # Create a new MIDI file
# mf = midi.translate.music21ObjectToMidiFile(stream.Score())

# # Create a new piano track
# t = midi.MidiTrack(1)
# mf.tracks.append(t)

# # Add notes to the track
# for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
#     n = note.Note(note)
#     n.duration.type = 'whole'
#     t.append(n.midiNote)

# # Save the MIDI file to disk
# mf.open('scale.mid', 'wb')
# mf.write()
# mf.close()

# %%
# from music21 import *

# # Create a new Stream
# s = stream.Stream()

# # Add some notes to the Stream
# s.append(note.Note('C4'))
# s.append(note.Note('D4'))
# s.append(note.Note('E4'))
# s.append(note.Note('F4'))

# # Add a repeat structure
# s.append(bar.Barline('double'))

# # Save the stream to a MIDI file
# mf = midi.translate.music21ObjectToMidiFile(s)
# mf.open("bg_music.mid", 'wb')
# mf.write()
# mf.close()


# %%
# from midiutil.MidiFile import MIDIFile

# # Create the MIDI file
# midi = MIDIFile(1)

# # Add a track to the file
# track = 0
# time = 0
# midi.addTrackName(track, time, "Background Music")
# midi.addTempo(track, time, 120)

# # Add some notes to the track
# channel = 0
# pitch = 60
# time = 0
# duration = 1
# volume = 100
# midi.addNote(track, channel, pitch, time, duration, volume)

# # Save the MIDI file
# with open("bg_music.mid", "wb") as output_file:
#     midi.writeFile(output_file)


# %%
# import mido
# from mido import Message

# # Create a new MIDI file
# mid = mido.MidiFile()

# # Create a new track
# track = mido.MidiTrack()
# mid.tracks.append(track)

# # Add some notes to the track
# track.append(Message('note_on', note=60))
# track.append(Message('note_off', note=60, time=512))
# track.append(Message('note_on', note=64))
# track.append(Message('note_off', note=64, time=512))

# # Save the MIDI file
# mid.save('bg_music1.mid')

# %%
# from moviepy.editor import *

# # Load the image
# image = ImageClip("image.jpg")

# # Load the background music
# music = AudioFileClip("bg_music.mp3")

# # Create the final video by concatenating the image and music
# final_video = concatenate_videoclips([image, music])

# # Save the final video
# final_video.write_videofile("video_with_image_and_music.mp4")
