from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
import os
import json
import re

from mutable.auth import login_required
from mutable.db import get_gene_db, get_distance_db, get_sample_db, get_dnv_db, get_constraint_db, get_plddt_db

bp = Blueprint('views', __name__)


@bp.route('/gene/<gene>', methods=("GET", "POST"))
@login_required
def gene_view(gene):
    if request.method == 'POST':
        gene = request.form['gene'].upper()
        gene = gene.strip()
        return redirect(url_for('views.gene_view', gene=gene))
    
    gene = gene.upper().strip()
    gene_db = get_gene_db()

    if "ENSG" in gene:
        gene_id_info = gene_db.execute(
            """
            SELECT hgnc, uniprot_id, ensembl_id 
            FROM gene 
            WHERE ensembl_id = ?
            """, (gene,)
        ).fetchone()

        if not gene_id_info: # gene id not exist in our database
            return redirect(url_for('views.handleError'))

        gene = gene_id_info["hgnc"].upper()

    distance_db = get_distance_db()
    dnv_db = get_dnv_db()
    constraint_db = get_constraint_db()
    plddt_db = get_plddt_db()
    rows = dnv_db.execute(
        """
        SELECT *
        FROM dnvs
        WHERE UPPER(dnvs.gene) = ?
        """, (gene,)
    ).fetchall()

    metrics = gene_db.execute(
        """
        SELECT pli, mis_z, oe_lof, mim_id, ensembl_id, uniprot_id, uniprot_json, s_het_zeng, gene_full_name, MisFit_sgene_mis 
        FROM gene 
        WHERE UPPER(hgnc) = ?
        """, (gene,)
    ).fetchone()

    dist = distance_db.execute(
        """
        SELECT * FROM distance WHERE UPPER(gene) = ?
        """, (gene,)
    ).fetchall()

    # handling error, when the gene does not exist in the database
    if not rows or not metrics:
        return redirect(url_for('views.handleError'))

    dist_keys = ("gene","id_of_variant_1","resno_of_variant_1","id_of_variant_2","resno_of_variant_2","distance_3d","distance_1d")
    dist = [dict(zip(dist_keys, values)) for values in dist]

    # fix issue when mutiple uniprot_id with multiple protein length
    try:
        uniprot_json = json.loads(metrics["uniprot_json"])
    except Exception:
        # missing gene protein metrics
        return redirect(url_for('views.handleError'))

    sequence_info = uniprot_json["sequence"]
    aa_change_max = sequence_info["length"]
    for v in rows:
        aa_info = v["aa_change"]
        aa_pos = re.search(r'p\.\D*(\d+)', aa_info)
        if aa_pos:
            aa_change_max = max(aa_change_max, int(aa_pos.group(1))+1)
        else:
            continue
    sequence_info["length"] = aa_change_max

    sequence = {"name": "sequence", "values": sequence_info}
    aa_change = {"name": "aa_change", "values": aa_change_max}
    domains = {"name": "domains", "values": [x for x in uniprot_json["features"] if x["type"] == "Domain" or x["type"] == "Region" or x["type"] == "DNA binding"]}
    distance = {"name": "distance", "values": dist}

    seen = {}
    consequences = set()
    conditions = set()
    more_than_one = False
    for v in rows:
        if v["aa_change"] != ".":
            position = v["aa_change"].split(":")[-1]

            consequences.add(v["consequence"].replace('_variant', ''))
            conditions.add(v["cohort_condition"] if v["status"] == "affected" else v["status"])
            try:
                seen[v["aa_change"]]["count"] += 1
                more_than_one = True
            except KeyError:

                seen[v["aa_change"]] = {
                    "label": position,
                    "position": int(re.search(r"p\.(\D*)(\d+)", position).group(2)),
                    "count": 1,
                    "gmvp": v["gmvp"] if (v["gmvp"] and ("missense" in v["consequence"])) else "none",
                    "type": v["consequence"].replace('_variant', ''),
                    "condition": v["cohort_condition"] if v["status"] == "affected" else v["status"],
                    "alphamissense": "none",
                    "misfit_d": "none"
                }
                if "MisFit_D" in v.keys() and ("missense" in v["consequence"]):
                    seen[v["aa_change"]]["misfit_d"] = v["MisFit_D"]
                
                if "AlphaMissense" in v.keys() and ("missense" in v["consequence"]):
                    seen[v["aa_change"]]["alphamissense"] = v["AlphaMissense"]

                if "missense" not in v["consequence"]:
                    seen[v["aa_change"]]["label"] = re.search(r"p\.(\D*)(\d+)", position).group(2)
        
    # need to work around vega bug, also looks nicer to have a larger range when only one counts
    # this "variant" is not seen on plot due to some js logic
    if not more_than_one:
        seen["invisible"] = {
            "position": 1,
            "count": 2,
            "type": "invisible"
        }
    
    #order the missense ones to the front, for better coloring result in vega
    consequences = sorted(consequences, key=lambda x: 0 if "missense" in x else 1)

    #####new regionl depletion 
    constraint = constraint_db.execute(
        """
        SELECT gene_name, start_aa, stop_aa, oe 
        FROM regional 
        WHERE UPPER(gene_name) = ?
        """, (gene,)
    ).fetchall()

    constraint_dict = []
    for item in constraint:
        curr_row = {"gene_name": item[0], 
                    "start_aa": int(re.search(r'\d+', item[1]).group()), 
                    "stop_aa": int(re.search(r'\d+', item[2]).group()), 
                    "oe": item[3]}
        constraint_dict.append(curr_row)

    constraint_data = {"name": "constraints", "values": constraint_dict}

    #####new plddt
    uniprot_id = metrics['uniprot_id'].split(";")[0]

    plddt = plddt_db.execute(
        """
        SELECT *
        FROM plddt
        WHERE UniProtID = ?
        ORDER BY location
        """, (uniprot_id,)
    ).fetchall()
    plddt_keys = ("id","UniProtID","location","pLDDT")
    plddt_data = [dict(zip(plddt_keys, values)) for values in plddt]

    plddt = {"name": "scores", "values": plddt_data}

    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, "scripts/config.json")
    with open(config_path) as f:
        config_f = json.load(f)
        display_fields = config_f.get("display_fields")

    return render_template('gene.html', dnvs=rows, gene=gene, metrics=metrics, variants={"name": "variants", "values": list(seen.values())},
                            consequences=consequences, conditions=list(conditions), sequence=sequence, domains=domains, 
                            distance=distance, aa_change=aa_change, constraints=constraint_data, plddt=plddt, uniprot_id=uniprot_id, display_fields=display_fields)

