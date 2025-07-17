# Self-hosting Mutable
Mutable provides tools and scripts for self-hosting a web platform for searching, analysis and visualization for *De novo* variants (DNVs).

## Prerequisites
Follow the instructions to install [Docker](https://docs.docker.com/engine/install/) 

Clone the repository

```git clone https://github.com/ShenLab/mutable-sh; cd mutable-sh```

  
For generating databases for extended data, [R](https://www.r-project.org/) is required. And following R packages are required:
- bio3d
- dplyr
- DBI
- stringr
- RSQLite

## Self-host Mutable
For self-hosting using example datasets, inside the repo, create a folder with ```mkdir instance```. Under ```mutable-sh/instance```, download PDB data from [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). And unzip the PDB file ```UP000005640_9606_HUMAN_v4.zip```.

Make sure all other databases (*dnvs.sqlite*, *genes.sqlite*, *samples.sqlite*, *distance.sqlite*, *constraint.sqlite*, *plddt.sqlite*, *users.sqlite*) are in the directory ```mutable-sh/instance```. Inside  ```mutable-sh/instance```, create a new file ```config.py``` with ```SECRET_KEY=$YOUR_KEY```,  replace with your own secret key for flask to secure session data for the web app, or you can create a random string using ```python -c 'import os; print(os.urandom(12))'```.

We use Docker to host and deploy Mutable. To self-host Mutable on user's end, use ```docker build -t mutable:latest . ``` to build the Docker container image. And then run with ```docker run -v $INSTANCE_DIRECTORY:/mutable/instance -p 8000:8000 mutable:latest -b 0.0.0.0 "mutable:create_app()"``` to run Mutable. Replace the ```$INSTANCE_DIRECTORY``` with the absolute path to the /instance folder. You can modify the docker image tag if needed.

## Data preparation for additional user-provided data
7 databases and 1 additional dataset folder are required to host Mutable. Example data can be retrieved [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). For extending unpublished data for DNVs and samples, under ```mutable-sh/instance``` modify the ```dnvs.sqlite```, ```samples.sqlite```, and ```distance.sqlite``` accordingly. 

### dnvs.sqlite 
Our published data for *de novo* varaints can be retreived [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). It contains the curated annotated data for published DNVs. See [dnvs.sql](schema/dnvs.sql) for the schema required for creating and importing the database for DNVs. The schema shows the required attributes for variants data need for Mutable. You can add more fields if needed. We annotate the *de novo* varaints using the annotation pipelines [here](https://github.com/ShenLab/nf_pipelines)

### samples.sqlite
It contains sample-level [data]((https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA)) for published variants. See [samples.sql](schema/samples.sql) for the format required for creating the database for samples. The schema shows the required attributes need for sample-level data for Mutable. You can add more fields if needed.

### distance.sqlite
Our example data for pairwise distance data for the published DNVs can be retreived [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). 
The pairwise 1D and 3D distances data are stored in this database. We calculate the spatial distance using the script [here](mutable/scripts/protein_link.R). First unzip the downloaded ```UP000005640_9606_HUMAN_v4.zip```, then run the script to generate the pairwise distance between variants. Modify the paths in the script if needed.
The default script takes 4 arguments: paths for the ```dnvs.sqlite```, ```genes.sqlite```, ```UP000005640_9606_HUMAN_v4```, and ```distance.sqlite``` respectively. Make sure all the packages required by R are installed. Then under ```/instance``` run the script with ```Rscript ../protein_link.R dnvs.sqlite genes.sqlite UP000005640_9606_HUMAN_v4 distance.sqlite```. The ```distance.sqlite``` will be updated or created if not previously exist. 

### other databases
Other databases can also be retreived [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). 
The ```users.sqlite``` in the example data only contain access for the guest users. If you want to host Mutable and authorize registration access to the complete data, add the user email address as new username to ```users.sqlite``` following [user.sql](schema/user.sql). And then the authorized users will be able to register with the username and their own password on Mutable. Passwords will be hashed for credentials safety. 

```constraint.sqlite```, ```genes.sqlite```, and ```plddt.sqlite``` do not require modification as they contain complete curated gene-level information for all human genes. You can also modify the databases if needed.

### Annotation data specification
On the gene-centered page, variant-level annotation data for computational estimates and selection coefficients are selected to display on the gene-centerd page. You can modify [config.json](mutable/scripts/config.json) to specify data columns to show in the table.