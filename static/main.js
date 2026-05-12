let map = null;
let markers = [];
let userMarker = null;
let selectedClinic = null;

let currentClinicPage = 1;
let currentClinicData = [];
const clinicsPerPage = 3;

let clinicSearchMode = "all";
let nearbyClinicData = [];
let serviceClinicPage = 1;
let serviceClinicData = [];
const serviceClinicsPerPage = 9;

const knownServices = [
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
    "Health Center"
];

function setupMap() {
    const mapElement = document.getElementById("map");

    if (!mapElement || typeof L === "undefined" || map !== null) {
        return;
    }

    map = L.map("map").setView([10.6765, 122.9509], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    setTimeout(function () {
        map.invalidateSize();
    }, 300);
}

function normalizeText(text) {
    if (!text) {
        return "";
    }

    return text
        .toLowerCase()
        .replace(/\//g, " ")
        .replace(/-/g, " ")
        .replace(/[^a-z0-9\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function serviceMatches(clinicServices, searchedService) {
    const searched = normalizeText(searchedService);

    if (!searched) {
        return true;
    }

    if (!clinicServices) {
        return false;
    }

    const serviceList = clinicServices
        .split(",")
        .map(function (service) {
            return normalizeText(service);
        })
        .filter(Boolean);

    return serviceList.some(function (service) {
        return searched === service || service.includes(searched) || searched.includes(service);
    });
}

function isServiceSearch(value) {
    const normalizedValue = normalizeText(value);

    return knownServices.some(function (service) {
        const normalizedService = normalizeText(service);
        return normalizedValue.includes(normalizedService) || normalizedService.includes(normalizedValue);
    });
}

function clearMarkers() {
    if (!map) {
        return;
    }

    markers.forEach(function (marker) {
        map.removeLayer(marker);
    });

    markers = [];
}

function loadClinics(searchValue = "", searchType = "text") {
    clearMarkers();

    let url = "/api/clinics";

    if (searchValue.trim() !== "") {
        if (searchType === "service") {
            url += "?service=" + encodeURIComponent(searchValue.trim());
        } else {
            url += "?search=" + encodeURIComponent(searchValue.trim());
        }
    }

    fetch(url)
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load clinics. Status: " + response.status);
            }

            return response.json();
        })
        .then(function (clinics) {
            displayClinics(clinics, searchValue);
            addMarkers(clinics);
        })
        .catch(function (error) {
            console.error("Clinic loading error:", error);
            const clinicList = document.getElementById("clinicList");
            if (clinicList) {
                clinicList.innerHTML = `
                    <div class="empty-state">
                        <h3>Unable to load clinics</h3>
                        <p>Please check your Flask terminal and the /api/clinics endpoint.</p>
                    </div>
                `;
            }
        });
}

function searchClinics() {
    const textSearch = document.getElementById("textSearch");
    const serviceSelect = document.getElementById("serviceSelect");

    const typedValue = textSearch ? textSearch.value.trim() : "";
    const selectedService = serviceSelect ? serviceSelect.value.trim() : "";

    let searchValue = typedValue;
    let searchType = "text";

    if (clinicSearchMode === "health-centers") {
        searchValue = "Health Center";
        searchType = "service";
    } else if (clinicSearchMode === "services") {
        searchValue = selectedService || typedValue;
        searchType = "service";
    } else if (clinicSearchMode === "clinics") {
        searchType = "text";
    } else if (typedValue !== "" && isServiceSearch(typedValue)) {
        searchValue = typedValue;
        searchType = "service";
    } else if (selectedService !== "") {
        searchValue = selectedService;
        searchType = "service";
    }

    if (searchValue !== "") {
        loadClinics(searchValue, searchType);
    } else {
        loadClinics();
    }
}

function setClinicSearchMode(mode) {
    clinicSearchMode = mode;

    const buttons = document.querySelectorAll(".search-mode-btn");
    const modeLabels = {
        all: "all",
        clinics: "clinics",
        services: "services",
        "health-centers": "health centers"
    };

    buttons.forEach(function (button) {
        button.classList.toggle(
            "active",
            button.textContent.trim().toLowerCase() === modeLabels[mode]
        );
    });

    if (mode === "health-centers") {
        const serviceSelect = document.getElementById("serviceSelect");
        if (serviceSelect) {
            serviceSelect.value = "Health Center";
        }
    }

    searchClinics();
}

function quickSearch(service) {
    const textSearch = document.getElementById("textSearch");
    const serviceSelect = document.getElementById("serviceSelect");

    clinicSearchMode = "services";

    if (textSearch) {
        textSearch.value = "";
    }

    if (serviceSelect) {
        serviceSelect.value = service;
    }

    loadClinics(service, "service");
}

function addMarkers(clinics) {
    if (!map || !Array.isArray(clinics)) {
        return;
    }

    clinics.forEach(function (clinic) {
        const latitude = parseFloat(clinic.latitude);
        const longitude = parseFloat(clinic.longitude);

        if (Number.isNaN(latitude) || Number.isNaN(longitude)) {
            return;
        }

        const marker = L.marker([latitude, longitude]).addTo(map);
        marker.bindPopup(
            "<strong>" + clinic.name + "</strong><br>" +
            clinic.address + "<br>Contact: " + (clinic.contact || "No contact listed") + "<br>Rating: " + (clinic.rating || "5.0") + " / 5.0<br>Services: " + (clinic.services || "No services listed")
        );
        marker.on("click", function () {
            openDetails(clinic.id);
        });
        markers.push(marker);
    });

    const firstClinic = clinics.find(function (clinic) {
        return clinic.latitude && clinic.longitude;
    });

    if (firstClinic) {
        const latitude = parseFloat(firstClinic.latitude);
        const longitude = parseFloat(firstClinic.longitude);

        if (!Number.isNaN(latitude) && !Number.isNaN(longitude)) {
            map.setView([latitude, longitude], 14);
        }
    }

    setTimeout(function () {
        if (map) {
            map.invalidateSize();
        }
    }, 300);
}

function ratingStars(rating) {
    const value = parseFloat(rating || 5.0);
    const fullStars = Math.floor(value);
    let stars = "";

    for (let index = 0; index < 5; index += 1) {
        stars += index < fullStars ? "★" : "☆";
    }

    return stars + " " + value.toFixed(1);
}

function updateHeroStats(clinics) {
    const clinicCountText = document.getElementById("clinicCountText");
    const averageRatingText = document.getElementById("averageRatingText");

    if (!Array.isArray(clinics)) {
        clinics = [];
    }

    if (clinicCountText) {
        clinicCountText.innerText = String(clinics.length);
    }

    if (averageRatingText) {
        if (clinics.length === 0) {
            averageRatingText.innerText = "0.0★";
            return;
        }

        const totalRating = clinics.reduce(function (total, clinic) {
            return total + parseFloat(clinic.rating || 5.0);
        }, 0);

        averageRatingText.innerText = (totalRating / clinics.length).toFixed(1) + "★";
    }
}

function displayClinics(clinics, searchValue) {
    const clinicCount = document.getElementById("clinicCount");
    const resultText = document.getElementById("resultText");

    if (!Array.isArray(clinics)) {
        clinics = [];
    }

    currentClinicData = clinics;
    currentClinicPage = 1;

    updateHeroStats(clinics);

    if (clinicCount) {
        clinicCount.innerText = "(" + clinics.length + ")";
    }

    if (resultText) {
        if (searchValue && searchValue.trim() !== "") {
            resultText.innerHTML = "Showing results for: <strong>" + searchValue + "</strong>";
        } else {
            resultText.innerText = "Showing available clinics";
        }
    }

    renderClinicPage();
}

function renderClinicPage() {
    const clinicList = document.getElementById("clinicList");
    const pagination = document.getElementById("clinicPagination");

    if (!clinicList) {
        return;
    }

    clinicList.innerHTML = "";

    if (!Array.isArray(currentClinicData) || currentClinicData.length === 0) {
        clinicList.innerHTML = `
            <div class="empty-state">
                <h3>No clinics found</h3>
                <p>Try another service, clinic name, or address.</p>
            </div>
        `;

        if (pagination) {
            pagination.innerHTML = "";
        }

        return;
    }

    const startIndex = (currentClinicPage - 1) * clinicsPerPage;
    const endIndex = startIndex + clinicsPerPage;
    const visibleClinics = currentClinicData.slice(startIndex, endIndex);

    visibleClinics.forEach(function (clinic) {
        const services = clinic.services ? clinic.services.split(",") : [];
        const tags = services.map(function (service) {
            return "<span>" + service.trim() + "</span>";
        }).join("");

        const distanceText = clinic.distance !== undefined ? '<p class="distance-text">' + clinic.distance.toFixed(2) + ' km away</p>' : "";
        const latitude = clinic.latitude || 0;
        const longitude = clinic.longitude || 0;

        clinicList.innerHTML += `
            <div class="clinic-card">
                <div class="clinic-card-header">
                    <h3>${clinic.name}</h3>
                    <span>${clinic.status || "Open Now"}</span>
                </div>
                <p class="clinic-rating">${ratingStars(clinic.rating)} / 5.0</p>
                ${distanceText}
                <p>${clinic.address}</p>
                <p>${clinic.contact || "No contact listed"}</p>
                <p>${clinic.hours || "No hours listed"}</p>
                <div class="service-tags">${tags || "<span>No services listed</span>"}</div>
                <div class="clinic-actions">
                    <button onclick="openDetails(${clinic.id})" class="primary-btn">View Details</button>
                    <button onclick="openDirections(${latitude}, ${longitude})" class="outline-btn">Directions</button>
                </div>
            </div>
        `;
    });

    renderClinicPagination();

    setTimeout(function () {
        if (map) {
            map.invalidateSize();
        }
    }, 300);
}

function renderClinicPagination() {
    const pagination = document.getElementById("clinicPagination");

    if (!pagination) {
        return;
    }

    const totalPages = Math.ceil(currentClinicData.length / clinicsPerPage);

    if (totalPages <= 1) {
        pagination.innerHTML = "";
        return;
    }

    let buttons = '<button onclick="changeClinicPage(' + (currentClinicPage - 1) + ')" ' + (currentClinicPage === 1 ? "disabled" : "") + '>Previous</button>';

    for (let page = 1; page <= totalPages; page += 1) {
        buttons += '<button onclick="changeClinicPage(' + page + ')" class="' + (page === currentClinicPage ? "active" : "") + '">' + page + '</button>';
    }

    buttons += '<button onclick="changeClinicPage(' + (currentClinicPage + 1) + ')" ' + (currentClinicPage === totalPages ? "disabled" : "") + '>Next</button>';

    pagination.innerHTML = buttons;
}

function changeClinicPage(page) {
    const totalPages = Math.ceil(currentClinicData.length / clinicsPerPage);

    if (page < 1 || page > totalPages) {
        return;
    }

    currentClinicPage = page;
    renderClinicPage();

    const resultsSection = document.querySelector(".clinic-carousel-section");
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: "smooth" });
    }
}

