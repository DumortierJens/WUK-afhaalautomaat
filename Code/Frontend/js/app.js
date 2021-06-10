'use strict';

//#region ***  Global references                           ***********

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let token;
let lockerId;
let updateLastDetection, updateLastLockOpened;

//#endregion

//#region ***  DOM references                           ***********

let htmlIndex, htmlLogin, htmlHistoriek, htmlLocker, htmlLockerCode, htmlLockerStatus, htmlLockerOrder, htmlLockerEditOrder;
let htmlChartTemperature, htmlChartDetection, htmlChartLocks;

//#endregion

//#region ***  Callback-Visualisation - show___         ***********

const showLockers = function (data) {
    const lockers = data.lockers;

    let html = ``;
    let idLockers = [];
    for (let locker of lockers) {
        html += `<div class="c-locker o-layout__item">
            <div class="c-locker__box">
                <p class="c-locker__title">
                    ${locker.name}
                    <a class="c-value-box__link" href="./locker?lockerid=${locker.id}"><span class="material-icons-outlined">arrow_forward_ios</span></a>
                </p>
                <p class="c-locker__item">Slot <span class="c-locker__value js-locker-lock" data-deviceid=${locker.deviceid}>Gesloten</span></p>
                <p class="c-locker__item">Status <span class="c-locker__value">${locker.status}</span></p>
            </div>
        </div>`;
        idLockers.push(locker.id);
    }

    document.querySelector('.js-lockers').innerHTML = html;
    for (let lockerId of idLockers) socket.emit('F2B_locker_lock_status', lockerId);
};

const showLocker = function (data) {
    const locker = data.locker;

    document.querySelector('.js-button-code').href += `?lockerid=${locker.id}`;
    document.querySelector('.js-button-status').href += `?lockerid=${locker.id}`;
    document.querySelector('.js-button-order').href += `?lockerid=${locker.id}`;

    document.querySelector('.js-locker-name').innerHTML = locker.name;
    document.querySelector('.js-locker-status').innerHTML = locker.status;
    document.querySelector('.js-locker-lock').dataset.deviceid = locker.deviceid;

    socket.emit('F2B_locker_lock_status', locker.id);
};

const showLockStatus = function (lock) {
    const htmlLocks = document.querySelectorAll(`.js-locker-lock`);

    if (htmlLocks != []) {
        for (let htmlLock of htmlLocks) {
            if (htmlLock.dataset.deviceid == lock.deviceid) {
                if (lock.status == 1) htmlLock.innerHTML = 'Open';
                else if (lock.status == 0) htmlLock.innerHTML = 'Gesloten';
            }
        }
    }
};

const showCurrentTemperature = function (currentTemperature) {
    document.querySelector('.js-current-temperature').innerHTML = `${currentTemperature.toString().replace(".", ",")} °C`;
};

const timediffTimestamp = function (timestamp) {
    let timeDiffString = `Minder dan 1 minuut`;

    const timeDiff = Date.now() - new Date(timestamp).getTime();
    const seconds = Math.floor(timeDiff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days != 0) {
        if (days == 1) timeDiffString = `1 dag`;
        else timeDiffString = `${days} dagen`;
    }
    else if (hours != 0) {
        timeDiffString = `${hours} uur`;
    }
    else if (minutes != 0) {
        if (minutes == 1) timeDiffString = `1 minuut`;
        else timeDiffString = `${minutes} minuten`;
    }

    return timeDiffString;
};

const showLockLastOpened = function (lock) {
    let lockLastOpened = `Minder dan 1 minuut`;
    if (lock.status == 0) lockLastOpened = timediffTimestamp(lock.timestamp);
    document.querySelector(`.js-locker-last-opened`).innerHTML = `${lockLastOpened} geleden`;
};

const showLastDetection = function (lastDetection) {
    let htmlLastDetection = `Minder dan 1 minuut`;
    if (lastDetection.status == 0) htmlLastDetection = timediffTimestamp(lastDetection.timestamp);
    document.querySelector('.js-last-detection').innerHTML = `${htmlLastDetection} geleden`;
};

