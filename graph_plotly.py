############################# imports #####################################

import pandas as pd
import numpy as np
import mysql.connector as sql
import plotly.express as px
from plotly.io import to_json

################### fonction generation de la connection sql ##################

def gener_sql_conn(hote, base, utilisateur, mot_passe):
    conn = sql.connect(host=hote, database=base, user=utilisateur, password=mot_passe)
    return conn

#################### Connection et import des tables ########################

conn = gener_sql_conn('localhost', 'test_pandas', 'root', 'Melusine@@37')

sejour = pd.read_sql('SELECT * FROM sejour', conn)
patient = pd.read_sql('SELECT * FROM patient', conn)
mouvement = pd.read_sql('SELECT * FROM mouvement', conn)
structure = pd.read_sql('SELECT * FROM structure', conn)


#################### fonction generation du dataframe ##################

def gener_data(variable, d_min, d_max, T1, T2=None):
    if variable is not None :
        if T2 is not None :
            data=(
                T1
                .merge(T2, how='inner', left_on='patient_id',right_on='id')
                .loc[:,['id_x',variable, 'date_entree','date_sortie']]
                .query('date_entree >= @d_min & date_entree <= @d_max') # filtre sur date_entrée
                )
            nb_na = data[variable].isnull().sum() # Nombre de val manquantes
            data = data[data[variable].notna()]
        else :
            data=(
                T1
                .loc[:,['id',variable, 'date_entree','date_sortie']]
                .query('date_entree >= @d_min & date_entree <= @d_max') # filtre sur date_entrée
                    )
            nb_na = data[variable].isnull().sum()  # Nombre de val manquantes
            data = data[data[variable].notna()]
    else :
        data=(
            T1
            .loc[:,['id','date_entree','date_sortie']]
            .query('date_entree >= @d_min & date_entree <= @d_max') # filtre sur date_entrée
              )
        nb_na = 0 # Nombre de val manquantes

    data["delta"]=(data['date_sortie'] - data['date_entree']).dt.days
    nb_na = nb_na + data["delta"].isna().sum()
    data = data.sort_values(by=["delta"])
    data = data[data["delta"].notna()]
    return data, nb_na

data2, nb_na = gener_data('statut_vital','2005-05-17', '2016-01-27', sejour, patient)


#######################################################################
#################### fonction generation du graphique ##################

