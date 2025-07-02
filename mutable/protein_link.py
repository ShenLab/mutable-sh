import sqlite3
import pandas as pd
import re
from Bio.PDB import *
from Bio.PDB.PDBParser import PDBParser
import os
import gzip
from sklearn.metrics.pairwise import pairwise_distances
from flask import flash, redirect, url_for

def get_data(file, genes_db):
    ext = os.path.splitext(file)[1]
    if ext == ".tsv":
        mut_df = pd.read_csv(file, sep='\t')
    elif ext == ".txt":
        mut_df = pd.read_csv(file, sep=" ")
    else: # csv file
        mut_df = pd.read_csv(file)

    # uploaded file in variant format, with not aa_change column specified
    mut_df.columns = mut_df.columns.str.lower()
    chr_names = ['chr', 'chrom', 'chromosome']
    pos_names = ['pos', 'position']

    if 'aa_change' not in mut_df:

        if "consequence" not in mut_df:
            flash("Data should include consequence column.")
            return redirect(url_for('views.lollipop'))
        
        if "chr" in mut_df:
            mut_df.rename(columns={'gene': 'symbol'}, inplace=True)
        
        if not any([n for n in chr_names if n in mut_df.columns]):
            flash("Data should include CHROM column.")
            return redirect(url_for('views.lollipop'))
        else:
            mut_df.rename(columns={'gene': 'symbol'}, inplace=True)
        
        if not any([n for n in pos_names if n in mut_df.columns]):
            flash("Data should include POS column.")
            return redirect(url_for('views.lollipop'))
        
        if "ref" not in mut_df:
            flash("Data should include REF column.")
            return redirect(url_for('views.lollipop'))
        
        if "alt" not in mut_df:
            flash("Data should include ALT column.")
            return redirect(url_for('views.lollipop'))


        ### More error debugging should goes here

        mut_df['key'] = mut_df['chrom'].str.extract(r'(\d+)')[0].astype(str) + '-' + mut_df['pos'].astype(str) + '-' + mut_df['ref'].astype(str) + '-' + mut_df['alt'].astype(str)
        mut_df = mut_df[mut_df["consequence"] == "missense"]

        keys_set = set(mut_df['key'])

        misfit_path = os.path.join('/mutable/instance', "misfit.sqlite")
        conn = sqlite3.connect(misfit_path)
        conn.row_factory = sqlite3.Row

        try:
            param = ', '.join('?' * len(keys_set))
            query = f"""
                    SELECT  Symbol,
                            Ensembl_protein_position,
                            AA_ref,
                            AA_alt
                            FROM misfit
                    WHERE (Chrom||'-'||Pos||'-'||Ref||'-'||Alt) IN ({param})
                    """

            res = pd.read_sql_query(query, conn, params=list(keys_set))
            conn.close()

            res['gene'] = res['Symbol']
            res['consequence'] = "missense"
            res['aa_change'] = res['Ensembl_protein_position'].astype(str)+res['AA_ref']+'>'+res['Ensembl_protein_position'].astype(str)+res['AA_alt']
        except Exception as e:
            print("The error in protein_link is", e, flush=True)

        mut_df = res


    # uploaded file in gene format (with aa_change column specified)
    else:
        if "gene" not in mut_df:
            flash("Data should include gene column.")
            return redirect(url_for('views.lollipop'))

        if "consequence" not in mut_df:
            flash("Data file should include consequence column.")
            return redirect(url_for('views.lollipop'))

        mut_df = mut_df[mut_df["aa_change"].notna()]

    gene = mut_df['gene'].iloc[0]

    gene_df = pd.read_sql_query("SELECT hgnc, uniprot_id FROM gene WHERE uniprot_id IS NOT NULL", genes_db)
    return mut_df, gene_df, gene


def process_data(mut_df, gene_df):
    mut_df['aa_change'] = mut_df['aa_change'].str.extract(r'(\d+)')[0].astype('Int64')
    df = mut_df.merge(gene_df, left_on='gene', right_on='hgnc', how='inner')
    missense_df = df[df['consequence'] == 'missense']
    return missense_df

def get_distance(gene, missense_df, pdb_dir, threshold):
    uniprot_id = missense_df.loc[missense_df['gene'] == gene]["uniprot_id"].iloc[0]
    pdb_file = os.path.join(pdb_dir, f"AF-{uniprot_id}-F1-model_v4.pdb.gz")

    if not os.path.exists(pdb_file):
        return pd.DataFrame()
        
    parser = PDBParser(QUIET=True)
    temp = gzip.open(pdb_file, "rt")
    
    structure = parser.get_structure('pdb', temp)
    coords = []
    for atom in structure.get_atoms():
        res_id = atom.get_full_id()[3][1]
        curr_coord = atom.get_coord()
        coords.append([res_id, curr_coord[0], curr_coord[1], curr_coord[2]])
    
    coords_df = pd.DataFrame(coords, columns=['resno', 'x', 'y', 'z'])

    if coords_df.shape[0] <= 1:
        return pd.DataFrame()

    avg_coords = coords_df.groupby('resno').mean()
    missense_df = missense_df.drop_duplicates(subset=['aa_change'])
    coords_df = pd.merge(missense_df[missense_df['gene'] == gene], avg_coords, left_on='aa_change', right_on='resno', how='inner')

    dist_mtx = pairwise_distances(coords_df[['x','y','z']], metric="euclidean")

    close_nodes = []
    for i in range(1, len(dist_mtx)):
        for j in range(i):
            if dist_mtx[i][j] < threshold:
                resno1 = coords_df['aa_change'][i]
                resno2 = coords_df['aa_change'][j]
                dist_1d = abs(resno1 - resno2)
                
                if resno1 > resno2:
                    close_nodes.append([gene, resno2, resno1, round(dist_mtx[i][j],3), dist_1d])
                else:
                    close_nodes.append([gene, resno1, resno2, round(dist_mtx[i][j],3), dist_1d])

    res_df = pd.DataFrame(close_nodes, columns=["gene","resno_of_variant_1","resno_of_variant_2", "distance_3d", "distance_1d"])
    return res_df