const showHistoryTemperature = function (data) {
    const history = data.history;

    let chartData = [];
    for (let item of history) {
        chartData.push([new Date(item.timestamp).getTime() + 1 * 60 * 60000, item.value]);
    }

    if (htmlChartTemperature == null) {
        const options = {
            chart: {
                type: 'area',
                height: '240px',
                fontFamily: 'Open Sans, sans-serif',
                foreColor: '#f2ebe1',
                toolbar: {
                    tools: {
                        download: false,
                    }
                }
            },
            stroke: {
                curve: 'smooth',
                width: 2
            },
            colors: ['#f8991e'],
            series: [
                {
                    name: 'Temperatuur (°C)',
                    data: chartData,
                },
            ],
            xaxis: {
                type: 'datetime',
            },
            legend: {
                showForSingleSeries: true,
                onItemClick: {
                    toggleDataSeries: false,
                },
            },
            tooltip: {
                x: {
                    format: 'H:mm dd/MM/yyyy ',
                },
                marker: false
            },
            dataLabels: {
                enabled: false,
            },
        };
        htmlChartTemperature = new ApexCharts(document.querySelector('.js-temperature-chart'), options);
        htmlChartTemperature.render();
    }
    else {
        htmlChartTemperature.updateSeries([{ data: chartData }]);
    }
};

const showHistoryDetection = function (data) {
    const history = data.history;

    let chartData = [];
    for (let item of history) {
        item.status == 0 ? item.status = 1 : item.status = 0;
        chartData.push([new Date(item.timestamp).getTime() + 1 * 60 * 60000, item.status]);
    }

    if (htmlChartDetection == null) {
        const options = {
            chart: {
                type: 'area',
                height: '240px',
                fontFamily: 'Open Sans, sans-serif',
                foreColor: '#f2ebe1',
                toolbar: {
                    tools: {
                        download: false,
                    }
                }
            },
            stroke: {
                curve: 'stepline',
                width: 2
            },
            colors: ['#f8991e'],
            series: [
                {
                    name: 'Detectie',
                    data: chartData,
                },
            ],
            xaxis: {
                type: 'datetime',
            },
            yaxis: {
                labels: {
                    show: false,
                }
            },
            legend: {
                showForSingleSeries: true,
                onItemClick: {
                    toggleDataSeries: false
                },
            },
            tooltip: {
                x: {
                    show: false,
                    format: 'H:mm dd/MM/yyyy ',
                },
                items: {
                    display: 'none',
                },
            },
            dataLabels: {
                enabled: false,
            },
        };

        htmlChartDetection = new ApexCharts(document.querySelector('.js-detection-chart'), options);
        htmlChartDetection.render();
    }
    else {
        htmlChartDetection.updateSeries([{ data: chartData }]);
    }
};

const showHistoryLocks = function (data) {
    const history = data.history;

    let chartData = {};
    for (let item of history) {
        item.status == 0 ? item.status = 1 : item.status = 0;
        if (!(item.name in chartData)) chartData[item.name] = [];
        chartData[item.name].push([new Date(item.timestamp).getTime() + 1 * 60 * 60000, item.status]);
    }

    // console.log(chartData);

    let series = [];
    for (let key in chartData) {
        series.push({ name: key, data: chartData[key] });
    }

    if (htmlChartLocks == null) {
        const options = {
            chart: {
                type: 'area',
                height: '240px',
                fontFamily: 'Open Sans, sans-serif',
                foreColor: '#f2ebe1',
                toolbar: {
                    tools: {
                        download: false,
                    }
                }
            },
            stroke: {
                curve: 'stepline',
                width: 2
            },
            colors: ['#f8991e', '#d91f11'],
            series: series,
            xaxis: {
                type: 'datetime',
            },
            yaxis: {
                labels: {
                    show: false
                }
            },
            legend: {
                showForSingleSeries: true,
            },
            tooltip: {
                x: {
                    show: false,
                    format: 'H:mm dd/MM/yyyy ',
                },
                items: {
                    display: 'none',
                },
            },
            dataLabels: {
                enabled: false,
            },
        };

        htmlChartLocks = new ApexCharts(document.querySelector('.js-lock-status-chart'), options);
        htmlChartLocks.render();
    }
    else {
        htmlChartLocks.updateSeries(series);
    }
};

const showLockerStatuses = function (data) {
    const statuses = data.statuses;

    let html = ``;
    for (let status of statuses) html += `<option value="${status.id}">${status.description}</option>`;
    document.querySelector('.js-status').innerHTML = html;

    getLockerStatus(lockerId);
};

const showLockerStatus = function (data) {
    document.querySelector('.js-status').value = data.status.lockerstatusid;
};