function showServiceClinics(service) {
    const overlay = document.getElementById("serviceOverlay");
    const resultTitle = document.getElementById("serviceResultTitle");
    const resultText = document.getElementById("serviceResultText");
    const clinicList = document.getElementById("serviceClinicList");
    const overlayCount = document.getElementById("serviceOverlayCount");

    if (!overlay || !clinicList) {
        return;
    }

    if (resultTitle) {
        resultTitle.innerText = service + " Clinics";
    }

    if (resultText) {
        resultText.innerText = "Loading clinics that offer " + service + "...";
    }

    overlay.style.display = "flex";
    overlay.setAttribute("aria-hidden", "false");

    clinicList.innerHTML = `
        <div class="empty-state">
            <h3>Loading...</h3>
            <p>Please wait while MediMap searches clinics.</p>
        </div>
    `;

    fetch("/api/clinics")
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load clinics");
            }

            return response.json();
        })
        .then(function (clinics) {
            serviceClinicData = clinics.filter(function (clinic) {
                return serviceMatches(clinic.services, service);
            });
            serviceClinicPage = 1;

            if (overlayCount) {
                overlayCount.innerText = String(serviceClinicData.length);
            }

            if (resultText) {
                resultText.innerText = serviceClinicData.length === 0 ? "No clinics found for " + service + "." : "Showing " + serviceClinicData.length + " clinic(s) for " + service + ".";
            }

            renderServiceClinicPage();
        })
        .catch(function (error) {
            console.error("Service directory error:", error);
            if (resultText) {
                resultText.innerText = "Unable to load clinics.";
            }
            clinicList.innerHTML = `
                <div class="empty-state">
                    <h3>Error loading clinics</h3>
                    <p>Please check your server or database connection.</p>
                </div>
            `;
        });
}

