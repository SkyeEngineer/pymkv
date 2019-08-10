# sheldon woodward
# 2/25/2018

"""MKVTrack Class"""

import json
from os.path import expanduser, isfile
import subprocess as sp

from pymkv.Verifications import verify_supported
from pymkv.ISO639_2 import is_ISO639_2


class MKVTrack:
    """A class that represents an MKV track such as video, audio, or subtitles.

        MKVTracks can be added to an MKVFile. MKVTracks can be video, audio, or subtitle tracks. The only required
        argument is path which gives the path to a track file. Tracks can be either standalone track files or can 
        represent a single track within an MKV file. The MKVTrack class can be added to an MKVFile and will be 
        included when the MKV is muxed.

        Attributes
        ----------
        default_track : {False, True}
            Flag to set the track as the default track for its media type.
        file_path
        forced_track : {False, True}
            Flag to set the track as a forced track.
        language
        mkvmerge_path : str
            The path to the mkvmerge binary.
        no_chapters : {False, True}
            Flag to exclude chapters from the mux output.
        no_global_tags : {False, True}
            Flag to exclude global tags from the mux output.
        no_track_tags : {False, True}
            Flag to exclude track tags from the mux output.
        no_attachments : {False, True}
            Flag to exclude attachments from the mux output.
        tags
        track_codec
        track_id
        track_name : str
            The name that will be geiven to the track in the mux output.
        track_type
    """
    def __init__(self, file_path, track_id=0, track_name=None, language=None, default_track=False, forced_track=False):
        """MKVTrack constructor method.

        The MKVTrack constructor method used to initalize a new track.

        Parameters
        ----------
        file_path : str
            Path to the track file. This can also be an MKV where the `track_id` is the track represented in the MKV.
            This is the only required argument.
        track_id : int, optional
            The id of the track to be used in the file. `track_id` only needs to be set when importing a specific 
            track from an MKV. In this case, you can specify `track_id` to indicate which track from the MKV should 
            be imported. If not set, it will import the first track.
        track_name : str, optional
            The name that will be given to the track when muxed into a file.
        language : str, optional
            The language of the track. It must be an ISO639-2 language code.
        default_track : {False, True}
            Determines if the track should be the default track of its type when muxed into an MKV file.
        forced_track : {False, True}
            Determines if the track should be a forced track when muxed into an MKV file.
        """
        # track info
        self._track_codec = None
        self._track_type = None

        # base
        self.mkvmerge_path = 'mkvmerge'
        self._file_path = None
        self.file_path = file_path
        self._track_id = None
        self.track_id = track_id

        # flags
        self.track_name = track_name
        self._language = None
        self.language = language
        self._tags = None
        self.default_track = default_track
        self.forced_track = forced_track

        # exclusions
        self.no_chapters = False
        self.no_global_tags = False
        self.no_track_tags = False
        self.no_attachments = False

    def __repr__(self):
        return repr(self.__dict__)

    @property
    def file_path(self):
        """str: The path to the track or MKV file.
        
        Setting `file_path` will verify the passed in file is supported 
        by mkvmerge and set the track_id to 0. It is recomended to 
        recreate MKVTracks instead of setting their file path after 
        instantiation.
        """
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        file_path = expanduser(file_path)
        if not verify_supported(file_path):
            raise ValueError('"{}" is not a supported file')
        self._file_path = file_path
        self.track_id = 0

    @property
    def track_id(self):
        """int: The ID of the track. Should be left at 0 unless 
        extracting a specific track from an MKV.

        Setting `track_id` will check that the ID passed in exists in 
        the file. It will then look at the new track and set the codec 
        and track type.
        """
        return self._track_id

    @track_id.setter
    def track_id(self, track_id):
        info_json = json.loads(sp.check_output([self.mkvmerge_path, '-J', self.file_path]).decode())
        if not 0 <= track_id < len(info_json['tracks']):
            raise IndexError('track index out of range')
        self._track_id = track_id
        self._track_codec = info_json['tracks'][track_id]['codec']
        self._track_type = info_json['tracks'][track_id]['type']

    @property
    def language(self):
        """str: The language of the track. It will be an ISO-639 
        language code.

        Setting `language` will verify that the passed in language is 
        an ISO-639 language code.
        """
        return self._language

    @language.setter
    def language(self, language):
        if language is None or is_ISO639_2(language):
            self._language = language
        else:
            raise ValueError('not an ISO639-2 language code')

    @property
    def tags(self):
        """str: The tags file to include with the track.
        
        Setting `tags` will check that the file path passed in exists.
        """
        return self._tags

    @tags.setter
    def tags(self, file_path):
        if not isinstance(file_path, str):
            raise TypeError('"{}" is not of type str'.format(file_path))
        file_path = expanduser(file_path)
        if not isfile(file_path):
            raise FileNotFoundError('"{}" does not exist'.format(file_path))
        self._tags = file_path

    @property
    def track_codec(self):
        """str: The codec of the track such as h264 or AAC."""
        return self._track_codec

    @property
    def track_type(self):
        """The type of track such as video or audio."""
        return self._track_type