const showLockerOrder = function (data) {
    const order = data.order;

    if (htmlLockerOrder) {
        document.querySelector('.js-orderid').innerHTML = order.orderid == null ? '-' : order.orderid;
        document.querySelector('.js-name').innerHTML = order.name == null ? '-' : order.name;
        document.querySelector('.js-email').innerHTML = order.email == null ? '-' : order.email;
        document.querySelector('.js-tel').innerHTML = order.tel == null ? '-' : order.tel;
        document.querySelector('.js-description').innerHTML = order.description == null ? '-' : order.description.replace(/(?:\n)/g, '<br/>');
    }

    if (htmlLockerEditOrder) {
        document.querySelector('.js-orderid').value = order.orderid;
        document.querySelector('.js-name').value = order.name;
        document.querySelector('.js-email').value = order.email;
        document.querySelector('.js-tel').value = order.tel;
        document.querySelector('.js-description').value = order.description;
    }
};

const showLockerCode = function (data) {
    document.querySelector('.js-code').value = data.credentials.code;
};

//#endregion

//#region ***  Callback-No Visualisation - callback___  ***********

// Callback authentication
const callbackLogin = function (data) {
    localStorage.setItem('token', data.access_token);
    window.location.href = 'index.html';
};
const callbackLoginFailed = function (data) {
    if (data.status === 401) document.querySelector('.js-error').innerHTML = 'Gebruikersnaam en/of wachtwoord zijn verkeerd!';
    document.querySelector('.js-password').value = '';
};
const callbackUserIsLoggedIn = function (data) {
    console.log(`${data.username} is logged in`);
};
const callbackUserIsNotLoggedIn = function (data) {
    if (data.status == 401) {
        localStorage.removeItem('token');
        window.location.href = `http://${window.location.hostname}/login.html`;
    }
};

// Callback form set code
const callbackSetCode = function () {
    window.location.href = `http://${window.location.hostname}/locker?lockerid=${lockerId}`;
};

// Callback form set status
const callbackSetStatus = function () {
    window.location.href = `http://${window.location.hostname}/locker?lockerid=${lockerId}`;
};

// Callback form edit order
const callbackEditOrder = function () {
    window.location.href = `http://${window.location.hostname}/locker/bestelling.html?lockerid=${lockerId}`;
};

// Callback order deleted
const callbackDeleteOrder = function () {
    getLockerOrder(lockerId);
};

// Callback locker open
const callbackSuccessfull = function () { };

// Callback error
const callbackError = function (data) {
    console.log(data);
    if (data.status == 422) {
        localStorage.removeItem('token');
        window.location.href = `http://${window.location.hostname}/login.html`;
    }
};

//#endregion

//#region ***  Data Access - get___                     ***********

// Authentication
const validateUser = function () {
    handleData(`http://${window.location.hostname}:5000/api/v1/users/validate`, callbackUserIsLoggedIn, callbackUserIsNotLoggedIn, 'GET', null, token);
};

// Lockers
const getLockers = function () {
    handleData(`http://${window.location.hostname}:5000/api/v1/lockers`, showLockers, callbackError, 'GET', null, token);
};
const getLocker = function (id) {
    handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${id}`, showLocker, callbackError, 'GET', null, token);
};
const getLockerStatus = function (id) {
    handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${id}/status`, showLockerStatus, callbackError, 'GET', null, token);
};
const getLockerStatuses = function () {
    handleData(`http://${window.location.hostname}:5000/api/v1/lockers/statuses`, showLockerStatuses, callbackError, 'GET', null, token);
};
const getLockerOrder = function (id) {
    handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${id}/order`, showLockerOrder, callbackError, 'GET', null, token);
};
const getLockerCredentials = function (id) {
    handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${id}/code`, showLockerCode, callbackError, 'GET', null, token);
};
const getOrderById = function (id) {
    handleData(`http://${window.location.hostname}:5000/api/v1/orders/${id}`, showLockerOrder, callbackError, 'GET', null, token);
};

// History
const getHistoryTemperature = function () {
    handleData(`http://${window.location.hostname}:5000/api/v1/history/temperature`, showHistoryTemperature, callbackError, 'GET', null, token);
};
const getHistoryDetection = function () {
    handleData(`http://${window.location.hostname}:5000/api/v1/history/detection`, showHistoryDetection, callbackError, 'GET', null, token);
};
const getHistoryLocks = function () {
    handleData(`http://${window.location.hostname}:5000/api/v1/history/locks`, showHistoryLocks, callbackError, 'GET', null, token);
};

//#endregion