function closeServiceClinics() {
    const overlay = document.getElementById("serviceOverlay");
    if (!overlay) {
        return;
    }

    overlay.style.display = "none";
    overlay.setAttribute("aria-hidden", "true");
}

function renderServiceClinicPage() {
    const clinicList = document.getElementById("serviceClinicList");
    const pagination = document.getElementById("serviceClinicPagination");

    if (!clinicList) {
        return;
    }

    clinicList.innerHTML = "";

    if (!Array.isArray(serviceClinicData) || serviceClinicData.length === 0) {
        clinicList.innerHTML = `
            <div class="empty-state">
                <h3>No clinics found</h3>
                <p>Try a different service or search again.</p>
            </div>
        `;

        if (pagination) {
            pagination.innerHTML = "";
        }

        return;
    }

    const startIndex = (serviceClinicPage - 1) * serviceClinicsPerPage;
    const endIndex = startIndex + serviceClinicsPerPage;
    const visibleClinics = serviceClinicData.slice(startIndex, endIndex);

    visibleClinics.forEach(function (clinic) {
        const services = clinic.services ? clinic.services.split(",") : [];
        const tags = services.map(function (item) {
            return "<span>" + item.trim() + "</span>";
        }).join("");

        clinicList.innerHTML += `
            <div class="clinic-card service-result-card">
                <div class="clinic-card-header">
                    <h3>${clinic.name}</h3>
                    <span>${clinic.status || "Open Now"}</span>
                </div>
                <p class="clinic-rating">${ratingStars(clinic.rating)} / 5.0</p>
                <p>${clinic.address}</p>
                <p>${clinic.contact || "No contact listed"}</p>
                <p>${clinic.hours || "No hours listed"}</p>
                <div class="service-tags">${tags || "<span>No services listed</span>"}</div>
                <div class="clinic-actions">
                    <button onclick="openDetails(${clinic.id})" class="primary-btn">View Details</button>
                    <button onclick="openDirections(${clinic.latitude}, ${clinic.longitude})" class="outline-btn">Directions</button>
                </div>
            </div>
        `;
    });

    if (pagination) {
        const totalPages = Math.ceil(serviceClinicData.length / serviceClinicsPerPage);

        if (totalPages <= 1) {
            pagination.innerHTML = "";
            return;
        }

        let buttons = '<button onclick="changeServiceClinicPage(' + (serviceClinicPage - 1) + ')" ' + (serviceClinicPage === 1 ? "disabled" : "") + '>Previous</button>';

        for (let page = 1; page <= totalPages; page += 1) {
            buttons += '<button onclick="changeServiceClinicPage(' + page + ')" class="' + (page === serviceClinicPage ? "active" : "") + '">' + page + '</button>';
        }

        buttons += '<button onclick="changeServiceClinicPage(' + (serviceClinicPage + 1) + ')" ' + (serviceClinicPage === totalPages ? "disabled" : "") + '>Next</button>';

        pagination.innerHTML = buttons;
    }
}

