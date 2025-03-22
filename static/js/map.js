
let map;
let markers = [];
let infoWindows = [];
let allProperties = [];

function initMap() {
    const mapOptions = {
        center: new naver.maps.LatLng(37.5014, 127.0398),
        zoom: 15,
        mapTypeControl: true
    };
    
    map = new naver.maps.Map('map', mapOptions);
}

async function loadProperties() {
    try {
        const sheetType = document.querySelector('input[name="sheetType"]:checked').value;
        const response = await fetch(`/api/properties/${sheetType}`);
        if (response.ok) {
            allProperties = await response.json();
            filterProperties();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function parseAmount(str) {
    if (!str) return 0;
    return parseInt(str.replace(/[^0-9]/g, '')) || 0;
}

function filterProperties() {
    const selectedStatus = document.querySelector('input[name="statusFilter"]:checked').value;
    const searchText = document.getElementById('searchInput').value.toLowerCase();

    const depositStartBillion = parseInt(document.getElementById('depositBillionStart').value || 0) * 10000;
    const depositStartMillion = parseInt(document.getElementById('depositMillionStart').value || 0);
    const depositEndBillion = parseInt(document.getElementById('depositBillionEnd').value || 0) * 10000;
    const depositEndMillion = parseInt(document.getElementById('depositMillionEnd').value || 0);
    
    const totalDepositStart = depositStartBillion + depositStartMillion;
    const totalDepositEnd = depositEndBillion + depositEndMillion;

    const monthlyRentStart = parseInt(document.getElementById('monthlyRentStart').value || 0);
    const monthlyRentEnd = parseInt(document.getElementById('monthlyRentEnd').value || 0);

    const filteredProperties = allProperties.filter(property => {
        if (selectedStatus !== 'all' && property.status !== selectedStatus) {
            return false;
        }

        if (searchText && !property.location.toLowerCase().includes(searchText)) {
            return false;
        }

        const propertyDeposit = parseAmount(property.deposit);
        if (totalDepositStart > 0 && propertyDeposit < totalDepositStart) {
            return false;
        }
        if (totalDepositEnd > 0 && propertyDeposit > totalDepositEnd) {
            return false;
        }

        const propertyMonthlyRent = parseAmount(property.monthly_rent);
        if (monthlyRentStart > 0 && propertyMonthlyRent < monthlyRentStart) {
            return false;
        }
        if (monthlyRentEnd > 0 && propertyMonthlyRent > monthlyRentEnd) {
            return false;
        }

        return true;
    });

    displayProperties(filteredProperties);
}

function displayProperties(properties) {
    const propertyList = document.getElementById('propertyList');
    propertyList.innerHTML = '';

    markers.forEach(marker => marker.setMap(null));
    markers = [];
    infoWindows = [];

    properties.forEach(property => {
        if (!property.location) return;

        const address = property.location + ' 서울특별시';
        naver.maps.Service.geocode({
            query: address
        }, function(status, response) {
            if (status === naver.maps.Service.Status.ERROR) return;

            if (response.v2.addresses.length > 0) {
                const item = response.v2.addresses[0];
                const position = new naver.maps.LatLng(item.y, item.x);

                const marker = new naver.maps.Marker({
                    map: map,
                    position: position
                });

                const infoWindow = new naver.maps.InfoWindow({
                    content: `
                        <div class="info-window">
                            <p>${property.reg_date}</p>
                            <p>${property.location}</p>
                            <p>보증금: ${property.deposit}</p>
                            <p>월세: ${property.monthly_rent}</p>
                            <p>상태: ${property.status}</p>
                            <a href="${property.hyperlink}" target="_blank">상세 정보</a>
                        </div>
                    `
                });

                markers.push(marker);
                infoWindows.push(infoWindow);

                naver.maps.Event.addListener(marker, 'click', function() {
                    infoWindows.forEach(iw => iw.close());
                    infoWindow.open(map, marker);
                });

                const listItem = document.createElement('div');
                listItem.className = 'list-group-item property-item';
                listItem.innerHTML = `
                    <h6>${property.location}</h6>
                    <p class="mb-1">보증금: ${property.deposit}</p>
                    <p class="mb-1">월세: ${property.monthly_rent}</p>
                    <p class="mb-1">상태: ${property.status}</p>
                `;
                listItem.addEventListener('click', () => {
                    map.setCenter(position);
                    infoWindows.forEach(iw => iw.close());
                    infoWindow.open(map, marker);
                });
                propertyList.appendChild(listItem);
            }
        });
    });
}

// Event Listeners
document.getElementById('filterButton').addEventListener('click', async () => {
    await loadProperties();
    filterProperties();
});
document.getElementById('searchInput').addEventListener('input', filterProperties);

// Initialize map when the page loads
window.addEventListener('load', initMap);