//#region ***  Event Listeners - listenTo___            ***********

// Toggle navigation
const listenToNavToggle = function () {
    document.querySelector('.js-nav-toggle').addEventListener('click', function () {
        document.querySelector('.js-nav').classList.toggle('c-header__nav--active');
    });
};

// Logout
const listenToLogout = function () {
    document.querySelector('.js-logout').addEventListener('click', function (e) {
        localStorage.removeItem('token');
        window.location.href = `http://${window.location.hostname}/login.html`;
    });
};

// Login form
const listenToFormLogin = function () {
    const form = document.querySelector('.js-form-login');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const body = JSON.stringify({
            username: document.querySelector('.js-username').value,
            password: document.querySelector('.js-password').value,
        });
        handleData(`http://${window.location.hostname}:5000/api/v1/login`, callbackLogin, callbackLoginFailed, 'POST', body, token);
    });
};

// Set locker code form
const listenToFormSetCode = function () {
    const form = document.querySelector('.js-form-set-code');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const body = JSON.stringify({
            code: form.querySelector('.js-code').value
        });
        handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${lockerId}/code`, callbackSetCode, callbackError, 'PUT', body, token);
    });

    form.addEventListener('reset', function (e) {
        e.preventDefault();
        window.location.href = `http://${window.location.hostname}/locker?lockerid=${lockerId}`;
    });

    form.querySelector('.js-button-renew-code').addEventListener('click', function () {
        let code = '';
        for (let i = 0; i < 8; i++) code += Math.floor(Math.random() * 10).toString();
        form.querySelector('.js-code').value = code;
    });
};

// Set locker status form
const listenToFormSetStatus = function () {
    const form = document.querySelector('.js-form-set-status');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const body = JSON.stringify({
            status: form.querySelector('.js-status').value
        });
        handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${lockerId}/status`, callbackSetStatus, callbackError, 'PUT', body, token);
    });

    form.addEventListener('reset', function (e) {
        e.preventDefault();
        window.location.href = `http://${window.location.hostname}/locker?lockerid=${lockerId}`;
    });
};

// Edit order form
const listenToFormEditOrder = function () {
    const form = document.querySelector('.js-form-edit-order');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const body = JSON.stringify({
            orderid: form.querySelector('.js-orderid').value,
            name: form.querySelector('.js-name').value,
            email: form.querySelector('.js-email').value,
            tel: form.querySelector('.js-tel').value,
            description: form.querySelector('.js-description').value
        });
        handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${lockerId}/order`, callbackEditOrder, callbackError, 'PUT', body, token);
    });

    form.addEventListener('reset', function (e) {
        e.preventDefault();
        window.location.href = `http://${window.location.hostname}/locker/bestelling.html?lockerid=${lockerId}`;
    });

    form.querySelector('.js-orderid').addEventListener('input', function () {
        const orderid = form.querySelector('.js-orderid');
        if (orderid.checkValidity()) getOrderById(orderid.value);
    });
};

// Open locker modal
const listenToModalOpenLocker = function () {
    const modal = document.querySelector('.js-modal-open-locker');

    modal.querySelector('.js-ok').addEventListener('click', function () {
        modal.classList.remove('c-modal--active');
        handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${lockerId}/lock/open`, callbackSuccessfull, callbackError, 'POST', null, token);
    });

    modal.querySelector('.js-cancel').addEventListener('click', function () {
        modal.classList.remove('c-modal--active');
    });

    document.querySelector('.js-show-modal-open-locker').addEventListener('click', function () {
        modal.classList.add('c-modal--active');
    });
};

// Delete order modal
const listenToModalDeleteOrder = function () {
    const modal = document.querySelector('.js-modal-delete-order');

    document.querySelector('.js-show-modal-delete-order').addEventListener('click', function () {
        modal.classList.add('c-modal--active');
    });

    modal.querySelector('.js-ok').addEventListener('click', function () {
        modal.classList.remove('c-modal--active');
        handleData(`http://${window.location.hostname}:5000/api/v1/lockers/${lockerId}/order`, callbackDeleteOrder, callbackError, 'DELETE', null, token);
    });

    modal.querySelector('.js-cancel').addEventListener('click', function () {
        modal.classList.remove('c-modal--active');
    });
};

