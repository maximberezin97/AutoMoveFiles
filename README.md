# AutoMoveFiles
A Python script that uniquely handles files/directories based on file/content types.
Target content includes audio (mp3, m4a, aac, flac), video (mkv, mp4, wmv, avi, mov), and comic (cbr, cbx, pdf).

Audio has cover artwork embedded into ID3 retrieved from Google Custom Search API.
Video sorted by type (movie, television, home video) and TV show & season, if applicable.
Comic renamed to custom format based on regex.

All content is copied to a temp location, handled, and moved to destination.
For personal use only. All content is copyright-free.
