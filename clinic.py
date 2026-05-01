from database import Database


class Clinic:
    def __init__(self):
        self.db = Database()

    def format_clinics(self, clinics):
        formatted = []

        for clinic in clinics:
            clinic = dict(clinic)
            clinic["latitude"] = float(clinic["latitude"])
            clinic["longitude"] = float(clinic["longitude"])
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

    def add_clinic(self, name, address, contact, services, latitude, longitude):
        connection = self.db.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO clinics
            (name, address, contact, services, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, address, contact, services, latitude, longitude))

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