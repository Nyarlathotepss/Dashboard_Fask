from flask import Flask, render_template, request, jsonify
import plotly.express as px
from plotly.io import to_json
from db import init_app, get_conn
app = Flask(__name__)
init_app(app)


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
