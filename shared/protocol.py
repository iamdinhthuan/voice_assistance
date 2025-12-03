# Message Types
MSG_START_LISTENING = "start_listening"
MSG_AUDIO_CHUNK = "audio_chunk"
MSG_END_SPEECH = "end_speech" # Optional, if client detects end of speech (e.g. VAD on client)
MSG_PLAY_AUDIO = "play_audio"
MSG_TEXT_RESPONSE = "text_response" # Optional, to show text on client if needed
MSG_ERROR = "error"

# Keys
KEY_TYPE = "type"
KEY_DATA = "data"
KEY_AUDIO = "audio" # For binary audio data, usually sent as separate binary message or base64
