from flask import Flask, render_template, request, jsonify
import plotly.express as px
from plotly.io import to_json
from db import init_app, get_conn, collection
from graph_plotly import graphique
app = Flask(__name__)
init_app(app)

@app.route('/api/post', methods=['POST'])
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
        return "Bravo, la ligne a été ajoutée"














@app.route('/api')
def api():
        return render_template("main_api.html")

@app.route('/api/sejours/', methods=['GET'])
def affiche_sejours():
    """ url qui permet d'afficher toute la table séjour """
    sejours = collection("SELECT * FROM sejour")
    #return render_template('show_sejour.html', sejours=sejours)
    return jsonify(sejours)



@app.route('/api/sejours/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def affiche_sejours_id(id):
    """ url qui permet d'afficher une ligne de la table séjour """
    if request.method == 'GET':
        sejour = collection("SELECT * FROM sejour WHERE id = %s LIMIT 1", (id,))
        return jsonify(sejour)

    if request.method == 'DELETE':
        con = get_conn()
        cur = con.cursor()
        cur1 = con.cursor()
        requete = collection("SELECT * FROM sejour WHERE id = %s", (id,))
        cur1.execute("DELETE FROM sejour WHERE id = %s", (id,))
        con.commit()
        cur.close()
        cur1.close()
        return jsonify(requete)

    if request.method == 'PUT':
        con = get_conn()
        cur1 = con.cursor()
        cur1.execute(" UPDATE sejour SET patient_id = %s, date_entree = %s, date_sortie = %s, mode_sortie = %s WHERE id = %s ", (
                    request.json['put_patient_id'],
                    request.json['put_date_entree'],
                    request.json['put_date_sortie'],
                    request.json['put_mode_sortie'],
                    id))
        con.commit()
        cur1.close()
        requete = collection("SELECT * FROM sejour WHERE id = %s", (id,))
        return jsonify(requete)















@app.route('/recup_variables', methods=['POST'])
def recup_variables():
    """ recuperation des variables date_min et date_max, et couleur """
    dateMin = request.json['date_Min']  # format date yyyy-mm-dd
    dateMax = request.json['date_Max']  # format date yyyy-mm-dd
    variable = request.json['variable_couleur']  # type string, a choisir parmis une liste
    graph = graphique(dateMin, dateMax, variable)
    return graph


@app.route('/variables', methods=['GET'])
def liste_variables_couleurs():
    """ liste des variables possibles """
    graph_base = graphique('1961-04-07', '2018-12-29')
    liste_variables = {"options":
                            [
                            {"value": "sexe", "label": "sexe "},
                            {"value": "statut_vital", "label":  "Statut vital"},
                            {"value": "pole_sortie", "label": "Pole de sortie"},
                            {"value": "patient_id", "label": "l'ID du patient"},
                            {"value": "mode_sortie", "label": "Mode de sortie"}
                            ],
                        "fig_json": graph_base
                        }
    return render_template("dashboard.html", liste=liste_variables, json=graph_base)


if __name__ == '__main__':
    app.run()