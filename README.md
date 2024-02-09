# spoke_genelab

[WORK IN PROGRESS]

---
## Data Import Into Neo4j Knowledge Graph

### Setup

------
Prerequisites: Miniconda3 (light-weight, preferred) or Anaconda3 and Mamba (faster than Conda)

* Install [Miniconda3](https://docs.conda.io/en/latest/miniconda.html)
* Update an existing miniconda3 installation: ```conda update conda```
* Install Mamba: ```conda install mamba -n base -c conda-forge```
* Install Git (if not installed): ```conda install git -n base -c anaconda```
------

1. Clone this Repository

```
git clone https://github.com/BaranziniLab/spoke_genelab.git
cd spoke_genelab
```

```
2. Create a Conda environment

The file `environment.yml` specifies the Python version and all required dependencies.

```
mamba env create -f environment.yml
```

3. Download the Neo4j Desktop application from the [Neo4j Download Center](https://neo4j.com/download-center/#desktop) and follow the installation instructions.

4. When the installation is complete, Neo4j Desktop will launch. Click the `New` button to create a new project.

![](docs/new_project.png)

5. Hover the cursor over the created project, click the edit button, and change the project name from `Project` to `spoke-genelab`.

![](docs/rename_project.png)

6. Click the `ADD` button and select `Local DBMS`.

![](docs/add_graph_dbms.png)

7. Enter the password `neo4jdemo` and click `Create`.
    
![](docs/create_dbms.png)
    
8. Select `Terminal` to open a terminal window.
    
![](docs/open_terminal.png)

9. Type `pwd` in the terminal window to show the path to the `NEO4J_HOME` directory. This path is required to configure the upload process, see the next section.
 
![](docs/get_path.png)

10. Make a *copy* of the file `.env_template` and rename it to `.env`

11. Edit the file `.env` and set the following variables

KG version number
`KG_VERSION=v0.0.1`

Path to the cloned git repository
`KG_GIT=/Users/.../spoke_genelab/`

Path to the Neo4J instance in Neo4j Desktop (in quotes). See step 8.
`NEO4J_INSTALL_PATH="/Users/.../Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/dbms-3d4b95d1-0219-480b-a3c4-ee5a409cc383"`


### Import data into the spoke-genelab Neo4j Desktop database

1. Start the spoke-genelab Graph DBMS

![](docs/start_dbms.png)

2. Activate the conda environment

```
conda activate spoke-genelab
```

3. Open and run the Jupyter Notebook import_to_desktop.ipynb to import the data into the versioned `spoke-genlab-v#.#.#` database.

[import_to_desktop.ipynb](notebooks/import_to_desktop.ipynb)

4. When the import is completed, click the `Refresh` button. The newly created database `spoke-genlab-v#.#.#` will be listed.

![](docs/db_imported.png)

5. Click the `Open` button to launch the database.

![](docs/open_dbms.png)

6. Click on the database icon on the left.

![](docs/select_db_icon.png)

7. Use the pull-down menu to select a version of `spoke-genlab-v#.#.#` database
   
![](docs/db_ready.png)

8. Set the Graph Stylesheet

Drag the file kg/v#.#.#/style.grass onto the Neo4j Browser window to set the colors, sizes, and labels for the nodes.

9. Now you are ready to run Cypher queries on the selected database.

10. When you are finished, stop the database in the Neo4j Desktop.

To stop the conda environment, type

```conda deactivate```
