# Self-hosting Mutable
Mutable provides tools and scripts for self-hosting a web platform for searching, analysis and visualization for *De novo* variants (DNVs).

## Prerequisites
Follow the instructions to install [Docker](https://docs.docker.com/engine/install/) 

Clone the repository

```git clone https://github.com/ShenLab/mutable-dev.git; cd mutable-dev```

## Self-host Mutable
For self-hosting using example datasets, create a folder /instance with ```mkdir instance```. Download data from [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). And unzip ```UP000005640_9606_HUMAN_v4.zip```.

Make sure the databases are in the directory ```mutable-dev/instance```. Inside  ```/instance```, create a new file ```config.py``` with ```SECRET_KEY = $YOUR_KEY```,  replace with your own secret key for flask.

We use Docker to host and deploy Mutable. To self-host Mutable on user's end, use ```docker build -t mutable:latest . ``` to build the Docker container image. And then run with ```docker run -v $INSTANCE_DIRECTORY:/mutable/instance -p 8000:8000 mutable:latest -b 0.0.0.0 "mutable:create_app()"``` to run Mutable on dev mode. Replace the ```$INSTANCE_DIRECTORY``` with the path to the /instance folder. You can modify the docker image tag if needed.

## Data preparation for additional user-provided data
7 databases and 1 additional dataset folder are required to host Mutable. Example data can be retrieved [here](https://zenodo.org/records/15792652?preview=1&token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImRlMGJjNjA1LTY3ZmYtNDMxNy04NmI0LWVjMzEzYmQ1Njg4OSIsImRhdGEiOnt9LCJyYW5kb20iOiIzZTEyNTZjZDQyOTc1MDJkNzcxMTEyNTZhOGE5ZWJlZSJ9.JsNTWqfgLL4Ild6FWn2AoDkRH2dvCX1Jei2rNj1Pb1-3-G9tv_q9YfY-03eE0vH9SZoW_wN8p8OLGhK467FYtA). Create a folder ```/instance``` with the databases and unzipped human pdb files ```UP000005640_9606_HUMAN_v4```. For extending unpublished data for DNVs and samples, modify the ```dnvs.sqlite```, ```samples.sqlite```, and ```distance.sqlite``` accordingly. 

### dnvs.sqlite
It contains the curated annotated data for DNVs. See [dnvs.sql](schema/dnvs.sql) for the schema required for creating and importing the database for DNVs. We annotate the *de novo* varaints using the annotation pipelines [here](https://github.com/ShenLab/nf_pipelines)

### samples.sqlite
It contains the sample-level data. See [samples.sql](schema/samples.sql) for the format required for creating the database for samples.

### distance.sqlite
The pairwise 1D and 3D distances data are stored in this database. We calculate the spatial distance using the script [here](mutable/protein_link.R). First unzip the downloaded ```UP000005640_9606_HUMAN_v4.zip```, then run the script to generate the pairwise distance between variants. Modify the paths in the script if needed.
The default script takes 4 arguments: path for the ```dnvs.sqlite```, ```genes.sqlite```, ```UP000005640_9606_HUMAN_v4```, and ```distance.sqlite``` respectively. Make sure all the packages required by R are installed. Then under ```/instance``` run the script with ```Rscript ../protein_link.R dnvs.sqlite genes.sqlite UP000005640_9606_HUMAN_v4 distance.sqlite```. The ```distance.sqlite``` will be updated or created if not previously exist. 

### other databases
The ```users.sqlite``` in the example data only contain access for the guest users. If you want to host Mutable and authorize registration access to the complete data, add the user email address to ```users.sqlite```. And the authorized users will be able to register with the same email address as username and with their own password on Mutable.

```constraint.sqlite```, ```genes.sqlite```, and ```plddt.sqlite``` do not require modification as they contain complete curated gene-level information for all human genes. You can also modify the databases if needed.

