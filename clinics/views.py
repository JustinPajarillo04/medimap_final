from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Clinic


SERVICES = [
    "Dental",
    "Check-up",
    "Vaccination",
    "Anti-Rabies",
    "Dog Bite / Anti-Rabies",
    "Laboratory",
    "Dialysis",
    "Pediatric",
    "OB-GYN",
    "Dermatology",
    "Health Center",
]


def build_services_from_form(request):
    selected_services = request.POST.getlist("services")
    custom_services = request.POST.get("custom_services", "").strip()

    if custom_services:
        extra_services = [
            service.strip()
            for service in custom_services.split(",")
            if service.strip()
        ]

        selected_services.extend(extra_services)

    cleaned_services = []

    for service in selected_services:
        if service and service not in cleaned_services:
            cleaned_services.append(service)

    return ", ".join(cleaned_services)


def get_clinic_status(clinic):
    if hasattr(clinic, "computed_status"):
        return clinic.computed_status

    return clinic.status or "Open Now"


def get_clinic_days(clinic):
    if hasattr(clinic, "days_display"):
        return clinic.days_display

    return ""


def get_time_display(time_value):
    if not time_value:
        return ""

    return time_value.strftime("%I:%M %p")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("admin_page")

    error = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("admin_page")

        error = "Invalid username or password."

    return render(request, "login.html", {
        "error": error,
    })


def logout_page(request):
    logout(request)
    return redirect("login")


def find_clinics_page(request):
    return render(request, "find_clinics.html", {
        "active_page": "find",
    })


def nearby_page(request):
    return render(request, "nearby.html", {
        "active_page": "nearby",
    })


def services_page(request):
    return render(request, "services.html", {
        "active_page": "services",
        "services": SERVICES,
    })


@login_required(login_url="login")
def admin_page(request):
    clinics = Clinic.objects.all().order_by("name")

    return render(request, "admin.html", {
        "active_page": "admin",
        "clinics": clinics,
        "services": SERVICES,
    })


@login_required(login_url="login")
def add_clinic(request):
    if request.method != "POST":
        return redirect("admin_page")

    clinic = Clinic(
        name=request.POST.get("name", "").strip(),
        address=request.POST.get("address", "").strip(),
        contact=request.POST.get("contact", "").strip(),
        latitude=request.POST.get("latitude"),
        longitude=request.POST.get("longitude"),
        hours=request.POST.get("hours", "").strip(),
        status=request.POST.get("status", "Open Now"),
        rating=request.POST.get("rating", 5.0),
        services=build_services_from_form(request),
    )

    if hasattr(clinic, "open_time"):
        clinic.open_time = request.POST.get("open_time") or None

    if hasattr(clinic, "close_time"):
        clinic.close_time = request.POST.get("close_time") or None

    weekday_fields = [
        "open_monday",
        "open_tuesday",
        "open_wednesday",
        "open_thursday",
        "open_friday",
        "open_saturday",
        "open_sunday",
    ]

    for field in weekday_fields:
        if hasattr(clinic, field):
            setattr(clinic, field, request.POST.get(field) == "on")

    clinic.save()

    return redirect("admin_page")


@login_required(login_url="login")
def edit_clinic(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    if request.method != "POST":
        return redirect("admin_page")

    clinic.name = request.POST.get("name", "").strip()
    clinic.address = request.POST.get("address", "").strip()
    clinic.contact = request.POST.get("contact", "").strip()
    clinic.latitude = request.POST.get("latitude")
    clinic.longitude = request.POST.get("longitude")
    clinic.hours = request.POST.get("hours", "").strip()
    clinic.status = request.POST.get("status", "Open Now")
    clinic.rating = request.POST.get("rating", 5.0)
    clinic.services = build_services_from_form(request)

    if hasattr(clinic, "open_time"):
        clinic.open_time = request.POST.get("open_time") or None

    if hasattr(clinic, "close_time"):
        clinic.close_time = request.POST.get("close_time") or None

    weekday_fields = [
        "open_monday",
        "open_tuesday",
        "open_wednesday",
        "open_thursday",
        "open_friday",
        "open_saturday",
        "open_sunday",
    ]

    for field in weekday_fields:
        if hasattr(clinic, field):
            setattr(clinic, field, request.POST.get(field) == "on")

    clinic.save()

    return redirect("admin_page")


@login_required(login_url="login")
def delete_clinic(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    clinic.delete()

    return redirect("admin_page")


def clinic_to_dict(clinic):
    open_time = getattr(clinic, "open_time", None)
    close_time = getattr(clinic, "close_time", None)

    return {
        "id": clinic.id,
        "name": clinic.name,
        "address": clinic.address,
        "contact": clinic.contact or "",
        "hours": clinic.hours or "",
        "status": get_clinic_status(clinic),
        "days": get_clinic_days(clinic),
        "open_time": get_time_display(open_time),
        "close_time": get_time_display(close_time),
        "services": clinic.services or "",
        "rating": clinic.rating or 5.0,
        "latitude": clinic.latitude,
        "longitude": clinic.longitude,
    }


def clinic_list_api(request):
    search_query = request.GET.get("search", "").strip()
    service_query = request.GET.get("service", "").strip()

    clinics = Clinic.objects.all().order_by("name")

    if search_query:
        clinics = clinics.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(services__icontains=search_query)
        )

    if service_query:
        clinics = clinics.filter(services__icontains=service_query)

    data = [clinic_to_dict(clinic) for clinic in clinics]

    return JsonResponse(data, safe=False)


def clinic_detail_api(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    return JsonResponse(clinic_to_dict(clinic))