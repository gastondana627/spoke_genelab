Project Documentation: KnowHax 2025 - SPOKE For Space Health Challenge Integration
I. Project Goal
Integrate specific physiological, phenotypic, and environmental data related to Spaceflight Associated Neuro-ocular Syndrome (SANS) from rodent studies found in NASA's Open Science Data Repository (OSDR) into the SPOKE knowledge graph fabric. This involves Data Readiness (Objective 1), Environmental Data processing (Objective 2), and Integration (Objective 3). Initial focus: processing 3 of 8 specified physiological/phenotypic data types.

II. Initial Setup & Environment
Repository: Cloned fork of BaranziniLab/spoke_genelab.
Software: Installed Neo4j Desktop, Miniconda/Mamba.
Neo4j Instance: Created spoke-genelab-db project (DBMS v5.23.0).
Conda Environment: Created spoke-genelab env from environment.yml.
Configuration File: Created .env file with KG_VERSION, KG_GIT, NEO4J_INSTALL_PATH, BIOPORTAL_API_KEY. Verified .gitignore excludes .env.
III. Loading Existing Omics KG (Prerequisite)
Assumed prior completion of notebooks 1-5 from spoke-genelab repository, loading baseline omics data into the spoke-genelab-v0.0.3 Neo4j database.
IV. Objective 1: Data Readiness (Physiological/Phenotypic - 3/8 Types Processed)
A. Optical Coherence Tomography (OCT) - OSD-679 (Completed Prior)

Dataset ID: OSD-679 confirmed.
Metadata Analysis: Ran save_metadata.py OSD-679; analyzed OSD-679_SampleTable.csv & OSD-679_contrasts.csv.
Data File Download: Downloaded LSDS-81_Ophthalmologic Diagnostic Technique_Fuller_OCT_TRANSFORMED.csv & Data Dictionary into project folder.
Data Analysis (Notebook 7_process_OCT_data.ipynb): Loaded CSVs; reshaped wide to long (pd.melt); parsed headers (regex); filtered bad rows; merged Treatment Group; mapped Location to UBERON IDs; generated unique IDs.
Graph Modeling & Output Formatting:
Nodes: :Subject, :Anatomy (proxy), :Assay, :MeasurementValue.
Relationships: :PERFORMED_ON, :HAS_OUTPUT, :MEASURES_ANATOMY.
Created formatted CSVs for import in output_csvs folder.
B. Tonometry - OSD-679 (Completed Prior)

Dataset ID: OSD-679 confirmed.
Metadata Analysis: Reused OSD-679_SampleTable.csv.
Data File Download: Downloaded LSDS-81_tonometry_Fuller_TonometryIOP_TRANSFORMED.csv into project folder.
Data Analysis (Notebook 11_process_tonometry_data.ipynb): Loaded CSVs; cleaned; reshaped wide to long; parsed headers; merged Treatment Group; mapped Eye UBERON IDs; generated unique IDs.
Graph Modeling & Output Formatting:
Nodes: :IOP (measurement), :Anatomy (eye), :Treatment (group).
Relationships: :MEASURED_IN (IOP->Anatomy), :BELONGS_TO (IOP->Treatment).
Created formatted CSVs for import directly in project folder.
C. Immunostaining (HNE) - OSD-557 (Completed This Session)

Dataset ID: OSD-557 confirmed.
Metadata Analysis: Assumed pre-existing :Sample nodes from prior work or save_metadata.py.
Data File Download: Located and downloaded HNE Retina Layer (LSDS-1...HNE_RetinaLayer...csv), HNE Photoreceptor, and PNA Retina transformed files. Resolved download issues and moved files into notebooks directory.
Data Analysis (Jupyter Notebook): Loaded HNE Retina CSV into pandas datasets dictionary; cleaned column names; identified sample_id and hne_mean_intensity_1 for integration.
Graph Modeling: Planned nodes :Sample (existing), :HneMeasurement (new), :Study (existing/created); relationships :HAS_MEASUREMENT (new), :HAS_SAMPLE (new/verified).
V. Objective 2: Environmental Data (Exploration Started)
Identified RR-1 mission for OSD-679.
EDA website explored; limited export options noted.
Used OSDR API via notebook 8_explore...ipynb:
Explored Study, Mission, Payload endpoints.
Found env data categories under Payload RR-1 but no direct download URLs via API.
Status: Incomplete. Needs further investigation (ISA.zip? Re-analyze Study file list?).
VI. Objective 3: SPOKE Integration (Partially Complete - 3 Types Integrated)
A. OCT Data Integration (Completed Prior)

Copied formatted CSVs to Neo4j import.
Used Python (py2neo) notebook 10_import... to create constraints and LOAD CSV nodes/rels. Verified.
B. Tonometry Data Integration (Completed Prior)

Copied formatted CSVs to Neo4j import.
Used direct Cypher (LOAD CSV) in Neo4j Browser to load nodes/rels. Verified.
C. Immunostaining (HNE) Data Integration (Completed This Session)

Used Python (neo4j-driver) to attempt loading sample HNE Retina data (hne_mean_intensity_1 for F15, F16, F17).
Encountered transaction persistence errors: script reported commit success, but data (measurements/relationships) was not found in subsequent queries.
Manually verified/created :Sample nodes exist via Browser Cypher.
Manually created/verified :HneMeasurement node and :HAS_MEASUREMENT relationship for sample F15 via Browser Cypher.
Manually created/verified :Study node (accession: 'OSD-557') and :HAS_SAMPLE relationships for F15, F16, F17 via Browser Cypher.
Successfully visualized the integrated path Study -> Sample -> Measurement for the manually confirmed F15 data point in Neo4j Browser.
Status: Integration pattern successfully demonstrated for sample HNE data from OSD-557. Loading other HNE/PNA data via script/LOAD CSV requires further debugging/time.
VII. Hurdles & Findings
Hurdles: Setup details; BioPortal navigation; OSDR API endpoint discovery; Neo4j Browser limitations; Neo4j transaction persistence inconsistencies (Python driver); workflow/file location confusion; debugging LOAD CSV (file location, 0 rows processed); time constraints.
Findings/Successes: Successful setup; processing of OCT & Tonometry data; ontology mapping; graph modeling; Python scripting; API interaction; successful Neo4j loading (py2neo, direct Cypher); successful loading & integration demonstration for HNE data via manual Cypher correction; insight into OSDR data structure; successfully integrated three data modalities (OCT, Tono, HNE) into KG.
VIII. Remaining Work (Full Challenge Scope)
Objective 1: Process remaining 5 physio/pheno types (Micro-CT, PNA Immunostaining (OSD-557), Immunostaining/Microscopy (OSD-568), Ultrasonography, MRI, Implanted Sensors).
Objective 2: Find downloadable environmental data source, process, model, format.
Objective 3: Load formatted data from remaining Obj 1 & Obj 2 work into Neo4j. Verify full integration.
Bonus Objective: Analyze integrated graph for SANS insights using Cypher.
Deliverables: Documentation, GitHub Markdown, Pitch Deck, Videos.
Image 5-4-...at 5.48 PM

JPG
Image 5-4-...at 6.14 PM

JPG
You’re near your Gemini Advanced usage limit. You can upload files again at 7:06 PM. Learn more.

