import sys
import json
import sqlite3
import re
import os 
import uuid
import flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from mutable.db import get_gene_db
from mutable.protein_link import get_data, process_data, get_distance


bp = Blueprint('lollipop', __name__)

ALLOWED_EXTENSION = {".tsv", ".txt", ".csv"}

@bp.route('/lollipop/plot/<file>', methods=('GET', 'POST'))
def generate_lollipop(file):
    # print(file, flush=True)
    ext = os.path.splitext(file)[1]
    if ext not in ALLOWED_EXTENSION:
        # print("File format not supported", flush=True)
        flash("File format not supported")
        return redirect(url_for('views.lollipop'))
    
    gene_db = get_gene_db()
    pdb_path = os.path.join('/mutable/instance', "UP000005640_9606_HUMAN_v4")

    rdm_id = uuid.uuid4() #generate unique id for each uploaded file

    try:
        mut_df, gene_df, gene = get_data(file, gene_db)

        #save the user uploaded file to temporary path (with null removed)
        dnvs_path = os.path.join('/mutable/instance', f"{rdm_id}-dnvs.sqlite")
        conn_dnvs = sqlite3.connect(dnvs_path)
        mut_df.to_sql('dnvs', conn_dnvs, if_exists = "replace", index=True)

        missense_df = process_data(mut_df, gene_df)
        distance_df = get_distance(gene, missense_df, pdb_path, 15)
    except Exception as e:
        print("The error in lollipop is", str(e), flush=True)
        flash("File invalid. Please check and submit again")
        return redirect(url_for('views.lollipop'))

    try:
        dist_path = os.path.join('/mutable/instance', f"{rdm_id}-dist.sqlite")
        conn_dist = sqlite3.connect(dist_path)
        distance_df.to_sql('distance', conn_dist, if_exists = "replace", index=False)

        print("Successfully write to database", flush=True)
    except Exception as e:
        print(f"Error writing to database: {e}", flush=True)

    distance_db = conn_dist
    conn_dist.row_factory = sqlite3.Row

    dnvs_db = conn_dnvs
    dnvs_db.row_factory = sqlite3.Row
    rows = dnvs_db.execute(
        """
        SELECT  gene,
                consequence,
                CAST(aa_change AS TEXT) as aa_change
                FROM dnvs
        """
    ).fetchall()

    gene = rows[0]['gene']

    if len(rows) == 0:
        flash("File invalid. Please check and submit again")
        return redirect(url_for('views.lollipop'))

    metrics = gene_db.execute(
        """
        SELECT uniprot_id, uniprot_json
        FROM gene 
        WHERE UPPER(hgnc) = ?
        """, (gene,)
    ).fetchone()

    dist = distance_db.execute(
        """
        SELECT * FROM distance WHERE UPPER(gene) = ?
        """, (gene,)
    ).fetchall()

    dist_keys = ("gene","resno_of_variant_1","resno_of_variant_2","distance_3d","distance_1d")
    dist = [dict(zip(dist_keys, values)) for values in dist]


    uniprot_json = json.loads(metrics["uniprot_json"])
    sequence = {"name": "sequence", "values": uniprot_json["sequence"]}
    domains = {"name": "domains", "values": [x for x in uniprot_json["features"] if x["type"] == "Domain" or x["type"] == "Region" or x["type"] == "DNA binding"]}
    distance = {"name": "distance", "values": dist}

    seen = {}
    consequences = set()
    more_than_one = False
    for v in rows:
        if v["aa_change"]:
            try:
                position = int(re.search(r'\d+', v["aa_change"]).group())
                consequences.add(v["consequence"])
            except:
                continue # invalid aa_change

            try:
                seen[v["aa_change"]]["count"] += 1
                more_than_one = True
            except KeyError:
                seen[v["aa_change"]] = {
                    "label": v["aa_change"],
                    "position": position,
                    "count": 1,
                    "type": v["consequence"]
                }
                if v["consequence"] != "missense":
                    seen[v["aa_change"]]["label"] = position
                else:
                    if "p." in v["aa_change"]:
                        # aa_info = v["aa_change"].strip().split("p.")[-1]
                        # part1 = re.split('\d+', aa_info)[0]
                        # part2 = re.split('\d+', aa_info)[-1]
                        # seen[v["aa_change"]]["label"] = str(position)+part1+">"+part2
                        seen[v["aa_change"]]["label"] = v["aa_change"]
                    else:
                        aa_info = [part for part in re.split('(\d+)', v["aa_change"].strip()) if part]
                        seen[v["aa_change"]]["label"] = aa_info[0] + aa_info[1] + aa_info[-1]
        
    if not more_than_one:
        seen["invisible"] = {
            "position": 1,
            "count": 2,
            "type": "invisible"
        }

    #remove temporary files immediately
    if os.path.exists(dnvs_path):
        os.remove(dnvs_path)

    if os.path.exists(dist_path):
        os.remove(dist_path)
    
    return render_template('display_lollipop.html', variants={"name": "variants", "values": list(seen.values())}, \
                           consequences=list(consequences), sequence=sequence, domains=domains,distance=distance, gene=gene)
