"""Data Entry into MongoDB"""

def docs_from_df(df, model):
    """Load a list of documents from a table."""
    return [model.from_json(row.to_json()) for _,row in df.iterrows()]
