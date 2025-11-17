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

credentials = {
    "type": "service_account",
    "project_id": "devstackerp",
    "private_key_id": "3a7d1511ed3d81296b76f192794449c8145de068",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDp5iCeNNQl7WO3\nHwBSsnBazysuke/CjA9V5Pu+V9j0+PetgQgJbbHHkGzvC1W2vkXaZDD/veTn69Fq\n7VL2snWmna2OUg+j03j/zZtI2m8AHJNUoUvGKXAaYcUO1wrinGCPRrpcioNl8ZvO\nnJcfWuO/siPO0iT7L7xgYtAqd2RSHYGzY/9Q/2BdA2XtrPEu2VT79fVocJDwKZ9W\nnU9slh2aE7CDKDjn2ljiQXSrx6NkZyEdEdm/oaEd+2zvacx/zTpFpSzKCavj4h+y\n/iSgVZ0YKkc4QgUhWIQFUfq3/4Sk81K2CCjHSXSz0H4lh7qsO6yqoe1LU/IqwfJH\nabcVScFfAgMBAAECggEAVIqhb42YwLy1NhM2gq2MfsYyzXpiNud5A4rokzwdZy42\nF7hztzS29XL2bNCkApFzniRosYdpnYpW/1cYjaKjc726ZZ6zmHtvWMZwQjzxshCi\nEAzc3ptLsb11BJAllxL+s8rUwW4vYEGcF2nyFZs8hqVU3ASI6WGvrQcKRs8wq5zd\num2nnQuvVYVfCtGcp5qlcrDBgJV5EBy8H13mmAZSQo88UtK39KLc2qih2HFAmZnM\nJCjZj6EiJ57G4HuL1EF1pr6fIPzVgsYl6LFZ3MCr5qxrVYi8UxozdLVhka2jLLY1\nZSz+IOa4gm66nlYjdJoypmRFCXJrS4xVaTdah0DOQQKBgQD6sjAUFxNA1Fe0AdIc\nQdQnW9jcynLaXYSMqWZ/D7WsNnE7AVTnPuPuM/tY4jrxA4YNOUwVhJJxfRCgtWWt\nUwpBn0iFrh3oOWcLAi1fxoxj76b+mtzjuVEBSBmBvsIvnQJOpTWNfPp2OsnZwwz4\n3oGBeQ1bhCcTZK2rUE7tc7QAkwKBgQDu2PavXl8mhhzReeWlA/BftoaHWr0GfEaz\nyeVkqNHOlKPEl+Hmdb/YmEEhvcIHmC+a9UT4RdZdRRboPy1m2Z53OJn5VYuNuIil\nsStZO15xBEik1/gWeKUjTVX5HQqdoTccJpWINLpx95uNrZpLafsbMVUowdIgEipm\nYC9pEs7XhQKBgFtewmMwHdZNDkIPP9MIsxg9Q4cFSmMIHp1dyHua8C36Eb7dt2Io\n684PqBY3LiBVlnAPaAmXrgArAvpv4sUPNPfB5B7E3SWcdk/u1TbJGLX7zLOTIdrl\n2f5LlvBQ5FmSMhsT37bXzDl3J8Z0bq/t+OmFgzbNrahF035S4NFukDZ9AoGAQYNR\nZpjEEJUIooyE6NZDwH0YOVgyMO01l2rxeMK1iaxLn0jptYTmskpQ0yhxaBPeOuq7\nmD3PppWkyt9JXMSkKp9j3HgSZzUOhiQqd7dJGEbMhiqW6dL9uMklo8bLeqEVtKsA\nqPONkGUSTbIoeDcBoVvOt/cx44oYByyq1G9MPOECgYAPzv5Q93oiMAJlWVuzv1RV\nw9HpOD6pv5ryPMMd/q+qrWfJDz5wYoU4ccTRh0CzgERNKRPCy7zNMqCHRp0xTqBU\nyGMjJY6w1fvZYoqXVa2TVB3gXnb64v3guG2N8wHpK9qeAciN4G/IrCy5a9IQv45o\nSF/AbO/1i7rBpBtwfDuhZQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "itdevstack@devstackerp.iam.gserviceaccount.com",
    "client_id": "100362920078189694738",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/itdevstack%40devstackerp.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}


#---------------------------- Funciones generales --------------------------------

