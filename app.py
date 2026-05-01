from flask import Flask, render_template, request, redirect, jsonify
from clinic import Clinic


app = Flask(__name__)
clinic_model = Clinic()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    clinics = clinic_model.get_all_clinics()
    return render_template("admin.html", clinics=clinics)


@app.route("/add", methods=["POST"])
def add_clinic():
    name = request.form["name"]
    address = request.form["address"]
    contact = request.form["contact"]
    services = request.form["services"]
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]

    clinic_model.add_clinic(name, address, contact, services, latitude, longitude)

    return redirect("/admin")


@app.route("/delete/<int:clinic_id>")
def delete_clinic(clinic_id):
    clinic_model.delete_clinic(clinic_id)
    return redirect("/admin")


@app.route("/api/clinics")
def api_clinics():
    keyword = request.args.get("search", "")

    if keyword:
        clinics = clinic_model.search_clinics(keyword)
    else:
        clinics = clinic_model.get_all_clinics()

    return jsonify(clinics)


if __name__ == "__main__":
    app.run(debug=True)