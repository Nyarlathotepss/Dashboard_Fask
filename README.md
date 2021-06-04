<h1> Dashboard Flask </h1>

<h2> Présentation du projet </h2>

<p> Le projet consiste à afficher un graphique sur la durée des différents séjours en fonction de 
	différents paramètres comme le sexe, la date, etc ....
	Une partie API est mise en place avec les différentes méthodes
</p>
 
<h2> Mise en place du projet </h2>

<p> Le projet a été développé sur Windows 10 sur IDE pycharm
 
<ol>
	<li> Cloner le projet GIT en local : https://github.com/Nyarlathotepss/Dashboard_Fask.git </li>
	<li> Importer le projet sur votre IDE  </li>
	<li> Executer la commande suivante: "pip install -r requirements.txt"
	<br> Elle va installer toutes les bibliothèques nécessaires
	</li>
	<li> Dans le fichier db.py préciser les informations liées a votre bdd.
	<li> Dans le fichier graph_plotly.py mettre a jour les info de connexion à la bdd (ligne 17)
	<li> Démarrer le serveur Flask > Dans un terminal positionner vous dans le dossier du projet puis 
	<br>	 éxécuter la commande: app run</li>
</ol>

<h2>Le Dashboard</h2>

Accéder à l'URL : http://127.0.0.1:5000/variables
<p> Génère un un graphique par défaut puis vous permet de saisir une option 
grace a un menu deroulant </p>

<h2>L' API</h2>

Accéder à l'URL : http://127.0.0.1:5000/api
<p> Vous odnne accès à l'api via une interface.
Selectionner la methode puis les différents paramètres puis cliquer sur le bouton </p>