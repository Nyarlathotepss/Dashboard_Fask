from flask import Flask, render_template, request, jsonify
from db import init_app, get_conn
from graph_plotly import graphique

app = Flask(__name__)
init_app(app)

@app.route('/recup_variables', methods=['POST'])
def recup_variables():
    """ recuperation des variables date_min et date_max, et couleur """
    dateMin = request.json['min']  # format date yyyy-mm-dd
    dateMax = request.json['max']  # format date yyyy-mm-dd
    variable = request.json['option']  # type string, a choisir parmis une liste
    graph = graphique(dateMin, dateMax, variable)
    return graph


@app.route('/variables', methods=['GET'])
def liste_variables_couleurs():
    """ liste des variables possibles """
    graph_base = graphique('1961-04-07', '2018-12-29')
    liste_variables = {"options":
                            [
                            {"value": "sexe", "label": "sexe "},
                            {"value": "statut_vital", "label":  "Statut Vital"},
                            {"value": "pole_sortie", "label": "Pole de Sortie"},
                            {"value": "patient_id", "label": "l'ID du Patient"},
                            {"value": "mode_sortie", "label": "Mode de Sortie"}
                            ],
                        "fig_json": graph_base
                        }
    return render_template("dashboard.html", liste=liste_variables, json=graph_base)


@app.route('/api/<int:id>', methods=['GET', 'DELETE', 'PUT'])
def api_get_delete_and_put(id):
    """url qui permet de modifier, afficher ou supprimer une ligne de la table patient"""

    if request.method == 'GET':
        con = get_conn()
        cur = con.cursor()
        cur.execute("SELECT * FROM sejour WHERE id = %s LIMIT 1", (id,))
        sejour = cur.fetchall()
        return jsonify(sejour)

    if request.method == 'DELETE':
        con = get_conn()
        cur = con.cursor()
        cur.execute("DELETE FROM sejour WHERE id = %s", (id,))
        con.commit()
        cur.close()
        return "Suppression effective"

    if request.method == 'PUT':
        con = get_conn()
        cur = con.cursor()
        cur.execute("""
            UPDATE sejour SET
                patient_id = %s,
                date_entree = %s,
                date_sortie = %s,
                mode_sortie = %s
            WHERE id = %s
        """, (
        request.json['patient_id'],
        request.json['date_entree'],
        request.json['date_sortie'],
        request.json['mode_sortie'],
        id
        ))
        con.commit()
        cur.close()
        return "ok"

@app.route('/api', methods=['POST'])
def api_create():
    """ url qui permet d'ajouter une ligne à la table séjour  """
    if request.method == 'POST':
        con = get_conn()
        cur = con.cursor()
        cur.execute("INSERT INTO sejour (patient_id, date_entree, date_sortie, mode_sortie )"
                    "VALUES (%s, %s, %s, %s)",
                    (
        request.json["patient_id"],
        request.json["date_entree"],
        request.json["date_sortie"],
        request.json["mode_sortie"])
                    )
        con.commit()
        cur.close()
        return "Bravo."



@app.route('/api/sejours', methods=['GET'])
def affiche_sejours():
    """ url qui permet d'afficher toute la table séjour """
    con = get_conn()
    cur = con.cursor()
    cur.execute('SELECT * FROM sejour')
    sejour = cur.fetchall()
    return jsonify(sejour)



if __name__ == '__main__':
    app.run()
# commentaire test git