// Delete order modal
const listenToModalShutdown = function () {
    const modal = document.querySelector('.js-modal-shutdown');

    modal.querySelector('.js-ok').addEventListener('click', function () {
        handleData(`http://${window.location.hostname}:5000/api/v1/shutdown`, callbackSuccessfull, callbackError, 'POST', null, token);
    });

    modal.querySelector('.js-cancel').addEventListener('click', function () {
        modal.classList.remove('c-modal--active');
    });

    document.querySelector('.js-shutdown').addEventListener('click', function () {
        modal.classList.add('c-modal--active');
    });
};

// Sockets
const listenToSockets = function () {

    socket.on('connect', function () {
        console.log('Verbonden met socket webserver');

        if (htmlIndex != null | htmlHistoriek != null) {
            socket.emit('F2B_current_temperature');
            socket.emit('F2B_last_detection');
        }
    });

    socket.on('B2F_current_temperature', function (data) {
        const currentTemperature = data.temperature;

        if (htmlIndex != null | htmlHistoriek != null) showCurrentTemperature(currentTemperature);
        if (htmlHistoriek) getHistoryTemperature();
    });

    socket.on('B2F_last_detection', function (data) {
        const lastDetection = JSON.parse(data).lastDetection;

        if (htmlIndex != null | htmlHistoriek != null) {
            // Update last detection every second
            if (updateLastDetection) clearInterval(updateLastDetection);
            updateLastDetection = window.setInterval(function () {
                showLastDetection(lastDetection);
            }, 1000);
        }
        if (htmlHistoriek) getHistoryDetection();
    });

    socket.on('F2B_locker_lock_status', function (data) {
        const lock = JSON.parse(data).lock;

        if (htmlLocker) {
            // Update last lock opened every second
            if (updateLastLockOpened) clearInterval(updateLastLockOpened);
            updateLastLockOpened = window.setInterval(function () {
                showLockLastOpened(lock);
            }, 1000);
        }
        if (htmlIndex != null | htmlLocker != null) showLockStatus(lock);
        if (htmlHistoriek) getHistoryLocks();
    });

};

//#endregion

//#region ***  Init / DOMContentLoaded                  ***********

const init = function () {

    htmlIndex = document.querySelector('.js-page-index');
    htmlLogin = document.querySelector('.js-page-login');
    htmlHistoriek = document.querySelector('.js-page-historiek');
    htmlLocker = document.querySelector('.js-page-locker');
    htmlLockerCode = document.querySelector('.js-page-locker-set-code');
    htmlLockerStatus = document.querySelector('.js-page-locker-set-status');
    htmlLockerOrder = document.querySelector('.js-page-locker-order');
    htmlLockerEditOrder = document.querySelector('.js-page-locker-edit-order');

    // Authentication
    token = localStorage.getItem('token');
    if (token) validateUser();
    else if (htmlLogin == null) window.location.href = `http://${window.location.hostname}/login.html`;

    // Get current locker
    const urlParams = new URLSearchParams(window.location.search);
    lockerId = urlParams.get('lockerid');

    // Listen to sockets
    listenToSockets();

    // Listen to nav toggel
    listenToNavToggle();

    // Logout
    if (document.querySelector('.js-logout')) {
        listenToLogout();
    }

    // Shutdown
    if (document.querySelector('.js-shutdown')) {
        listenToModalShutdown();
    }

    // Pages
    if (htmlIndex) {
        getLockers();
    }

    if (htmlLogin) {
        listenToFormLogin();
    }

    if (htmlHistoriek) {
        getHistoryTemperature();
        getHistoryDetection();
        getHistoryLocks();
    }

    if (htmlLocker) {
        getLocker(lockerId);
        listenToModalOpenLocker();
    }

    if (htmlLockerCode) {
        getLockerCredentials(lockerId);
        listenToFormSetCode();
        document.querySelector('.js-back').href += `?lockerid=${lockerId}`;
    }

    if (htmlLockerStatus) {
        getLockerStatuses();
        listenToFormSetStatus();
        document.querySelector('.js-back').href += `?lockerid=${lockerId}`;
    }

    if (htmlLockerOrder) {
        getLockerOrder(lockerId);
        listenToModalDeleteOrder();
        document.querySelector('.js-back').href += `?lockerid=${lockerId}`;
        document.querySelector('.js-edit-order').href += `?lockerid=${lockerId}`;
    }

    if (htmlLockerEditOrder) {
        getLockerOrder(lockerId);
        listenToFormEditOrder();
        document.querySelector('.js-back').href += `?lockerid=${lockerId}`;
    }
};
document.addEventListener('DOMContentLoaded', init);

//#endregion
