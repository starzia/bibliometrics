def get_from_row(row, column_idx):
    """get the value from the specified column index, or return None if it's empty"""
    if (len(row) <= column_idx) or row[column_idx] == "":
        return None
    return row[column_idx]