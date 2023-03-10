from typing import Dict, Any, Optional
import pandas as pd

def import_csv_as_df(
        filename: str, 
        dir: Optional[str] = None, 
        index_col_name: Optional[str] = None, 
        index_rename: Optional[str] = None,
        index_is_datetime: bool = False, 
        converter: Optional[Dict[str, Any]] = None, 
        column_types: Optional[Dict[str, Any]] = None, 
        column_rename: Optional[Dict[str, str]] = None,
        ) -> pd.DataFrame:
    
    """ Imports CSV as dataframe. Enables user to specify which column to make index and if type is datetime.
    
    Args:
        filename: Filename of the CSV
        dir: Directory of the CSV
        index_name: Name of column to make index
        index_is_datetime: Optional set index to datetime
        converter: specify dictionary for {column name : converter function}
        column_type: specify dictionary of {column name : dtype}. Uses ',' as thousands seperator
        column_rename: provide dictionary of renamed values
        
    Returns:
        df: Dataframe of CSV  
    """
    
    # Build filepath
    if dir == None:
        path = filename
    else:
        path = dir + filename

    # Import CSV
    df = pd.read_csv(path, index_col = index_col_name, converters = converter, dtype = column_types, thousands = ',')
    
    if index_is_datetime == True:
        df.index = pd.to_datetime(df.index)   
        
    # Rename Columns & index
    if column_rename:
        df = df.rename(columns = column_rename)

    if index_rename:
        df.index.name = index_rename
    
    return df

