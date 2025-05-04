# Project Documentation: KnowHax 2025 - SPOKE For Space Health Challenge Integration


## I. Project Goal
Integrate specific physiological, phenotypic, and environmental data related to Spaceflight Associated Neuro-ocular Syndrome (SANS) from rodent studies found in NASA's Open Science Data Repository (OSDR) into the SPOKE knowledge graph fabric. This involves Data Readiness (Objective 1), Environmental Data processing (Objective 2), and Integration (Objective 3). Initial focus: processing 2 of 8 specified physiological/phenotypic data types.

## II. Initial Setup & Environment
1.  **Repository:** Cloned fork of `BaranziniLab/spoke_genelab`.
2.  **Software:** Installed Neo4j Desktop, Miniconda/Mamba.
3.  **Neo4j Instance:** Created `spoke-genelab-db` project (DBMS v5.23.0).
4.  **Conda Environment:** Created `spoke-genelab` env from `environment.yml`.
5.  **Configuration File:** Created `.env` file with `KG_VERSION`, `KG_GIT`, `NEO4J_INSTALL_PATH`, `BIOPORTAL_API_KEY`. Verified `.gitignore` excludes `.env`.

## III. Loading Existing Omics KG (Prerequisite)
* Assumed prior completion of notebooks 1-5 from `spoke-genelab` repository, loading baseline omics data into the `spoke-genelab-v0.0.3` Neo4j database.

## IV. Objective 1: Data Readiness (Physiological/Phenotypic - 2/8 Types Processed)

### A. Optical Coherence Tomography (OCT) - OSD-679
1.  **Dataset ID:** OSD-679 confirmed.
2.  **Metadata Analysis:** Ran `save_metadata.py OSD-679`; analyzed `OSD-679_SampleTable.csv` (found complex Treatment Groups) & `OSD-679_contrasts.csv`.
3.  **Data File Download:** Downloaded `LSDS-81_Ophthalmologic Diagnostic Technique_Fuller_OCT_TRANSFORMED.csv` & `OSD-679_sup_Fuller_DataDictionary.xlsx` into project folder.
4.  **Data Analysis (Notebook `7_process_OCT_data.ipynb`):** Loaded CSVs; reshaped wide data to long (`pd.melt`); parsed headers using regex (`.str.extract`) for `Timepoint`, `Location`, `MeasurementType`, `Unit` ('millimeter'); filtered bad rows; merged Treatment Group from SampleTable; mapped `Location` to UBERON IDs (`UBERON:0016823`, `UBERON:0016824`, `UBERON:0001773`) stored in `AnatomyID`; generated unique IDs (`SubjectID`, `AssayID`, `MeasurementID`).
5.  **Graph Modeling & Output Formatting:**
    * Nodes: `:Subject`, `:Anatomy` (proxy), `:Assay`, `:MeasurementValue`.
    * Relationships: `:PERFORMED_ON`, `:HAS_OUTPUT`, `:MEASURES_ANATOMY`.
    * Created pandas DataFrames for each node/rel type with Neo4j headers (`:ID`, `:LABEL`, etc.).
    * Saved DataFrames as formatted CSVs in `output_csvs` folder.

### B. Tonometry - OSD-679
1.  **Dataset ID:** OSD-679 confirmed.
2.  **Metadata Analysis:** Reused `OSD-679_SampleTable.csv`.
3.  **Data File Download:** Downloaded `LSDS-81_tonometry_Fuller_TonometryIOP_TRANSFORMED.csv` into project folder.
4.  **Data Analysis (Notebook `11_process_tonometry_data.ipynb`):** Loaded Tonometry & SampleTable CSVs; cleaned (dropped Unnamed cols); reshaped wide data to long (`tono_df_long`) using `pd.melt`; parsed headers for `Day`, `MeasurementType` ('Intraocular Pressure'), `Unit` ('torr'); merged Treatment Group; mapped Eye (`_OD`/`_OS`) to UBERON IDs (`UBERON:0004549`/`...4548`) stored in `AnatomyID`; generated unique IDs (`IOP_ID`, `Anatomy_Node_ID`, `Treatment_Node_ID`).
5.  **Graph Modeling & Output Formatting:**
    * Nodes: `:IOP` (measurement), `:Anatomy` (eye), `:Treatment` (group).
    * Relationships: `:MEASURED_IN` (IOP->Anatomy), `:BELONGS_TO` (IOP->Treatment).
    * Created pandas DataFrames for nodes/rels using simplified structure (`id`, `source`, `target`, `relation`).
    * Saved DataFrames as formatted CSVs (e.g., `tonometry_data_iop_nodes.csv`) directly in project folder.

