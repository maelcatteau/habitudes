# Copyright (c) 2025, Maël CATTEAU and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_to_date, date_diff


class Occurencesdeshabitudes(Document):
	pass

def generate_habit_occurences():
	# Récupérer toutes les habitudes actives
    habits = frappe.get_all("Habitudes", filters={"actif": 1}, fields=["name", "fréquence"])
    
    for habit in habits:
        # Récupérer la dernière occurrence complétée de l’habitude
        last_occurrence = frappe.db.get_value(
            "Occurrences d'Habitudes",
            filters={"habitude": habit["name"]},
            fieldname=["date"],
            order_by="date desc"
        )
        
        # Calculer la date de la prochaine occurrence en fonction de la fréquence
        if last_occurrence:
            if habit["fréquence"] == "Quotidienne":
                next_due_date = add_to_date(last_occurrence, 0, 0, 0, 1)
            elif habit["fréquence"] == "Hebdomadaire":
                next_due_date = add_to_date(last_occurrence, 0, 0, 1)
            elif habit["fréquence"] == "Mensuelle":
                next_due_date = add_to_date(last_occurrence, 0, 1)
            else:
                # Si la fréquence est invalide ou non définie, ignorer cette habitude
                continue
        else:
            # Si aucune occurrence n’existe, créer une occurrence aujourd’hui
            next_due_date = nowdate()

        # Vérifier si une occurrence est nécessaire
        if date_diff(nowdate(), next_due_date) >= 0:
            # Vérifier si une occurrence existe déjà pour la date calculée
            existing = frappe.get_all(
                "Occurrences d'Habitudes",
                filters={"habitude": habit["name"], "date": next_due_date}
            )
            if not existing:
                # Créer une nouvelle occurrence
                frappe.get_doc({
                    "doctype": "Occurrences d'Habitudes",
                    "habitude": habit["name"],
                    "date": next_due_date,
                    "statut": "À faire"
                }).insert()
