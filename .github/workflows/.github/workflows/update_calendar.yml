name: Mise à jour Radar Salles

on:
  schedule:
    - cron: '0 * * * *'  # Lance le script à la minute 0 de chaque heure
  workflow_dispatch:      # Permet d'avoir le bouton "Run workflow" manuel

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Récupération du code
      uses: actions/checkout@v3

    - name: Installation de Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10' # On assure une version récente

    - name: Installation des dépendances
      run: |
        pip install -r requirements.txt

    - name: Lancement du Radar
      # C'EST ICI QUE C'ETAIT BLOQUÉ :
      run: |
        python Radarrrr.py

    - name: Sauvegarde du fichier ICS
      run: |
        git config --global user.name "RadarBot"
        git config --global user.email "bot@noreply.github.com"
        # On ajoute le fichier qui a été créé par votre script
        git add salles_libres.ics
        # On sauvegarde (commit) et on envoie (push)
        git commit -m "Mise à jour auto calendrier" || echo "Pas de changement"
        git push
