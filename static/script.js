var map = L.map("map").setView([14.5995, 120.9842], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors"
}).addTo(map);

var markers = [];

function clearMarkers() {
    markers.forEach(function(marker) {
        map.removeLayer(marker);
    });

    markers = [];
}

function loadClinics() {
    clearMarkers();

    var searchValue = document.getElementById("searchInput").value;

    fetch("/api/clinics?search=" + encodeURIComponent(searchValue))
        .then(function(response) {
            return response.json();
        })
        .then(function(clinics) {
            clinics.forEach(function(clinic) {
                var marker = L.marker([
                    clinic.latitude,
                    clinic.longitude
                ]).addTo(map);

                marker.bindPopup(`
                    <strong>${clinic.name}</strong><br>
                    Address: ${clinic.address}<br>
                    Contact: ${clinic.contact}<br>
                    Services: ${clinic.services}
                `);

                markers.push(marker);
            });

            if (clinics.length > 0) {
                map.setView([clinics[0].latitude, clinics[0].longitude], 14);
            }
        });
}

loadClinics();