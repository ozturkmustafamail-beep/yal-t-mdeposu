/**
 * Location (City/District) Selection for Yalitimdeposu.com
 */
document.addEventListener('DOMContentLoaded', function () {
    const popup = document.getElementById('locationPopup');
    const cityList = document.getElementById('cityList');
    const citySearch = document.getElementById('citySearchInput');
    const districtSection = document.getElementById('districtSection');
    const districtSelect = document.getElementById('districtSelect');
    const confirmBtn = document.getElementById('confirmLocationBtn');
    const changeCityBtn = document.getElementById('changeCityBtn');

    let selectedCityId = null;

    // Cities data — loaded inline to avoid extra requests
    const cities = [
        { id: 0, name: 'Adana', plate: '01' }, { id: 0, name: 'Adıyaman', plate: '02' },
        { id: 0, name: 'Afyonkarahisar', plate: '03' }, { id: 0, name: 'Ağrı', plate: '04' },
        { id: 0, name: 'Amasya', plate: '05' }, { id: 0, name: 'Ankara', plate: '06' },
        { id: 0, name: 'Antalya', plate: '07' }, { id: 0, name: 'Artvin', plate: '08' },
        { id: 0, name: 'Aydın', plate: '09' }, { id: 0, name: 'Balıkesir', plate: '10' },
        { id: 0, name: 'İstanbul', plate: '34' }, { id: 0, name: 'İzmir', plate: '35' },
        { id: 0, name: 'Bursa', plate: '16' }, { id: 0, name: 'Kocaeli', plate: '41' },
        { id: 0, name: 'Konya', plate: '42' }, { id: 0, name: 'Gaziantep', plate: '27' },
    ];
    // Note: Full city list will be loaded dynamically from the API

    // Load full cities from API
    function loadCities() {
        // We'll use a simple fetch to get cities
        // For now render them from the popup's data
        if (!cityList) return;

        fetch('/api/cities/')
            .catch(() => {
                // Fallback: render basic city buttons
                renderCityButtons();
            });
    }

    function renderCityButtons(filter = '') {
        if (!cityList) return;
        // We need actual city data from the server
        // The popup in base.html will work with server-rendered data
        // For now just set up search functionality
    }

    // City search
    if (citySearch) {
        citySearch.addEventListener('input', function () {
            const filter = this.value.toLowerCase();
            const buttons = cityList.querySelectorAll('.city-btn');
            buttons.forEach(btn => {
                btn.style.display = btn.textContent.toLowerCase().includes(filter) ? '' : 'none';
            });
        });
    }

    // Change city button
    if (changeCityBtn) {
        changeCityBtn.addEventListener('click', function () {
            // Show popup if exists, or reload with popup
            if (popup) {
                popup.style.display = 'flex';
            } else {
                // Force show popup by removing session
                window.location.href = '/?change_location=1';
            }
        });
    }

    // Load cities from API/inline
    if (popup && cityList) {
        // Populate cities via API
        fetch('/lokasyon/ilceler/0/')
            .catch(() => { });

        // Actually, let's populate from the existing data in the page
        // We need to create city buttons
        populateCitiesFromServer();
    }

    function populateCitiesFromServer() {
        if (!cityList) return;

        // Fetch all cities (we'll use a simple endpoint)
        // For now, populate with hardcoded list that matches seed data
        const allCities = [
            'Adana', 'Adıyaman', 'Afyonkarahisar', 'Ağrı', 'Amasya', 'Ankara', 'Antalya',
            'Artvin', 'Aydın', 'Balıkesir', 'Bilecik', 'Bingöl', 'Bitlis', 'Bolu', 'Burdur',
            'Bursa', 'Çanakkale', 'Çankırı', 'Çorum', 'Denizli', 'Diyarbakır', 'Edirne',
            'Elazığ', 'Erzincan', 'Erzurum', 'Eskişehir', 'Gaziantep', 'Giresun', 'Gümüşhane',
            'Hakkari', 'Hatay', 'Isparta', 'Mersin', 'İstanbul', 'İzmir', 'Kars', 'Kastamonu',
            'Kayseri', 'Kırklareli', 'Kırşehir', 'Kocaeli', 'Konya', 'Kütahya', 'Malatya',
            'Manisa', 'Kahramanmaraş', 'Mardin', 'Muğla', 'Muş', 'Nevşehir', 'Niğde', 'Ordu',
            'Rize', 'Sakarya', 'Samsun', 'Siirt', 'Sinop', 'Sivas', 'Tekirdağ', 'Tokat',
            'Trabzon', 'Tunceli', 'Şanlıurfa', 'Uşak', 'Van', 'Yozgat', 'Zonguldak', 'Aksaray',
            'Bayburt', 'Karaman', 'Kırıkkale', 'Batman', 'Şırnak', 'Bartın', 'Ardahan', 'Iğdır',
            'Yalova', 'Karabük', 'Kilis', 'Osmaniye', 'Düzce'
        ];

        cityList.innerHTML = '';
        allCities.forEach((name, i) => {
            const btn = document.createElement('button');
            btn.className = 'city-btn';
            btn.textContent = name;
            btn.type = 'button';
            btn.addEventListener('click', () => selectCity(name, i + 1));
            cityList.appendChild(btn);
        });
    }

    function selectCity(name, plateIndex) {
        selectedCityId = plateIndex;

        // Highlight selected
        cityList.querySelectorAll('.city-btn').forEach(b => b.style.borderColor = '');

        // Load districts
        if (districtSection) {
            districtSection.style.display = 'block';
            districtSelect.innerHTML = '<option value="">Yükleniyor...</option>';

            fetch('/lokasyon/ilceler/' + plateIndex + '/')
                .then(r => r.json())
                .then(data => {
                    districtSelect.innerHTML = '<option value="">İlçe seçin...</option>';
                    if (data.districts.length === 0) {
                        // No districts, just confirm city
                        districtSection.style.display = 'none';
                        submitLocation(plateIndex, null);
                        return;
                    }
                    data.districts.forEach(d => {
                        const opt = document.createElement('option');
                        opt.value = d.id;
                        opt.textContent = d.name;
                        districtSelect.appendChild(opt);
                    });
                })
                .catch(() => {
                    // If no districts endpoint, just set city
                    submitLocation(plateIndex, null);
                });
        }
    }

    // Confirm button
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function () {
            const districtId = districtSelect ? districtSelect.value : null;
            submitLocation(selectedCityId, districtId);
        });
    }

    function submitLocation(cityId, districtId) {
        const formData = new FormData();
        formData.append('city_id', cityId);
        if (districtId) formData.append('district_id', districtId);

        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) formData.append('csrfmiddlewaretoken', csrfToken.value);

        // Also try cookie
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        const token = cookie ? cookie.split('=')[1] : '';

        fetch('/lokasyon/sehir-sec/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': token,
            },
        }).then(() => {
            window.location.reload();
        }).catch(() => {
            window.location.reload();
        });
    }
});