@bp.route('/sample/<sample>', methods=("GET", "POST"))
@login_required
def sample_view(sample):
    if request.method == 'POST':
        gene = request.form['gene'].upper()
        gene = gene.strip()
        return redirect(url_for('views.gene_view', gene=gene))
    
    dnv_db = get_dnv_db()
    get_sample = get_sample_db()

    samp = get_sample.execute(
        """
        SELECT *
        FROM samples WHERE sample = ?
        """, (sample,)
    ).fetchone()

    rows = dnv_db.execute(
        """
        SELECT *
        FROM dnvs
        WHERE sample = ?
        """, (sample,)
    ).fetchall()

    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, "scripts/config.json")
    with open(config_path) as f:
        config_f = json.load(f)
        display_fields = config_f.get("display_fields")

    return render_template('sample.html', dnvs=rows, sample=samp, display_fields=display_fields)

@bp.route('/about')
@login_required
def about():
    return render_template('about.html')

@bp.route('/notes')
@login_required
def notes():
    return render_template('notes.html')

@bp.route('/', methods=("GET", "POST"))
@login_required
def index():
    if request.method == 'POST':
        gene = request.form['gene'].upper()
        gene = gene.strip()
        return redirect(url_for('views.gene_view', gene=gene))

    return render_template('index.html')

@bp.route('/error', methods=('GET', 'POST'))
def handleError():
    if request.method == 'POST':
        gene = request.form['gene'].upper()
        gene = gene.strip()
        return redirect(url_for('views.gene_view', gene=gene))
    
    return render_template('errorPage.html')

@bp.route('/lollipop', methods=('GET', 'POST'))
def lollipop():
    if request.method == 'POST':
        file = request.files['file']
        # print(file.filename, flush=True)
        file.save(file.filename)
        return redirect(url_for('lollipop.generate_lollipop', file=file.filename))

    return render_template('lollipop.html')