function changeServiceClinicPage(page) {
    const totalPages = Math.ceil(serviceClinicData.length / serviceClinicsPerPage);

    if (page < 1 || page > totalPages) {
        return;
    }

    serviceClinicPage = page;
    renderServiceClinicPage();
}

function findNearbyMe() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    const resultText = document.getElementById("resultText");
    if (resultText) {
        resultText.innerText = "Detecting your location...";
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            showUserLocation(userLat, userLng);
            loadNearbyClinics(userLat, userLng);
        },
        function () {
            alert("Location access denied or unavailable.");
        }
    );
}

function showUserLocation(latitude, longitude) {
    if (!map) {
        return;
    }

    if (userMarker) {
        map.removeLayer(userMarker);
    }

    userMarker = L.marker([latitude, longitude]).addTo(map);
    userMarker.bindPopup("<strong>You are here</strong>").openPopup();
    map.setView([latitude, longitude], 14);
}

function loadNearbyClinics(userLat, userLng) {
    clearMarkers();

    fetch("/api/clinics")
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load nearby clinics");
            }
            return response.json();
        })
        .then(function (clinics) {
            clinics.forEach(function (clinic) {
                clinic.distance = calculateDistance(userLat, userLng, clinic.latitude, clinic.longitude);
            });

            clinics.sort(function (a, b) {
                return a.distance - b.distance;
            });

            nearbyClinicData = clinics;
            displayClinics(clinics, "Nearby Me");
            addMarkers(clinics);
        })
        .catch(function (error) {
            console.error("Nearby error:", error);
        });
}

