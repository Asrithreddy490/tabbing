from imports import* 


# core/utils.py
def save_uploaded_file(uploaded_file, prefix="__temp__"):
    """Save an uploaded file to a temp path and return the path."""
    temp_path = f"{prefix}_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path


def clean_blank_and_convert_to_numeric(first_data):    
    exclude_cols = ['date','markers']
    cols_to_convert = first_data.columns.difference(exclude_cols)
    first_data[cols_to_convert] = first_data[cols_to_convert].replace({' ':np.nan,'':np.nan})
    first_data[cols_to_convert] = first_data[cols_to_convert].apply(pd.to_numeric,errors='coerce')
    return first_data