def upload_to_google_drive(bytes_data, file_name, folder_id, service_account_info):

  credentials_pdf = service_account.Credentials.from_service_account_info(service_account_info,scopes=['https://www.googleapis.com/auth/drive'])

  # Build the Drive service
  drive_service = build('drive', 'v3', credentials=credentials_pdf)

  # Create BytesIO object from bytes_data
  bytes_io = BytesIO(bytes_data)
  # File metadata
  file_metadata = {
      'name': file_name,
      'parents': [folder_id]
  }

  try:
    # Create a media object from bytes_data
      media = MediaIoBaseUpload(BytesIO(bytes_data), mimetype='application/pdf')

  
      # Upload file to Google Drive
      file = drive_service.files().create(
          body=file_metadata,
          media_body=media,
          fields='id'
      ).execute()
        
      file_id=file.get('id')

      return file_id

  except Exception as e:
      st.write("File not compatible")
      st.write(str(e))

      file_id="https://drive.google.com/file/d/1hD5g5tymJLDnT-gh4g7NIXiOyvswqqNm/view?usp=sharing"

def read_file_googledrive(credentials,file_id):

    try:
        credentials_pdf = service_account.Credentials.from_service_account_info(credentials, scopes=['https://www.googleapis.com/auth/drive'])

        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=credentials_pdf)

        # Request the file content
        file_content = drive_service.files().get_media(fileId=file_id).execute()

        # Convert bytes content to string
        text_content = file_content.decode('utf-8')  # Assuming UTF-8 encoding
        text_content = json.loads(file_content)
         
    except Exception as e:
        print(f"Error: {str(e)}")
        print("No fue posible leer el file")
        #st.write(f"Error: {str(e)}")
        text_content=[]
    
    return text_content

def generate_barcode(number, dpi=600):
    # Ensure the number is a 12-digit string
    number = str(number).zfill(12)
    
    # Generate barcode with high DPI
    barcode = EAN13(number, writer=ImageWriter())
    
    # Create buffer to save barcode image
    buffer = io.BytesIO()
    barcode.write(buffer, options={"dpi": dpi})
    buffer.seek(0)
    
    # Save barcode image to file
    with open("barcode.png", "wb") as f:
        f.write(buffer.getvalue())
    
    barcode_filename = "barcode.png"

    # Create PDF with high definition barcode image
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(524, 262))
    c.drawImage(barcode_filename, 0, 0, width=523, height=261.5)  # Adjust the position and size as needed
    c.showPage()
    c.save()
    
    pdf_bytes = pdf_buffer.getvalue()

    return barcode_filename, barcode, pdf_bytes

@st.experimental_dialog("New experiment")
def new_value(master_data_dict):

    synthesis_methods = st.selectbox(
        "Synthesis methods",
        ("Hydrothermal", "Microwave"),index=None,placeholder="Select synthesis method...")
    
    variables = read_file_googledrive(credentials,'1k-Gnh-xUFUXej14D6ABMhGeGe8dXGxyT')

    if synthesis_methods:

        with st.form("my_form", clear_on_submit=True):
            timestamp = int(time.time())
            timestamp_str = str(timestamp).zfill(12)  # Pad the timestamp to ensure it's 12 digits
            barcode_path, barcode, pdf_bytes = generate_barcode(timestamp_str)
            barcode = str(barcode).split("'")[0]
            image = Image.open(barcode_path)

            if 'barcode' not in st.session_state:
                st.session_state['barcode'] = barcode
            if 'pdf_bytes' not in st.session_state:
                st.session_state['pdf_bytes'] = pdf_bytes
            
            responses = {}

            # Iterate over variables and create a text input for each
            for i in variables:
                if i['variable_type']=='Independant': # and synthesis_methods in i["synthesis_methods"]:
                    if synthesis_methods in i['synthesis_methods']:
                        responses[i["variable_name"]] = st.text_input(i["variable_name"], "" , key=i["variable_name"])

            purification_methods = st.selectbox(
                "Purification Methods",
                ("Filter 0.2 um", "Filter 0.2 um + Ultracentrifugation", "Filter 0.2 um + Ultracentrifugation+ dialysis"),index=None,placeholder="Select purification method...")
              
            submitted = st.form_submit_button("Submit form", use_container_width=True)

            st.image(image, caption='Generated Barcode')

        if submitted:

            file_id=upload_to_google_drive(st.session_state.pdf_bytes, st.session_state.barcode, '1reoksQe_LScoGunjAbHmLnCtu3BpjPML', credentials)
            file_id="https://drive.google.com/file/d/"+str(file_id)
            responses['Synthesis_methods']=synthesis_methods
            responses['Purification_methods']=purification_methods
            responses['File']=file_id
            responses['Barcode']=st.session_state.barcode
            master_data_dict.append(responses)
            update_text_file(credentials, '1Qz4keZrXh8jufcqKG0bN1aj-QycKZ-iR', '1DI-ZNSX88hmbdGW8-Nb1fOKIsTHyEEOU', 'cr_streamlit_prod.inventory_management.master_data', master_data_dict)
            st.session_state['barcode'] = barcode
            st.rerun()

    else:
        st.write("No synthesis method has been selected ")

