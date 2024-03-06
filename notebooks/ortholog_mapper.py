"""
This module provides functions to map model organism genes to orthologous human genes.

Author: Peter W Rose (pwrose@ucsd.edu)
Created: 2024-03-05
"""

import pandas as pd

def map_orthologs(df, ortholog_species_col, ortholog_species_entrez_gene_col, human_entrez_gene_col, ortholog_dbs):
    """
    Maps orthologous genes from other species to human genes.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to map orthologs to.

    ortholog_species_col : str
        The input column name in 'df' representing the ortholog species.

    ortholog_species_entrez_gene_col : str
        The input column name in 'df' representing the Entrez gene ID of the ortholog species.

    human_entrez_gene_col : str
        The output column name in 'df' representing the human Entrez gene ID.

    ortholog_dbs : list
        List of ortholog databases to use for mapping.
        See get_ortholog_dbs() for a list of available databases.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame with mapped orthologs.

    Raises:
    -------
    ValueError
        If invalid entries are provided in 'ortholog_dbs'.

    Example
    -------
    >>> import pandas as pd
    >>> import ortholog_mapper
    >>>
    >>> # Sample DataFrame (may contain other columns)
    >>> df = pd.DataFrame({
    >>>      "taxonomy": ["10090", "10090"],
    >>>      "entrez_gene": ["14573", "15401"]
    >>> })
    >>> # mapper adds a column with orthologous human genes
    >>> mapped_df = orthology_mapper.map_orthologs(df, "taxonomy", "entrez_gene", "human_entrez_gene", ortholog_dbs=["JAX", "Ensembl"])
    >>> print(mapped_df)
            taxonomy  entrez_gene  human_entrez_gene
    0       10090     14573        2668
    1       10090     15401 	   3201
    
    """
    
    # check if ortholog dbs are valid
    if not set(ortholog_dbs).issubset(get_ortholog_dbs()):
        raise ValueError(f"Invalid entry in ortholog_dbs: specified values: {ortholog_dbs}, valid values: {get_ortholog_dbs()}")
        
    mappings = get_ortholog_mappings(ortholog_dbs)

    mappings.rename(columns={"ortholog_species": ortholog_species_col, "ortholog_species_entrez_gene": ortholog_species_entrez_gene_col, "human_entrez_gene": human_entrez_gene_col}, inplace=True)
    df = df.merge(mappings, on=[ortholog_species_col, ortholog_species_entrez_gene_col], how="left")
    df.fillna("", inplace=True)
    return df


def get_ortholog_mappings(ortholog_dbs):
    # get JAX vertebrate mappings (mouse, human, rat, zebrafish)       
    jax = pd.DataFrame()
    if "JAX" in ortholog_dbs:
        jax = get_jax_mappings()

    # get HGNC mappings if there are other databases besides JAX
    hgnc = pd.DataFrame()
    if not ("JAX" in ortholog_dbs and len(ortholog_dbs) == 1):
        hgnc = get_hgnc_mappings(ortholog_dbs)

    hgnc_jax = pd.concat([hgnc, jax])
    hgnc_jax.drop_duplicates(inplace=True)

    return hgnc_jax


def get_ortholog_dbs():
    # JAX: https://www.informatics.jax.org/downloads/reports/index.html#homology
    # other dbs: https://www.genenames.org/help/hcop/#!/#tocAnchor-1-3
    return {"JAX", "Ensembl", "Treefam", "OMA", "EggNOG", "PhylomeDB", "OrthoDB", "Panther",
            "NCBI", "HomoloGene", "Inparanoid", "OrthoMCL", "HGNC", "ZFIN", "PomBase"}


def get_jax_mappings():
    columns = ["DB Class Key", "NCBI Taxon ID", "EntrezGene ID"]
    df = pd.read_csv("https://www.informatics.jax.org/downloads/reports/HOM_AllOrganism.rpt", usecols=columns, dtype=str, sep='\t')

    # create a dataframe with human genes
    df_human = df[df["NCBI Taxon ID"] == "9606"].copy()
    df_human.rename(columns={"NCBI Taxon ID": "taxid_human", "EntrezGene ID": "human_entrez_gene"}, inplace=True)

    # merge human genes with model organism genes
    df.rename(columns={"NCBI Taxon ID": "ortholog_species", "EntrezGene ID": "ortholog_species_entrez_gene"}, inplace=True)
    df = df.merge(df_human, on="DB Class Key")

    # remove human-to-human mappings
    df = df[df["ortholog_species_entrez_gene"] != df["human_entrez_gene"]].copy()
    
    df.drop(columns=["DB Class Key", "taxid_human"], inplace=True)

    return df


def get_hgnc_mappings(ortholog_dbs):
    columns = ["ortholog_species", "ortholog_species_entrez_gene", "human_entrez_gene", "support"]
    df = pd.read_csv("https://ftp.ebi.ac.uk/pub/databases/genenames/hcop/human_all_hcop_sixteen_column.txt.gz", dtype=str, usecols=columns, sep='\t')

    # filter mappings by the list of provided ortholog databases
    df["support"] = df["support"].str.split(",")
    df = df.explode("support")
    df = df[df["support"].isin(ortholog_dbs)]
    df.drop(columns=["support"], inplace=True)
    df.drop_duplicates(inplace=True)

    # remove rows that don't have entrez gene identifiers
    df = df[(df["ortholog_species_entrez_gene"].str.isdigit()) & (df["human_entrez_gene"].str.isdigit())].copy()

    # reorder columns
    df = df[["ortholog_species", "ortholog_species_entrez_gene", "human_entrez_gene"]]
    return df


def compare(ortholog_dbs):
    hgnc = get_hgnc_mappings(ortholog_dbs)
    hgnc.rename(columns={"human_entrez_gene": "human_entrez_gene_hgnc"}, inplace=True)
    
    jax = get_jax_mappings()
    jax.rename(columns={"human_entrez_gene": "human_entrez_gene_jax"},inplace=True)

    common = jax.merge(hgnc, on=["ortholog_species", "ortholog_species_entrez_gene"], how="left")

    return common

    