function filterNearbyClinics() {
    const searchInput = document.getElementById("nearbySearchInput");
    const serviceSelect = document.getElementById("nearbyServiceSelect");
    const resultText = document.getElementById("resultText");

    const searchValue = searchInput ? searchInput.value.trim() : "";
    const selectedService = serviceSelect ? serviceSelect.value.trim() : "";

    if (!Array.isArray(nearbyClinicData) || nearbyClinicData.length === 0) {
        if (resultText) {
            resultText.innerText = "Use your location first to load nearby clinics.";
        }
        return;
    }

    const filteredClinics = nearbyClinicData.filter(function (clinic) {
        const searchableText = normalizeText([clinic.name, clinic.address, clinic.services, clinic.status].join(" "));
        const matchesSearch = !searchValue || searchableText.includes(normalizeText(searchValue));
        const matchesService = !selectedService || serviceMatches(clinic.services, selectedService);
        return matchesSearch && matchesService;
    });

    const searchLabel = [searchValue, selectedService].filter(Boolean).join(" • ");
    displayClinics(filteredClinics, searchLabel || "Nearby Me");
}

function setupNearbyControls() {
    const searchInput = document.getElementById("nearbySearchInput");
    const serviceSelect = document.getElementById("nearbyServiceSelect");
    const searchButton = document.getElementById("nearbySearchButton");

    if (searchInput) {
        searchInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                filterNearbyClinics();
            }
        });
    }

    if (serviceSelect) {
        serviceSelect.addEventListener("change", filterNearbyClinics);
    }

    if (searchButton) {
        searchButton.addEventListener("click", filterNearbyClinics);
    }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const earthRadius = 6371;
    const dLat = degreesToRadians(lat2 - lat1);
    const dLon = degreesToRadians(lon2 - lon1);

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(degreesToRadians(lat1)) *
        Math.cos(degreesToRadians(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return earthRadius * c;
}

function degreesToRadians(degrees) {
    return degrees * (Math.PI / 180);
}

function openDetails(clinicId) {
    fetch("/api/clinics/" + clinicId)
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Clinic not found");
            }
            return response.json();
        })
        .then(function (clinic) {
            selectedClinic = clinic;

            const detailName = document.getElementById("detailName");
            const detailAddress = document.getElementById("detailAddress");
            const detailContact = document.getElementById("detailContact");
            const detailHours = document.getElementById("detailHours");
            const detailStatus = document.getElementById("detailStatus");
            const detailServices = document.getElementById("detailServices");
            const detailRating = document.getElementById("detailRating");

            if (detailName) detailName.innerText = clinic.name;
            if (detailAddress) detailAddress.innerText = clinic.address;
            if (detailContact) detailContact.innerText = clinic.contact || "No contact listed";
            if (detailHours) detailHours.innerText = clinic.hours || "No hours listed";
            if (detailStatus) detailStatus.innerText = clinic.status || "";
            if (detailRating) detailRating.innerText = ratingStars(clinic.rating) + " / 5.0";

            if (detailServices) {
                const services = clinic.services ? clinic.services.split(",") : [];
                detailServices.innerHTML = services.length === 0
                    ? "<span>No services listed</span>"
                    : services.map(function (service) { return "<span>" + service.trim() + "</span>"; }).join("");
            }

            const modal = document.getElementById("detailsModal");
            if (modal) {
                modal.style.display = "flex";
            }
        })
        .catch(function (error) {
            console.error("Details error:", error);
        });
}

