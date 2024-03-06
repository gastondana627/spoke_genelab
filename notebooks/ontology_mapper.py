"""
This module provides functions to map terms to concepts in an ontology.

Author: Peter W Rose (pwrose@ucsd.edu)
Created: 2024-03-03
"""
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import inflection

def map_ontology(df, input_col, output_col, ontology, apikey):
    """
    Map terms from a DataFrame column to concepts in an ontology.

    Parameters
    ----------
    df (pandas.DataFrame): The DataFrame containing the data to be mapped.
    input_col (str): The name of the column in `df` containing terms to be mapped.
    output_col (str): The name of the column in `df` to store the mapped ontology concepts.
    ontology (Ontology): Name of the ontology

    Returns
    -------
    pandas.DataFrame: The DataFrame with mapped ontology concepts in the `output_col` column.

    Notes
    -----
    Make sure to set the `BIOPORTAL_API_KEY` variable in the .env file.
    Create a BioPortal account to get an API key.

    Example
    -------
    >>> import os
    >>> import pandas as pd
    >>> from dotenv import load_dotenv
    >>> import ontology_mapper
    >>>
    >>> # get BioPortal API key
    >>> load_dotenv(<path to .env file>)
    >>> apikey = os.getenv("BIOPORTAL_API_KEY")
    >>>
    >>> # Sample DataFrame (may contain other columns)
    >>> df = pd.DataFrame({"terms": ["liver", "brain", "zygote"]})
    >>> mapped_df = ontology_mapper.map_ontology(df, "terms", "mapped_concepts", "UBERON", apikey)
    >>> print(mapped_df)
            terms     mapped_concepts
    0       liver     UBERON:0002107
    1       brain     UBERON:0000955
    2      zygote     CL:0010017
    
    """

    # convert to lowercase and map to ontology
    df["__lower__"] = df[input_col].str.lower()
    df = map_column(df, "__lower__", ontology, apikey)

    # remove anatomical positions and map to ontology
    df["__nopos__"] = df["__lower__"].str.replace("left " , "")
    df["__nopos__"] = df["__nopos__"].str.replace("right ", "")
    df["__nopos__"] = df["__nopos__"].str.replace("medial ", "")
    df["__nopos__"] = df["__nopos__"].str.replace("peripheral ", "")
    df = map_column(df, "__nopos__", ontology, apikey)

    # convert plural to singular terms and map to ontology
    df["__singular__"] = df["__lower__"].apply(lambda x: inflection.singularize(x))
    df = map_column(df, "__singular__", ontology, apikey)
    
    # coalesce mappings
    df[output_col] = df[["__id__lower__", "__id__nopos__", "__id__singular__"]].copy().bfill(axis=1).iloc[:, 0]

    # drop temporary columns
    df.drop(columns=["__lower__", "__nopos__", "__singular__", "__id__lower__", "__id__nopos__", "__id__singular__"], inplace=True)
    
    df[output_col] = df[output_col].fillna("")

    # convert URI to CURIE
    df[output_col] = df[output_col].str.replace("http://purl.obolibrary.org/obo/", "")
    df[output_col] = df[output_col].str.replace("_", ":")
    
    return df
    

def map_column(df, column, ontology, apikey):
    terms = list(df[column].unique())
    map = match_terms(terms, column, ontology, apikey) 
    df = df.merge(map, on=column, how="left")
    return df


def match_terms(terms, label, ontology, apikey):
    data = get_recommendation(terms, ontology, apikey)
    id_col = f"__id{label}"
    match = pd.json_normalize(data[0]["coverageResult"], record_path="annotations", errors="ignore")
    match.rename(columns={"text": label, "annotatedClass.@id": id_col}, inplace=True)
    match[label] = match[label].str.lower()
    match = match[[label, id_col]].copy()
    return match


def get_recommendation(terms, ontologies, apikey):
    """
    Get ontology recommendations based on input terms.

    Parameters
    ----------
    terms : str
        Input terms for which ontology recommendations are needed.
        Can be a single term or a list of terms separated by comma.
    ontologies : str
        Ontologies to consider for recommendations.
        Can be a single ontology or a list of ontologies separated by comma.
    apikey : str
        BipPortal API key.

    Returns
    -------
    dict
        A dictionary containing ontology recommendations based on the input terms.

    Raises
    ------
    requests.exceptions.HTTPError
        If the HTTP request to the recommender API fails (e.g., invalid API key, server error).
    requests.exceptions.RequestException
        If there is a general request exception while communicating with the recommender API.

    Notes
    -----
    This function sends a POST request to the BioPortal Recommender API
    (https://bioportal.bioontology.org/recommender) to get ontology recommendations
    based on the provided input terms and ontologies.

    The API requires authentication via an API key, and the function uses the provided API key
    for authorization. Make sure to set the 'APIKEY' variable with a valid BioPortal API key
    before calling this function. Create a BioPortal account to get an API key.

    Example
    -------
    >>> APIKEY = "your_api_key"
    >>> terms = ["apple], "orange"]
    >>> ontologies = "FOODON"
    >>> recommendations = get_recommendation(terms, ontologies)
    """
    URL = "https://data.bioontology.org/recommender"
    HEADERS = {"accept": "application/json", "Authorization": f"apikey token={apikey}"}
    terms_string = ",".join(terms)

    params = {"input": terms_string, "input_type": "2", "ontologies": ontologies}

    try:
        response = requests.post(URL, headers=HEADERS, json=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as error:
        print(f"ERROR: {error}")
        raise
    except requests.exceptions.RequestException as error:
        print(f"ERROR: {error}")
        raise

    return data
