import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import json
import pandas as pd
import re
import numpy as np
from streamlit_dynamic_filters import DynamicFilters
from barcode import EAN13
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import time
import io


import streamlit.components.v1 as components
import pandas as pd
import base64
import json


#st.cache_data.clear()
st.set_page_config(
  page_title="Lilliput Inventory Management",
  page_icon="🔬",
  layout="wide",
)

#---------------------------- Variables generales --------------------------------