function closeDetails() {
    const modal = document.getElementById("detailsModal");
    if (modal) {
        modal.style.display = "none";
    }
}

function viewOnMap() {
    if (!selectedClinic || !map) {
        return;
    }

    map.setView([selectedClinic.latitude, selectedClinic.longitude], 16);
    closeDetails();
}

function getDirections() {
    if (!selectedClinic) {
        return;
    }

    openDirections(selectedClinic.latitude, selectedClinic.longitude);
}

function openDirections(latitude, longitude) {
    const url = "https://www.google.com/maps/dir/?api=1&destination=" + latitude + "," + longitude;
    window.open(url, "_blank");
}

function openAddModal() {
    const modal = document.getElementById("addModal");
    if (modal) {
        modal.style.display = "flex";
    }
}

function closeAddModal() {
    const modal = document.getElementById("addModal");
    if (modal) {
        modal.style.display = "none";
    }
}

function openEditModal(id) {
    const modal = document.getElementById("editModal" + id);
    if (modal) {
        modal.style.display = "flex";
    }
}

function closeEditModal(id) {
    const modal = document.getElementById("editModal" + id);
    if (modal) {
        modal.style.display = "none";
    }
}

function filterAdminCards() {
    const input = document.getElementById("adminSearch");
    const cards = document.querySelectorAll(".admin-clinic-card");

    if (!input) {
        return;
    }

    const keyword = input.value.toLowerCase();
    cards.forEach(function (card) {
        card.style.display = card.innerText.toLowerCase().includes(keyword) ? "grid" : "none";
    });
}

function updateServiceCounts() {
    const countTargets = {
        Dental: "count-Dental",
        "Check-up": "count-Check-up",
        Vaccination: "count-Vaccination",
        "Anti-Rabies": "count-Anti-Rabies",
        Laboratory: "count-Laboratory",
        Dialysis: "count-Dialysis",
        Pediatric: "count-Pediatric",
        "OB-GYN": "count-OB-GYN",
        "Health Center": "count-Health-Center"
    };

    if (!document.querySelector(".service-count")) {
        return;
    }

    fetch("/api/clinics")
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load service counts");
            }
            return response.json();
        })
        .then(function (clinics) {
            Object.keys(countTargets).forEach(function (service) {
                const target = document.getElementById(countTargets[service]);
                if (!target) {
                    return;
                }

                const count = clinics.filter(function (clinic) {
                    return serviceMatches(clinic.services, service);
                }).length;

                target.innerText = String(count);
            });
        })
        .catch(function (error) {
            console.error("Service count error:", error);
        });
}

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeServiceClinics();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    setupMap();
    setupNearbyControls();
    updateServiceCounts();

    if (document.getElementById("clinicList")) {
        loadClinics();
    }

    const textSearch = document.getElementById("textSearch");
    const serviceSelect = document.getElementById("serviceSelect");

    if (textSearch) {
        textSearch.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                searchClinics();
            }
        });
    }

    if (serviceSelect) {
        serviceSelect.addEventListener("change", function () {
            const selectedService = serviceSelect.value.trim();
            if (selectedService !== "") {
                loadClinics(selectedService, "service");
            } else {
                loadClinics();
            }
        });
    }
});
