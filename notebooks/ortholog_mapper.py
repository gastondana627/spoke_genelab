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
        The input column name in "df" representing the ortholog species.

    ortholog_species_entrez_gene_col : str
        The input column name in "df" representing the Entrez gene ID of the ortholog species.

    human_entrez_gene_col : str
        The output column name in "df" representing the human Entrez gene ID.

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
        If invalid entries are provided in "ortholog_dbs".

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
    >>> mapped_df = ortholog_mapper.map_orthologs(df, "taxonomy", "entrez_gene", "human_entrez_gene", ortholog_dbs=["JAX", "Ensembl"])
    >>> print(mapped_df)
            taxonomy  entrez_gene  human_entrez_gene
    0       10090     14573        2668
    1       10090     15401 	   3201
    
    """
    
    # check if ortholog dbs are valid
    if not set(ortholog_dbs).issubset(get_ortholog_dbs()):
        raise ValueError(f"Invalid entry in ortholog_dbs: specified values: {ortholog_dbs}, valid values: {get_ortholog_dbs()}")

    # check if ortholog species mappings are available in the specified databases
    check_ortholog_species(df, ortholog_species_col, ortholog_dbs)

    mappings = get_ortholog_mappings(ortholog_dbs)

    # TODO check if organisms are supported

    mappings.rename(columns={"ortholog_species": ortholog_species_col, "ortholog_species_entrez_gene": ortholog_species_entrez_gene_col, "human_entrez_gene": human_entrez_gene_col}, inplace=True)

    # drop the output column if it exists
    df.drop(columns=human_entrez_gene_col, errors="ignore", inplace=True)

    # map orthologs
    df = df.merge(mappings, on=[ortholog_species_col, ortholog_species_entrez_gene_col], how="left")

    # human genes don"t need to be mapped
    df[human_entrez_gene_col] = df.apply(lambda x: x[ortholog_species_entrez_gene_col] if x[ortholog_species_col] == "9606" else x[human_entrez_gene_col], axis=1)

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


def check_ortholog_species(df, ortholog_species_col, ortholog_dbs):
    requested_species = set(df[ortholog_species_col].unique())
    available_species = {"9606"}

    ortholog_list = get_ortholog_species()
    for db in ortholog_list.keys():
        available_species.update(ortholog_list.get(db))

    not_available = requested_species - available_species
    if len(not_available) > 0:
        print(f"WARNING: The following ortholog species: {','.join(not_available)} are not available in {','.join(ortholog_dbs)}")
        
        
def get_ortholog_species():
    ortholog_list = dict()
    ortholog_list["Panther"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9796", "9823", "9913", "10090", "10116", "13616", "28377", "284812"}
    ortholog_list["HGNC"] = {"10090"}
    ortholog_list["Ensembl"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9796", "9823", "9913", "10090", "10116", "13616", "28377", "284812"}
    ortholog_list["EggNOG"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9823", "9913", "10090", "10116", "13616", "28377", "284812"}
    ortholog_list["PomBase"] = {"284812"}
    ortholog_list["ZFIN"] = {"7955"}
    ortholog_list["HomoloGene"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9544", "9598", "9615", "9913", "10090", "10116", "284812"}
    ortholog_list["PhylomeDB"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9913", "10090", "10116", "13616", "284812"}
    ortholog_list["Treefam"] = {"6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9796", "9823", "9913", "10090", "10116", "13616", "28377"}
    ortholog_list["JAX"] = {"7955", "10090", "10116"}
    ortholog_list["OMA"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9796", "9823", "9913", "10090", "10116", "13616", "28377", "284812"}
    ortholog_list["OrthoDB"] = {"6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9796", "9823", "9913", "10090", "10116", "13616", "28377"}
    ortholog_list["NCBI"] = {"7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9796", "9823", "9913", "10090", "10116", "13616", "28377"}
    ortholog_list["Inparanoid"] = {"4932", "6239", "7227", "7955", "8364", "9031", "9258", "9544", "9598", "9615", "9685", "9796", "9823", "9913", "10090", "10116", "13616", "28377", "284812"}
    return ortholog_list

def get_jax_mappings():
    columns = ["DB Class Key", "NCBI Taxon ID", "EntrezGene ID"]
    df = pd.read_csv("https://www.informatics.jax.org/downloads/reports/HOM_AllOrganism.rpt", usecols=columns, dtype=str, sep="\t")

    # create a dataframe with human genes
    df_human = df[df["NCBI Taxon ID"] == "9606"].copy()
    df_human.rename(columns={"NCBI Taxon ID": "taxid_human", "EntrezGene ID": "human_entrez_gene"}, inplace=True)

    # merge human genes with model organism genes
    df = df[df["NCBI Taxon ID"] != "9606"].copy()
    df.rename(columns={"NCBI Taxon ID": "ortholog_species", "EntrezGene ID": "ortholog_species_entrez_gene"}, inplace=True)
    df = df.merge(df_human, on="DB Class Key")

    # remove human-to-human mappings
    df = df[df["ortholog_species_entrez_gene"] != df["human_entrez_gene"]].copy()
    
    df.drop(columns=["DB Class Key", "taxid_human"], inplace=True)

    return df


def get_hgnc_mappings(ortholog_dbs):
    columns = ["ortholog_species", "ortholog_species_entrez_gene", "human_entrez_gene", "support"]
    df = pd.read_csv("https://ftp.ebi.ac.uk/pub/databases/genenames/hcop/human_all_hcop_sixteen_column.txt.gz", dtype=str, usecols=columns, sep="\t")

    # filter mappings by the list of provided ortholog databases
    df["support"] = df["support"].str.split(",")
    df = df.explode("support")
    df = df[df["support"].isin(ortholog_dbs)]
    df.drop(columns=["support"], inplace=True)
    df.drop_duplicates(inplace=True)

    # remove rows that don"t have entrez gene identifiers
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

def get_ortholog_list():
    data = []
    dbs = list(get_ortholog_dbs())
    
    for db in dbs:
        mappings = get_ortholog_mappings([db])
        organisms = list(mappings["ortholog_species"].unique())
        organisms = sorted(organisms, key=lambda x: int(x))
        data.append({"db": db, "ortholog_species": organisms})

    return pd.DataFrame(data)


def get_ortholog_statistics():
    data = []
    dbs = list(get_ortholog_dbs())
    dbs = ["JAX"]
    
    for db in dbs:
        mappings = get_ortholog_mappings([db])
        mappings["db"] = db
        ortho_groups = mappings.groupby(["ortholog_species", "db"]).agg({"human_entrez_gene": "nunique", "ortholog_species_entrez_gene": "nunique"}).reset_index()
        ortho_groups.rename(columns={"human_entrez_gene": "human_genes",  "ortholog_species_entrez_gene": "orthologs"}, inplace=True)
        ortho_groups["orthologs_per_human_gene"] = ortho_groups["orthologs"]/ortho_groups["human_genes"]
        data.append(ortho_groups)

    statistics = pd.concat(data)
    statistics.sort_values(["ortholog_species", "orthologs_per_human_gene"], inplace=True)

    return statistics
    

    