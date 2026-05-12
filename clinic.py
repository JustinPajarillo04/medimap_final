import re
from database import Database


class Clinic:
    def __init__(self):
        self.db = Database()

    def normalize_text(self, text):
        if not text:
            return ""

        text = text.lower()
        text = text.replace("/", " ")
        text = text.replace("-", " ")
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def service_matches(self, clinic_services, searched_service):
        clinic_services = clinic_services or ""
        searched_service = self.normalize_text(searched_service)

        if not searched_service:
            return True

        service_list = [
            self.normalize_text(service)
            for service in clinic_services.split(",")
            if service.strip()
        ]

        for service in service_list:
            if searched_service in service or service in searched_service:
                return True

        return False

    def format_clinics(self, clinics):
        formatted = []

        for clinic in clinics:
            clinic = dict(clinic)

            if clinic.get("latitude") is not None:
                clinic["latitude"] = float(clinic["latitude"])

            if clinic.get("longitude") is not None:
                clinic["longitude"] = float(clinic["longitude"])

            if clinic.get("rating") is not None:
                clinic["rating"] = float(clinic["rating"])
            else:
                clinic["rating"] = 5.0

            formatted.append(clinic)

        return formatted

    def get_all_clinics(self):
        connection = self.db.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM clinics ORDER BY id DESC")
        clinics = cursor.fetchall()

        cursor.close()
        connection.close()

        return self.format_clinics(clinics)

    def get_clinic_by_id(self, clinic_id):
        connection = self.db.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM clinics WHERE id = %s", (clinic_id,))
        clinic = cursor.fetchone()

        cursor.close()
        connection.close()

        if clinic:
            return self.format_clinics([clinic])[0]

        return None

    def search_clinics(self, keyword):
        connection = self.db.connect()
        cursor = connection.cursor()

        search_value = f"%{keyword}%"

        cursor.execute("""
            SELECT * FROM clinics
            WHERE name ILIKE %s
            OR address ILIKE %s
            OR services ILIKE %s
            ORDER BY id DESC
        """, (search_value, search_value, search_value))

        clinics = cursor.fetchall()

        cursor.close()
        connection.close()

        return self.format_clinics(clinics)

    def filter_by_service(self, service):
        clinics = self.get_all_clinics()

        filtered_clinics = [
            clinic for clinic in clinics
            if self.service_matches(clinic.get("services", ""), service)
        ]

        return filtered_clinics

    def add_clinic(self, name, address, contact, services, latitude, longitude, hours, status, rating):
        connection = self.db.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO clinics
            (name, address, contact, services, latitude, longitude, hours, status, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, address, contact, services, latitude, longitude, hours, status, rating))

        connection.commit()

        cursor.close()
        connection.close()

    def update_clinic(self, clinic_id, name, address, contact, services, latitude, longitude, hours, status, rating):
        connection = self.db.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE clinics
            SET name = %s,
                address = %s,
                contact = %s,
                services = %s,
                latitude = %s,
                longitude = %s,
                hours = %s,
                status = %s,
                rating = %s
            WHERE id = %s
        """, (name, address, contact, services, latitude, longitude, hours, status, rating, clinic_id))

        connection.commit()

        cursor.close()
        connection.close()

    def delete_clinic(self, clinic_id):
        connection = self.db.connect()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM clinics WHERE id = %s", (clinic_id,))
        connection.commit()

        cursor.close()
        connection.close()