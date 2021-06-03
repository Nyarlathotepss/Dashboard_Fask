import pandas as pd
import numpy as np
import mysql.connector as sql
import plotly.express as px
from datetime import datetime
from plotly.io import to_json


conn = sql.connect(host='localhost', database='cefim', user='root', password='root')
sejour = pd.read_sql('SELECT * FROM sejour', conn)
patient = pd.read_sql('SELECT * FROM patient', conn)
mouvement = pd.read_sql('SELECT * FROM mouvement', conn)
structure = pd.read_sql('SELECT * FROM structure', conn)
# Definition de la fonction pour le traitememnt Pandas et l'affichage du graphique Plotly


def graphique (dateMin, dateMax, variable=None):
        """ dateMin = date d'entrée minimale autorisé """
        """ dateMax = date d'entrée maximale autorisée """
        """ variable = catégorie pour les couleurs du graphique """
        #if pd.to_datetime(dateMin) < sejour["date_entree"].min() or pd.to_datetime(dateMax) > sejour["date_entree"].max():
        #    return "date incorrecte"
        #else:
        ''' Génération du graphique en fonction de ce qui est entré comme "variable" '''
        ''' Route si on entre quelque chose comme variable '''
        ''' Le dataframe "data" sera different selon la valeur de "variable" '''
        if variable is not None: # Cas si on renseigne une variable pour la couleur
            # Différents chemins pour les cas ou la variable couleur est dans des tables différentes
            # pour ne pas charger toutes les tables et alléger le traitement
            if variable in ('sexe','statut_vital'): # cas si variable dans la table patient
                ''' Route si la variable est "sexe" ou "statut_vital" '''
                data=(
                    sejour
                    .merge(patient, how='inner', left_on='patient_id',right_on='id')
                    .loc[:,['id_x', variable, 'date_entree','date_sortie']]
                    .query('date_entree >= @dateMin & date_entree <= @dateMax') # filtre sur date_entrée
                    )
            elif variable in ('pole_entree','pole_sortie') :
                ''' Route si la variable est "pole_entree" ou "pole_sortie" '''
                data = (
                        sejour
                        .merge(mouvement, how='inner', left_on='id',right_on='sejour_id', suffixes=('_sej','_mouv'))
                        [['sejour_id', 'service_id', 'date_entree_sej', 'date_sortie_sej', 'date_entree_mouv']]
                        .merge(structure, how='inner', left_on='service_id', right_on='id')
                        [['sejour_id', 'date_entree_sej', 'date_sortie_sej', 'parent_id', 'date_entree_mouv']]
                        .merge(structure, how='inner', left_on='parent_id', right_on='id')
                        .sort_values(['sejour_id', 'date_entree_mouv'])
                        .groupby('sejour_id')
                        .agg(
                            date_entree = ('date_entree_sej', 'first'),
                            date_sortie = ('date_sortie_sej', 'first'),
                            pole_entree = ('nom', 'first'),
                            pole_sortie = ('nom', 'last')
                        )
                        .reset_index(drop=False)
                        )
            else :
                ''' Route si la variable est "patient_id" ou "mode_sortie" '''
                data=(
                    sejour
                    .loc[:,['id', variable, 'date_entree','date_sortie']]
                    .query('date_entree >= @dateMin & date_entree <= @dateMax')
                    )
            ''' Creation du graphique avec le dataframe cree précedemment '''
            #nb_na = data[variable].isnull().sum() # Nombre de val manquantes
            # data[variable] = data[variable].fillna("Non renseigné")
            data = data[data[variable].notna()] # on ne garde que les données catégories diff de Nan
                                                # pour la variable catégorielle de la couleur
            data["delta"]=(data['date_sortie'] - data['date_entree']).dt.days
            data = data.sort_values(by=["delta"])
            fig = px.histogram(
                data,
                x="delta",
                color=variable,
                labels={
                     "delta": "durée du séjour"},
                nbins = int((data.delta.max()- data.delta.min()) + 1),
                barmode="stack")
            fig.layout.yaxis.title.text = 'Nombre de séjours'
            return to_json(fig)
           # return "Il y a " + nb_na.astype(str) + " valeurs manquantes"
        else :
            '''Route si on ne rentre pas de variable de coloration '''
            data=(
                sejour
                .loc[:,['id', 'date_entree','date_sortie']]
                .query('date_entree >= @dateMin & date_entree <= @dateMax')
                )
            ''' Creation du graphique avec le dataframe cree précedemment '''
            data["delta"]=(data['date_sortie'] - data['date_entree']).dt.days
            data = data.sort_values(by=["delta"])
            fig = px.histogram(
                data,
                x="delta",
                labels={
                        "delta": "durée du séjour"},
                nbins = int((data.delta.max()- data.delta.min()) + 1))
            fig.layout.yaxis.title.text = 'Nombre de séjours'
            return to_json(fig)