## V. Objective 2: Environmental Data (Exploration Started)
* Identified RR-1 mission for OSD-679.
* EDA website showed visualizations but only PNG export.
* Used OSDR API via notebook `8_explore...ipynb`:
    * Study Files API (`.../osd/files/679/`): No obvious env files found initially.
    * Specific Mission API (`.../mission/RR-1`): Failed (400 Bad Request).
    * All Missions API (`.../api/missions`): Found `SpaceX-4` ID.
    * Specific Mission API (`.../mission/SpaceX-4`): Found link to Payload `RR-1`.
    * Specific Payload API (`.../payload/RR-1`): Confirmed env data exists (e.g., `RodentHab`, `Transporter` categories) but no direct download URLs in response.
* **Status:** Incomplete. Next step would be re-analyzing the Study File list (Cell #2 output) or exploring the ISA.zip package.

## VI. Objective 3: SPOKE Integration (Partially Complete - 2 out of 8)
* **OCT Data:**
    * Copied `output_csvs` to Neo4j `import` folder.
    * Used Python notebook (`10_import_OCT_data.ipynb`) with `py2neo`.
    * Created constraints for Subject, Anatomy, Assay, MeasurementValue (Cell 1).
    * Loaded nodes using `LOAD CSV` (Cell 2).
    * Loaded relationships using `LOAD CSV` (Cell 3).
    * Verified load with basic queries.
* **Tonometry Data:**
    * Copied `tonometry_data_*.csv` files to Neo4j `import` folder.
    * Ran 5 `LOAD CSV ... CREATE ...` commands directly in Neo4j Browser (using simplified model: `:IOP`, `:Anatomy`, `:Treatment`, `:MEASURED_IN`, `:BELONGS_TO`) after resolving `file:///` prefix issue.
    * Verified load with basic queries.
* **Status:** Integration **complete** for OCT and Tonometry data. **Incomplete** for overall challenge (needs other physio/pheno and env data).

## VII. Hurdles & Findings
* **Hurdles:** Setup details, BioPortal navigation for specific UBERON IDs, OSDR API endpoint discovery (Mission/Payload vs Study), Neo4j Browser copy-paste limitations for complex Cypher, workflow/file location confusion.
* **Findings/Successes:** Successful setup of environment, processing of two distinct scientific datasets (OCT, Tonometry), ontology mapping (UBERON), graph data modeling, Python scripting for data transformation, successful API interaction, successful Neo4j data loading (via py2neo and direct Cypher), understanding OSDR data structure nuances.

## VIII. Remaining Work (Full Challenge Scope)
* **Objective 1:** Process remaining 6 physio/pheno types (find data, analyze, model, script, format).
* **Objective 2:** Find downloadable environmental data source (ISA.zip? Re-analyze Study file list?), analyze, model, script, format.
* **Objective 3:** Load formatted data from remaining Obj 1 & Obj 2 work into Neo4j. Verify full integration.
* **Bonus Objective:** Analyze integrated graph for SANS insights using Cypher.
* **Deliverables:** Documentation, GitHub Markdown, Pitch Deck, Videos.

---

This recap covers the journey so far based on our thread. You've made excellent progress, especially in processing and loading the OCT and Tonometry data!
