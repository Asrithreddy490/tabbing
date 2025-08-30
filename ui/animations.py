# animations.py
import requests
from streamlit_lottie import st_lottie
import streamlit as st

# ------------------------
# Helper to load lottie animations
# ------------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ------------------------
# Preload some animations
# ------------------------
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jbrw3hcz.json")
lottie_processing = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json")
lottie_upload = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_z9ed2jna.json")
lottie_error = load_lottieurl("https://assets2.lottiefiles.com/private_files/lf30_jtkhrafu.json")

# ------------------------
# Functions to display animations
# ------------------------
def show_success():
    if lottie_success:
        st_lottie(lottie_success, speed=1, width=200, height=200, key="anim_success")

def show_processing():
    if lottie_processing:
        st_lottie(lottie_processing, speed=1, width=300, height=200, key="anim_processing")

def show_upload():
    if lottie_upload:
        st_lottie(lottie_upload, speed=1, width=300, height=200, key="anim_upload")

def show_error():
    if lottie_error:
        st_lottie(lottie_error, speed=1, width=200, height=200, key="anim_error")
