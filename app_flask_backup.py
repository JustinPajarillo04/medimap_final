import os
from functools import wraps
from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from clinic import Clinic


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "temporary_local_secret_key")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

clinic_model = Clinic()


def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)

    return wrapper


def combine_services(form):
    selected_services = form.getlist("services")

    custom_services = form.get("custom_services", "")
    typed_services = [
        service.strip()
        for service in custom_services.split(",")
        if service.strip()
    ]

    all_services = selected_services + typed_services

    cleaned_services = []
    for service in all_services:
        if service not in cleaned_services:
            cleaned_services.append(service)

    return ", ".join(cleaned_services)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("find_clinics"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/find-clinics")
@admin_required
def find_clinics():
    return render_template(
        "find_clinics.html",
        active_page="find",
        include_map=True
    )


@app.route("/nearby")
@admin_required
def nearby():
    return render_template(
        "nearby.html",
        active_page="nearby",
        include_map=True
    )


@app.route("/services")
@admin_required
def services():
    return render_template(
        "services.html",
        active_page="services",
        include_map=False
    )


@app.route("/admin")
@admin_required
def admin():
    clinics = clinic_model.get_all_clinics()

    return render_template(
        "admin.html",
        clinics=clinics,
        active_page="admin",
        include_map=False
    )


@app.route("/add", methods=["POST"])
@admin_required
def add_clinic():
    name = request.form["name"]
    address = request.form["address"]
    contact = request.form["contact"]
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    hours = request.form.get("hours", "")
    status = request.form.get("status", "Open Now")
    rating = request.form.get("rating", "5.0")
    services = combine_services(request.form)

    clinic_model.add_clinic(
        name,
        address,
        contact,
        services,
        latitude,
        longitude,
        hours,
        status,
        rating
    )

    return redirect(url_for("admin"))


@app.route("/edit/<int:clinic_id>", methods=["POST"])
@admin_required
def edit_clinic(clinic_id):
    name = request.form["name"]
    address = request.form["address"]
    contact = request.form["contact"]
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    hours = request.form.get("hours", "")
    status = request.form.get("status", "Open Now")
    rating = request.form.get("rating", "5.0")
    services = combine_services(request.form)

    clinic_model.update_clinic(
        clinic_id,
        name,
        address,
        contact,
        services,
        latitude,
        longitude,
        hours,
        status,
        rating
    )

    return redirect(url_for("admin"))


@app.route("/delete/<int:clinic_id>")
@admin_required
def delete_clinic(clinic_id):
    clinic_model.delete_clinic(clinic_id)
    return redirect(url_for("admin"))


@app.route("/api/clinics")
@admin_required
def api_clinics():
    keyword = request.args.get("search", "")
    service = request.args.get("service", "")

    if service:
        clinics = clinic_model.filter_by_service(service)
    elif keyword:
        clinics = clinic_model.search_clinics(keyword)
    else:
        clinics = clinic_model.get_all_clinics()

    return jsonify(clinics)


@app.route("/api/clinics/<int:clinic_id>")
@admin_required
def api_clinic_details(clinic_id):
    clinic = clinic_model.get_clinic_by_id(clinic_id)

    if clinic:
        return jsonify(clinic)

    return jsonify({"error": "Clinic not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)