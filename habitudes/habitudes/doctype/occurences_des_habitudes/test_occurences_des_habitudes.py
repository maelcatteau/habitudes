# Copyright (c) 2025, Maël CATTEAU and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import nowdate, add_to_date
from habitudes.habitudes.habitudes.doctype.occurrences_des_habitudes.occurrences_des_habitudes import generate_habit_occurrences

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

class UnitTestOccurencesdeshabitudes(UnitTestCase):
    """
    Unit tests for Occurencesdeshabitudes.
    Use this class for testing individual functions and methods.
    """

    def create_habit(self, name, frequency):
        """
        Helper function to create a habit for testing.
        """
        habit = frappe.get_doc({
            "doctype": "Habitudes",
            "name": name,
            "fréquence": frequency,
            "actif": 1
        })
        habit.insert(ignore_permissions=True)
        return habit

    def create_occurrence(self, habit_name, date):
        """
        Helper function to create a habit occurrence for testing.
        """
        occurrence = frappe.get_doc({
            "doctype": "Occurrences d'Habitudes",
            "habitude": habit_name,
            "date": date,
            "statut": "Complétée"
        })
        occurrence.insert(ignore_permissions=True)
        return occurrence

    def test_generate_habit_occurrences(self):
        # Clean up test data
        frappe.db.delete("Habitudes")
        frappe.db.delete("Occurrences d'Habitudes")

        # Create test data
        daily_habit = self.create_habit("Daily Habit", "Quotidienne")
        weekly_habit = self.create_habit("Weekly Habit", "Hebdomadaire")
        monthly_habit = self.create_habit("Monthly Habit", "Mensuelle")

        # Create last occurrences for each habit
        self.create_occurrence("Daily Habit", add_to_date(nowdate(), 0, 0, 0, -1))  # Yesterday
        self.create_occurrence("Weekly Habit", add_to_date(nowdate(), 0, 0, -1))  # A week ago
        self.create_occurrence("Monthly Habit", add_to_date(nowdate(), 0, -1))  # A month ago

        # Run the generation script
        generate_habit_occurrences()

        # Fetch occurrences
        daily_occurrence = frappe.get_all(
            "Occurrences d'Habitudes",
            filters={"habitude": "Daily Habit", "date": nowdate()},
        )
        weekly_occurrence = frappe.get_all(
            "Occurrences d'Habitudes",
            filters={"habitude": "Weekly Habit", "date": nowdate()},
        )
        monthly_occurrence = frappe.get_all(
            "Occurrences d'Habitudes",
            filters={"habitude": "Monthly Habit", "date": nowdate()},
        )

        # Assert the results
        self.assertEqual(len(daily_occurrence), 1, "Daily occurrence should have been created")
        self.assertEqual(len(weekly_occurrence), 0, "Weekly occurrence should not have been created")
        self.assertEqual(len(monthly_occurrence), 0, "Monthly occurrence should not have been created")

        # Test future dates
        self.create_occurrence("Weekly Habit", add_to_date(nowdate(), 0, 0, -2))  # Two weeks ago
        self.create_occurrence("Monthly Habit", add_to_date(nowdate(), 0, -2))  # Two months ago

        # Run the generation script again
        generate_habit_occurrences()

        # Fetch updated occurrences
        weekly_occurrence = frappe.get_all(
            "Occurrences d'Habitudes",
            filters={"habitude": "Weekly Habit", "date": nowdate()},
        )
        monthly_occurrence = frappe.get_all(
            "Occurrences d'Habitudes",
            filters={"habitude": "Monthly Habit", "date": nowdate()},
        )

        # Assert the results again
        self.assertEqual(len(weekly_occurrence), 1, "Weekly occurrence should now be created")
        self.assertEqual(len(monthly_occurrence), 1, "Monthly occurrence should now be created")

class IntegrationTestOccurencesdeshabitudes(IntegrationTestCase):
    """
    Integration tests for Occurencesdeshabitudes.
    Use this class for testing interactions between multiple components.
    """

    pass