def update_text_file(credentials, folder_id, file_id, file_name, new_content):
    try:
        print("Empezando a subir a Google Drive")
        
        # Convert list of dictionaries to JSON string
        json_str = json.dumps(new_content, indent=4, ensure_ascii=False)
        
        # Encode the string into bytes
        bytes_data = json_str.encode('utf-8')

        # Create credentials from service account info
        credentials_pdf = service_account.Credentials.from_service_account_info(credentials)

        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=credentials_pdf)

        # Create file metadata
        file_metadata = {
            'name': file_name,
            'addParents': [folder_id]  # Add the file to the specified folder
        }

        # Create media object for uploading file content
        media = MediaIoBaseUpload(BytesIO(bytes_data), mimetype='text/plain')
        
        # Update the file
        file = drive_service.files().update(fileId=file_id, body=file_metadata, media_body=media).execute()

        print(f"File with ID '{file_id}' updated successfully")

    except Exception as e:
        print("Error updating file:", e)        

@st.experimental_dialog("Update experiment", width="large")
def complete_value(master_data_dict):

    def filter_by_barcode(barcode):
        return [entry for entry in master_data_dict if entry["Barcode"] == barcode]

    variables = read_file_googledrive(credentials,'1k-Gnh-xUFUXej14D6ABMhGeGe8dXGxyT')
    
    search_barcode_form = st.text_input("Search by barcode", key="search_barcode_form")
    filtered_data = filter_by_barcode(search_barcode_form)

    if search_barcode_form:

        if filtered_data:
            
            with st.form("my_form", clear_on_submit=False):
                values_from_dict1 = filtered_data[0]

                col1, col2 = st.columns(2)

                input_values = {}

                if values_from_dict1['Purification_methods'] == "Filter 0.2 um":
                    index=0
                elif values_from_dict1['Purification_methods'] == "Filter 0.2 um + Ultracentrifugation":
                    index=1
                elif values_from_dict1['Purification_methods'] == "Filter 0.2 um + Ultracentrifugation+ dialysis":
                    index=2
                

                if values_from_dict1['Synthesis_methods'] == "Hydrothermal":
                    index2=0
                elif values_from_dict1['Synthesis_methods'] == "Microwave":
                    index2=1

                with col1:
                    input_values["Synthesis_methods"] = st.selectbox("Synthesis Methods",("Hydrothermal","Microwave"),index=index2)
                    input_values["Purification_methods"] = st.selectbox("Purification Methods",("Filter 0.2 um", "Filter 0.2 um + Ultracentrifugation", "Filter 0.2 um + Ultracentrifugation+ dialysis"),index=index)

                for variable in variables:
                    if variable["variable_type"] == "Independant":
                        
                        variable_name = variable["variable_name"]
                        variable_description = variable["variable_description"]

                        # Get the corresponding value from dict1
                        value = values_from_dict1.get(variable_name, "")

                        with col1:

                            # Create a text input in Streamlit
                            input_values[variable_name] = st.text_input(label=f"{variable_name}", value=value, help=variable_description, key=variable_name)
                  
                    elif variable["variable_type"] == "Dependant":
                        variable_name = variable["variable_name"]
                        variable_description = variable["variable_description"]

                        # Get the corresponding value from dict1
                        value = values_from_dict1.get(variable_name, "")

                        with col2:

                            # Create a text input in Streamlit
                            input_values[variable_name] = st.text_input(label=f"{variable_name}", value=value, help=variable_description)

                submitted = st.form_submit_button("Submit form", use_container_width=True, type="primary")
                    
                if submitted:
                    input_values = {k: v for k, v in input_values.items() if v != ""}

                    for entry in master_data_dict:
                        if entry["Barcode"] == search_barcode_form:
                            entry.update(input_values)
                        
                    update_text_file(credentials, '1Qz4keZrXh8jufcqKG0bN1aj-QycKZ-iR', '1DI-ZNSX88hmbdGW8-Nb1fOKIsTHyEEOU', 'cr_streamlit_prod.inventory_management.master_data', master_data_dict)

                    st.rerun()






        else:
            st.write("No match found.")
    
        
        timestamp = int(search_barcode_form)
        timestamp_str = str(timestamp).zfill(13)
        barcode_path, barcode, pdf_bytes = generate_barcode(timestamp_str)
        barcode = str(barcode).split("'")[0]
        image = Image.open(barcode_path)

        st.image(image, caption='Generated Barcode', use_column_width=True)


    else:
        st.write("No value typed")

