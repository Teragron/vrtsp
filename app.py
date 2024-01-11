import logging
from pathlib import Path
from typing import Dict, Optional, cast

import av
import cv2
import streamlit as st
from aiortc.contrib.media import MediaPlayer
from streamlit_webrtc import WebRtcMode, WebRtcStreamerContext, webrtc_streamer

from sample_utils.download import download_file
from sample_utils.turn import get_ice_servers

HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)

MEDIAFILES: Dict[str, Dict] = {
    "insert_your_own_rtsp_url": {
        "url": "insert_your_own_rtsp_url",
        "type": "video",
    },
}
media_file_label = st.radio("Select a media source to stream", tuple(MEDIAFILES.keys()))
media_file_info = MEDIAFILES[cast(str, media_file_label)]
if "local_file_path" in media_file_info:
    download_file(media_file_info["url"], media_file_info["local_file_path"])


def create_player():
    if "local_file_path" in media_file_info:
        return MediaPlayer(str(media_file_info["local_file_path"]), options={"buffer_size": 4096})
    else:
        return MediaPlayer(media_file_info["url"])

key = f"media-streaming-{media_file_label}"
ctx: Optional[WebRtcStreamerContext] = st.session_state.get(key)


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:


    img = frame.to_ndarray(format="bgr24")

    # Duplicate the frame
    img_duplicate = cv2.hconcat([img, img])

    

    # Display the duplicated frames side by side
    return av.VideoFrame.from_ndarray(img_duplicate, format="bgr24")


webrtc_streamer(
    key=key,
    mode=WebRtcMode.RECVONLY,
    rtc_configuration={"iceServers": get_ice_servers()},
    media_stream_constraints={
        "video": media_file_info["type"] == "video",
        "audio": media_file_info["type"] == "audio",
    },
    player_factory=create_player,
    video_frame_callback=video_frame_callback,
)