def gener_histogram(data, nb_na, couleur=None):
    ''' initialisation de la variable pour définir le barmode + on fixe les couleurs '''
    if couleur in ('sexe', 'statut_vital'):
        forma = 'group'
        if couleur == 'sexe':
            color_discrete_map = {'F': 'rgb(275,75,78)', 'M': 'rgb(103,22,223)'}
        else :
            color_discrete_map = {'V': 'rgb(56,199,107)', 'D': 'rgb(214,199,127)'}
    else:
        forma='relative'
        color_discrete_map = {'Chirurgie Thoracique': 'rgb(275,75,78)',
                                  'Endocrinologie': 'rgb(255, 19, 171)',
                                  'Dermatologie': 'rgb(204, 99, 25)',
                                  'Urgences': 'rgb(254,222,0)',
                                  'Pneumologie': 'rgb(52,22,233)',
                                  'Ophtalmologie': 'rgb(152,100,223)',
                                  'Médecine Interne': 'rgb(32,22,150)',
                                  'Orthopédie': 'rgb(120,22,223)',
                                  'Maladies Infectieuses et Tropicales': 'rgb(103,27,123)',
                                  'Chirurgie Maxillo-Faciale': 'rgb(45,154,69)',
                                  'Gériatrie': 'rgb(13,222,23)',
                                  'Neurologie': 'rgb(3,47,29)',
                                  'Chirurgie Viscérale': 'rgb(45,212,223)',
                                  'Oto-Rhino-Laryngologie': 'rgb(255, 145, 117)',
                                  'Néphrologie': 'rgb(245,85,213)',
                                  'Hépato-Gastro-Entérologie': 'rgb(204, 173, 255)'
                             }

    ''' génération de l'histogramme '''
    fig = px.histogram(
                    data,
                    x="delta",
                    color=couleur,
                    color_discrete_map=color_discrete_map,
                    labels={
                            "delta": "Durée du séjour (jours)",
                            "statut_vital":"Statut vital du patient",
                            "patient_id": "ID du patient",
                            "pole_sortie":"Pôle de sortie",
                            "pole_entree":"Pôle d'entrée",
                            "mode_sortie":"Mode de sortie",
                            "sexe":"Sexe"},
                    barmode= forma,
                    nbins = int((data.delta.max()- data.delta.min()) + 1))

    ''' update des traces pour afficher le hover '''

    fig.update_traces(text=couleur,
                          hovertemplate= "<br>Durée du séjour : %{x}" +
                          "<br>Effectif : %{y}" +"<extra></extra>") #

    ''' update du layout : format des axes x et y / enlever la grille et couleur de fond '''
    fig.update_layout(
                        title_text='Effectifs des séjours par durée',
                        yaxis=dict(title='Nombre de séjours',
                            linecolor="#BCCCDC",  # Sets color of X-axis line
                            showgrid=False  # Removes X-axis grid lines
                                ),
                        bargap=0.2,
                        xaxis=dict(
                            tickmode = 'linear',
                            tick0 =  int(data.delta.min()),
                            dtick = 1,
                            linecolor="#BCCCDC",  # Sets color of X-axis line
                            showgrid=False
                                ),
                        hoverlabel=dict(
                                bgcolor="white",
                                font_size=16,
                                font_family="Rockwell"
                                        ),
                        plot_bgcolor="#FFF")

    ''' update du layout : ajout d'une ligne de txt pour compter nb val anormales (NA, None) '''

    if nb_na > 0 :
        fig.update_layout(margin_b=100,
                             annotations = [dict(xref='paper',
                                            yref='paper',
                                            x=0.5, y=-0.25,
                                            showarrow=False,
                                            text = "Nombre de séjours total : " + str(len(data)) +
                                           " || " + str(nb_na) + " lignes ont été enlevées à cause de valeurs incorrecte")]
                         )
    else :
        fig.update_layout(margin_b=100,
                             annotations = [dict(xref='paper',
                                            yref='paper',
                                            x=0.5, y=-0.25,
                                            showarrow=False,
                                            text = "Nombre de séjours total : " +
                                                 str(len(data)))])

    return fig



# Definition de la fonction pour le traitememnt Pandas et l'affichage du graphique Plotly

def graphique (dateMin, dateMax, variable=None):
        """ dateMin = date d'entrée minimale autorisé """
        """ dateMax = date d'entrée maximale autorisée """
        """ variable = catégorie pour les couleurs du graphique """

        ''' Génération du graphique en fonction de ce qui est entré comme "variable" '''

        ''' Route si on entre quelque chose comme variable '''
        ''' Le dataframe "data" sera different selon la valeur de "variable" '''

        if variable is not None:
            if variable in ('sexe','statut_vital'): # cas si variable dans la table patient
                ''' Route si la variable est "sexe" ou "statut_vital" '''

                data, nb_na = gener_data(variable, dateMin, dateMax, sejour, patient)

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
                        .query('date_entree >= @dateMin & date_entree <= @dateMax') # filtre sur date_entrée
                        )
                data["delta"]=(data['date_sortie'] - data['date_entree']).dt.days
                data = data.sort_values(by=["delta"])
                nb_na = 0
            else :
                ''' Route si la variable est "patient_id" ou "mode_sortie" '''

                data, nb_na = gener_data(variable, dateMin, dateMax, sejour)

            ''' Creation du graphique avec le dataframe cree précedemment '''

            fig = gener_histogram(data, nb_na, variable)
            return to_json(fig)

        else :
            '''Route si on ne rentre pas de variable de coloration '''

            data, nb_na = gener_data(variable, dateMin, dateMax, sejour)

            ''' Creation du graphique avec le dataframe généré précedemment '''

            fig = gener_histogram(data, nb_na)
            return to_json(fig)