@st.experimental_dialog("Delete experiment")
def delete_value(master_data_dict,search_barcode):

    with st.form("my_form", clear_on_submit=False):
        
        col1d, col2d = st.columns(2)

        with col1d:
            delete=st.form_submit_button("Delete ", use_container_width=True, type="primary")

            if delete:
                master_data_dict = [entry for entry in master_data_dict if entry['barcode'] != str(search_barcode)]
                update_text_file(credentials, '1Qz4keZrXh8jufcqKG0bN1aj-QycKZ-iR', '1DI-ZNSX88hmbdGW8-Nb1fOKIsTHyEEOU', 'cr_streamlit_prod.inventory_management.master_data', master_data_dict)
                st.rerun()


        with col2d:
            do_not_delete=st.form_submit_button("Do not delete ", use_container_width=True, type="secondary")
            if do_not_delete:
                st.rerun()

#---------------------------- Codigo general --------------------------------

st.title("Lilliput Inventory Management")

description="""

### Overview
The Inventory Module streamlines tracking and managing experiments in our chemical lab. Each experiment is tagged with a unique barcode containing key information about its conditions and parameters.

### Key Features

1. **Barcode Generation:**
   - Automatically generate and assign unique barcodes to experiments.

2. **Experiment Tracking:**
   - Scan barcodes to access detailed experiment info and key parameters.

3. **Data Management:**
   - Securely store all experiment data in a centralized database.
   - Maintain a historical record for reference.

4. **User-Friendly Interface:**
   - Easy navigation with quick search and filter options.

5. **Lab Equipment Integration:**
   - Automatically record and tag experiments with barcodes.
   - Real-time data capture and updates.

6. **Reporting and Analysis:**
   - Generate reports and analyze experiment trends and patterns.

### Benefits

- **Accuracy:** Reduces manual errors and ensures precise data tracking.
- **Efficiency:** Streamlines documentation and retrieval processes.
- **Organization:** Centralized storage improves lab management.
- **Insights:** Supports data analysis for research advancements.

"""

st.markdown(description)


st.markdown("---")

master_data_dict = read_file_googledrive(credentials,'1DI-ZNSX88hmbdGW8-Nb1fOKIsTHyEEOU')
master_data_df = pd.DataFrame(master_data_dict)



if st.button("Insert a new value (independent variables)", use_container_width=True):
    try:
        del st.session_state['barcode']
        del st.session_state['pdf_bytes']
    except:
        print("nothing")
    
    new_value(master_data_dict)

if st.button("Update a value (dependent variables)", use_container_width=True):
    try:
        del st.session_state['barcode']
    except:
        print("nothing")
    
    complete_value(master_data_dict)


search_barcode = st.text_input("Search by barcode", "")

try:
    # Filter the dataframe based on the input
    if search_barcode:
        filtered_df = master_data_df[master_data_df['barcode'].str.contains(search_barcode)]
        barcode_delete= st.button("Delete entry: "+str(search_barcode), use_container_width=True, type="primary")
        if barcode_delete:
            delete_value(master_data_dict, search_barcode)

        
    else:
        filtered_df = master_data_df
except:
    filtered_df = master_data_df


try:
    cols_to_move = ['Barcode', 'File']

    # Reorder the columns
    cols = cols_to_move + [col for col in filtered_df.columns if col not in cols_to_move]
    filtered_df = filtered_df[cols]

    master_data_df_edit = st.data_editor(filtered_df, num_rows="fixed", hide_index=True, use_container_width=True,
        column_config={
            "File": st.column_config.LinkColumn(
                "Barcode file", display_text="Open PDF"
            ),
        })

except:
    st.write("No data to show")
