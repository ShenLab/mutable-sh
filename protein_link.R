###
# Install all necessary packages before running the script
###
library(bio3d)
library(dplyr)
library(DBI)
library(stringr)
library(RSQLite)

args <- commandArgs(trailingOnly = TRUE)
dnvs_db <- args[1]
genes_db <- args[2]
pdb_dir <- args[3]
distance_db <- args[4]

###
# Preprocess and fetch the data
###
db_dnvs <- DBI::dbConnect(RSQLite::SQLite(), dnvs_db)
mut_df <- dbGetQuery(db_dnvs, "SELECT id, gene, aa_change, consequence FROM dnvs WHERE aa_change IS NOT NULL")

db_gene <- DBI::dbConnect(RSQLite::SQLite(), genes_db)
gene_df <- dbGetQuery(db_gene, "SELECT hgnc, uniprot_id FROM gene WHERE uniprot_id IS NOT NULL")

regexp <- "[[:digit:]]+"
mut_df$aa_change <- as.numeric(str_extract(mut_df$aa_change, regexp))
mut_df %>% count(aa_change)

# extract the location of the aa_change and select only the missense consequence
df <- inner_join(mut_df, gene_df, by=c("gene"="hgnc")) %>% filter(str_detect(consequence,"missense"))
regexp <- "[[:digit:]]+"
df$aa_change <- as.numeric(str_extract(df$aa_change, regexp))


###
# Get the distance between every pair of missense nodes
###
get_distance <- function(x) {
  id <- (df %>% filter(gene==x))$uniprot_id[1]
  file_name <- paste(paste(pdb_dir,"/AF-",sep=""), id, "-F1-model_v4.pdb.gz", sep="")
  if (!file.exists(file_name)) {
    return (data.frame())
  }
  pdb <- read.pdb(file_name)
  
  # Extract data from the pdb object
  data_atoms <- pdb$atom %>% as.data.frame() 
  coords <- data_atoms %>% select(resno, x, y, z)
  
  # Calculate the average coordinates
  avg_coords <- coords %>% group_by(resno) %>% dplyr::summarise(mean_x=mean(x), mean_y=mean(y), mean_z=mean(z))
  
  # Integrate the data 
  coords_df <- inner_join(df %>% filter(gene==x) %>% distinct(aa_change, .keep_all = TRUE), avg_coords, by=c("aa_change"="resno"))
  
  if (nrow(coords_df) <= 1) {
    return (data.frame())
  }
  
  # calculate the pairwise euclidean distance
  dist_mtx <- as.matrix(dist(coords_df[6:8], method = "euclidean", diag = TRUE, upper = TRUE))
  
  # interpret the pairwise distance
  close_nodes <- data.frame(col1=character(), col2=numeric(), col3=numeric(), col4=numeric(), col5=numeric(), col6=numeric(), col7=numeric())
  
  for (i in 2:nrow(dist_mtx)) {
    for (j in 1:(i-1)) {
      # setting the threshold as 15
      if (dist_mtx[i,j] < 15) {
        id1 <- coords_df$id[i]
        id2 <- coords_df$id[j]
        
        resno1 <- coords_df$aa_change[i]
        resno2 <- coords_df$aa_change[j]
        
        dist_1d <- abs(resno1-resno2)
        
        if (resno1 > resno2) {
          new_row <- c(x, id2, resno2, id1, resno1, signif(dist_mtx[i,j],3), dist_1d)
        } else {
          new_row <- c(x, id1, resno1, id2, resno2, signif(dist_mtx[i,j],3), dist_1d)
        }
      
        close_nodes <- rbind(close_nodes, new_row)
      }
    }
  }
  
  colnames(close_nodes) <- c("gene", "id_of_variant_1", "resno_of_variant_1", "id_of_variant_2", "resno_of_variant_2", "distance_3d", "distance_1d")
  return (close_nodes)
}

# Integrate all into a function
all_genes <- df %>% group_by(gene) %>% filter(n() > 1) %>% select(gene) %>% unique()
file_path <- "distance.csv"

for (i in 1:nrow(all_genes)) {
  gene_name <- all_genes$gene[i]
  distance_df <- get_distance(gene_name)
  
  cat(sprintf("Currently on index %d of gene %s \n", i, gene_name))
  write.table(distance_df, file = file_path, sep = ",", append = TRUE, row.names = FALSE, col.names=!file.exists(file_path))
}

###
# Convert the generated csv file to a sql database
###
data_dist <- read.csv("distance.csv")
conn <- DBI::dbConnect(RSQLite::SQLite(), distance_db)
dbWriteTable(conn, "distance", data_dist)
dbDisconnect(conn)