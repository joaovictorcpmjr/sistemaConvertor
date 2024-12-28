import os
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import ctypes
import threading
from colorama import Fore, Style
from pathlib import Path
import sys
import zipfile
from datetime import datetime


def logConv():
