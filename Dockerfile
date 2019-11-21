# Use an official Python runtime as a parent image
FROM python:3.7.5
WORKDIR /app/data/topArtists
WORKDIR /app/data/topTracks
WORKDIR /app/data/library
WORKDIR /app/data/followed
ADD . /app
ADD ./data/topArtists/126614655TopArtists.json /app/data/topArtists
WORKDIR /app
RUN pip install --trusted-host pypi.python.org bottle spotipy pprint
CMD ["python3.7", "/app/runWebApp.py"]
