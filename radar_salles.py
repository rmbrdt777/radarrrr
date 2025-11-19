import os
import time
import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- VOS SALLES ---
MES_SALLES = {
    "Amphi Amande":     "S9F8A5BD6A82A88EDE0530100007FD17D",
    "Amphi Ardoise":    "S9F8A5BD6A82B88EDE0530100007FD17D",
    "Amphi Bodin":      "S9F8A5BD6A82C88EDE0530100007FD17D",
    "Amphi Inca":       "S9F8A5BD6A6E688EDE0530100007FD17D",
    "Amphi Ivoire":     "S9F8A5BD6A6E788EDE0530100007FD17D",
    "Amphi Lagon":      "S9F8A5BD6A6E888EDE0530100007FD17D",
    "Amphi Pocquet":    "S9F8A5BD6A6E988EDE0530100007FD17D",
    "Amphi Quartz":     "S9F8A5BD6A6EA88EDE0530100007FD17D",
    "Amphi Sienne":     "S9F8A5BD6A6EB88EDE0530100007FD17D",
    "Amphi Tamaris":    "S9F8A5BD6A6EC88EDE0530100007FD17D",
    "Amphi Volney":     "S9F8A5BD6A6ED88EDE0530100007FD17D"
}

URL_BASE = "https://edt.univ-angers.fr/edt/ics"
DOSSIER_CACHE = 'cache_ics'
NOM_FICHIER_SORTIE = "Mes_Salles_Libres.ics"

if not os.path.exists(DOSSIER_CACHE):
    os.makedirs(DOSSIER_CACHE)

# --- FONCTIONS ---

def telecharger_calendrier(nom, id_salle):
    chemin_fichier = os.path.join(DOSSIER_CACHE, f"{nom.replace(' ', '_')}.ics")
    url = f"{URL_BASE}?id={id_salle}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        if "html" in response.text.lower(): return None 
        with open(chemin_fichier, 'wb') as f: f.write(response.content)
        return chemin_fichier
    except: return None

def normaliser_date(dt, tz):
    if not isinstance(dt, datetime): dt = datetime.combine(dt, datetime.min.time())
    if dt.tzinfo is None: return pytz.utc.localize(dt).astimezone(tz)
    else: return dt.astimezone(tz)

def analyser_salle(chemin_ics):
    try:
        with open(chemin_ics, 'rb') as f: cal = Calendar.from_ical(f.read())
        tz = pytz.timezone('Europe/Paris')
        maintenant = datetime.now(tz)
        evenements_futurs = []
        est_libre = True
        
        # On cherche si on est occupé
        for component in cal.walk('VEVENT'):
            dtstart = normaliser_date(component.get('dtstart').dt, tz)
            dtend = normaliser_date(component.get('dtend').dt, tz)
            if dtstart <= maintenant <= dtend: est_libre = False
            if dtstart > maintenant: evenements_futurs.append(dtstart)

        evenements_futurs.sort()
        if est_libre:
            prochain = evenements_futurs[0] if evenements_futurs else None
            return "LIBRE", prochain
        return "OCCUPE", None
    except: return "ERREUR", None

# --- GÉNÉRATION DU FICHIER ICS ---

print("\n" * 5)
print(f"--- 🏭 GÉNÉRATION DU CALENDRIER ({datetime.now().strftime('%H:%M')}) ---")

# Création du nouveau calendrier vide
cal_sortie = Calendar()
cal_sortie.add('prodid', '-//Radar Salles Angers//FR//')
cal_sortie.add('version', '2.0')

tz = pytz.timezone('Europe/Paris')
maintenant = datetime.now(tz)
compteur = 0

for nom_salle, id_salle in MES_SALLES.items():
    fichier = telecharger_calendrier(nom_salle, id_salle)
    if fichier:
        statut, prochain_cours = analyser_salle(fichier)
        
        if statut == "LIBRE":
            compteur += 1
            # Création de l'événement "Salle Libre"
            event = Event()
            event.add('summary', f"✅ {nom_salle} (LIBRE)")
            event.add('dtstart', maintenant)
            
            # Définition de la fin (Prochain cours ou 20h)
            if prochain_cours:
                if prochain_cours.date() > maintenant.date():
                    # Si libre jusqu'à demain, on coupe à 20h ce soir
                    fin = maintenant.replace(hour=20, minute=0, second=0)
                else:
                    fin = prochain_cours
            else:
                # Si libre tout le temps, on coupe à 20h
                fin = maintenant.replace(hour=20, minute=0, second=0)
            
            # Petite sécurité : si il est déjà passé 20h, on met fin + 1h
            if fin < maintenant:
                fin = maintenant + timedelta(hours=1)

            event.add('dtend', fin)
            event.add('description', "Créneau libre détecté par le Radar.")
            cal_sortie.add_component(event)
            
            print(f"➕ Ajouté : {nom_salle} (jusqu'à {fin.strftime('%H:%M')})")

# Sauvegarde du fichier
with open(NOM_FICHIER_SORTIE, 'wb') as f:
    f.write(cal_sortie.to_ical())

print("-" * 50)
print(f"✅ FICHIER GÉNÉRÉ : {NOM_FICHIER_SORTIE}")
print(f"👉 Vous pouvez maintenant l'ouvrir ou l'envoyer sur votre téléphone.")