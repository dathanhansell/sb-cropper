from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import os
import re

credits_length = 48
theme_length = 53

def split(input_file, midpoints=None):
    clip = VideoFileClip(input_file)
    duration_in_sec = clip.duration
    end_time = duration_in_sec - credits_length

    start_time = theme_length
    if midpoints != None:
        for i in range(len(midpoints)):
            ffmpeg_extract_subclip(input_file, start_time, midpoints[i], targetname=f"a{i+1}.mkv")
            start_time = midpoints[i] + 2

        ffmpeg_extract_subclip(input_file, start_time, end_time, targetname=f"a{len(midpoints)+1}.mkv")
    else:
        ffmpeg_extract_subclip(input_file, start_time, end_time, targetname="a1.mkv")


def separate_titles(filename):
    # Find the part of the filename that contains the titles
    titles_part = re.search(r'(S\d*E\d*) (.*) \(1080p', filename)
    episode_part = titles_part.group(1)
    titles = titles_part.group(2).split(' & ')
  
    episode_number = int(re.search(r'E(\d*)', episode_part).group(1))
    season_number = re.search(r'S(\d*)', episode_part).group(1)
  
    new_filenames = []
    for title in titles:
        # Construct a new filename for each title
        new_filename = re.sub(r'S\d*E\d* .*( \(1080p.*)', r'S{}E{:02d} {}{}'.format(season_number, episode_number, title, r'\1'), filename)
        new_filenames.append(new_filename)
        # Increment the episode number for the next filename
        episode_number += 1
    return new_filenames

import shutil

def process_season(directory, output_directory):
    # Read the midpoint times from A.txt
    with open(os.path.join(directory, 'A.txt'), 'r') as file:
        midpoints = file.read().splitlines()

    # Get the list of episode files in the directory, sorted by filename
    episode_files = sorted([f for f in os.listdir(directory) if f.endswith('.mkv')])

    for i in range(len(episode_files)):
        filename = episode_files[i]
        print(filename)
        midpoint_times = [int(m) for m in midpoints[i].split()]

        if len(midpoint_times) == 1 and midpoint_times[0] == 0:
            print("Full length episode, need to trim intro and credits")
            split(os.path.join(directory, filename))
            new_filename = separate_titles(filename)[0]
            os.rename("a1.mkv", os.path.join(output_directory, new_filename))
        else:
            # Split the episode into parts
            split(os.path.join(directory, filename), midpoint_times)
            new_filenames = separate_titles(filename)
            # Rename the file and move it to the output directory
            for j, new_filename in enumerate(new_filenames):
                os.rename(f"a{j+1}.mkv", os.path.join(output_directory, new_filename))

process_season('sb/Season 4', 'out4')