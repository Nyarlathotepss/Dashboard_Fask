import pandas as pd
import numpy as np
import mysql.connector as sql
import plotly.express as px
from plotly.io import to_json


########################### fonction generation du graphique ##################

def gener_histogram(data, couleur=None):
    ''' initialisation de la variable pour définir le barmode '''
    if couleur in ('sexe', 'statut_vital'):
        forma = 'group'
    else:
        forma='relative'

    ''' génération de l'histogramme '''
    fig = px.histogram(
                    data,
                    x="delta",
                    color=couleur,
                    labels={
                            "delta": "Durée du séjour (jours)"},
                    barmode= forma,
                    nbins = int((data.delta.max()- data.delta.min()) + 1))

    ''' update des traces pour afficher le hover '''
   # if couleur is not None:
    #  #  fig.update_traces(customdata=data[[couleur]],
    # #                     hovertemplate= "<b>     %{customdata}</b>     " + "<br>Durée du séjour : %{x}" +
     #                     "<br>Effectif : %{y}" +"<extra></extra>") #
    #else:
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
    return fig



######################## fonction generation de la connection sql ##################

def gener_sql_conn(hote, base, utilisateur, mot_passe):
    conn = sql.connect(host=hote, database=base, user=utilisateur, password=mot_passe)
    return conn


######################### fonction generation du dataframe #######################

def gener_data(variable, d_min, d_max, T1, T2=None):
    if variable is not None :
        if T2 is not None :
            data=(
                T1
                .merge(T2, how='inner', left_on='patient_id',right_on='id')
                .loc[:,['id_x',variable, 'date_entree','date_sortie']]
                .query('date_entree >= @d_min & date_entree <= @d_max') # filtre sur date_entrée
                )
            data = data[data[variable].notna()]
        else :
            data=(
                T1
                .loc[:,['id',variable, 'date_entree','date_sortie']]
                .query('date_entree >= @d_min & date_entree <= @d_max') # filtre sur date_entrée
                    )
            data = data[data[variable].notna()]
    else :
        data=(
            T1
            .loc[:,['id','date_entree','date_sortie']]
            .query('date_entree >= @d_min & date_entree <= @d_max') # filtre sur date_entrée
              )

    data["delta"]=(data['date_sortie'] - data['date_entree']).dt.days
    data = data.sort_values(by=["delta"])
    return data


############################" import des tables necessaires #########################################

conn = gener_sql_conn('localhost', 'test_pandas', 'root', 'Melusine@@37')

sejour = pd.read_sql('SELECT * FROM sejour', conn)
patient = pd.read_sql('SELECT * FROM patient', conn)
mouvement = pd.read_sql('SELECT * FROM mouvement', conn)
structure = pd.read_sql('SELECT * FROM structure', conn)


#########################" Fonction pour retourner le json "##########################################

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

                data = gener_data(variable, dateMin, dateMax, sejour, patient)

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
                data["delta"]=(data['date_sortie'] - data['date_entree']).dt.days
                data = data.sort_values(by=["delta"])
            else :
                ''' Route si la variable est "patient_id" ou "mode_sortie" '''

                data = gener_data(variable, dateMin, dateMax, sejour)

            ''' Creation du graphique avec le dataframe cree précedemment '''

            fig = gener_histogram(data, variable)
            #fig.show()
            return to_json(fig)
        else :
            '''Route si on ne rentre pas de variable de coloration '''

            data = gener_data(variable, dateMin, dateMax, sejour)

            ''' Creation du graphique avec le dataframe cree précedemment '''

            fig = gener_histogram(data)
            #fig.show()
            return to_json(fig)


test = graphique('2005-05-17', '2016-01-27', 'pole_sortie')
print(test)
