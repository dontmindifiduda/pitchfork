# Pitchfork Album Reviews - Audio Data Analysis

This repository includes project files for an audio analysis of songs appearing in the top and bottom 10% of albums reviewed by Pitchfork from 1999-2017. Album review data were scraped from [Pitchfork](https://pitchfork.com/), and the full dataset can be [found on Kaggle](https://www.kaggle.com/nolanbconaway/pitchfork-data). The dataset includes a total of 18,393 album reviews.

Reviewed albums are assigned a score of 0.0-10.0, with 0 being the worst and 10.0 being the best. Albums were sorted based on score, and the top and bottom 10% of albums were extracted from the full dataset. Audio features for each song were obtained from [Spotify](https://www.spotify.com/us/).

Song data from each album in the top and bottom 10% was acquired using [Spotipy](https://spotipy.readthedocs.io/en/2.16.0/). Spotipy interfaces with the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) to allow for easy data access for analysis using Python. The code used to extract data using Spotify is included in this repo (extract-album-data.py), but please note that you will need to provide your own Spotify account access credentials to be able to use it. CSV files containing the extracted song audio data are also included in this repository.

Lyric data was also scraped from [Genius](https://genius.com/) using the BeatifulSoup library. I plan on completing an NLP analysis of lyrical data at a later date.

The results of the analysis are summarized in the following notebooks:
* song-analysis.ipynb - analyzes data at the song level
* aggregate-album-analysis.ipynb - analyzes data aggregated at the album level

Also, please take a look at the Medium article I wrote to accompany this analysis and give it some claps - Audio Analysis: How to Impress (or Disappoint) Pitchfork.  
