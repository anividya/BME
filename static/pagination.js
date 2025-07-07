let rowsPerPage = 5;
let currentPage = 1;
let sortColumn = -1;
let sortDirection = 1; // 1 for ascending, -1 for descending
let filteredData = [...tableData];

function renderTable(data) {
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.assetNumber}</td>
            <td>${row.equipment}</td>
            <td>${row.make}</td>
            <td>${row.model}</td>
            <td>${row.serialNumber}</td>
            <td>${row.department}</td>
            <td>${row.ppmDue}</td>
            <td>${row.warrantyDue}</td>
            <td>${row.status}</td>
            <td>
                <a href="#addwoModal" class="btn btn-warning btn-sm" data-toggle="modal" onclick="wodata_ajax('${row.assetNumber}','${row.equipment}','${row.make}','${row.model}','${row.serialNumber}','${row.department}')">
                <i class="fas fa-info"></i>WO
                </a>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

function filterTable() {
    filteredData = tableData.filter(row => {
        return [...document.getElementsByClassName('search-box')].every((input, index) => {
            const value = input.value.toLowerCase();
            return Object.values(row)[index].toLowerCase().includes(value);
        });
    });
    currentPage = 1;
    paginateTable(filteredData);
}

function sortTable(columnIndex) {
    if (sortColumn === columnIndex) {
        sortDirection *= -1;
    } else {
        sortColumn = columnIndex;
        sortDirection = 1;
    }
    filteredData.sort((a, b) => {
        const cellA = Object.values(a)[columnIndex];
        const cellB = Object.values(b)[columnIndex];
        if (cellA < cellB) return -1 * sortDirection;
        if (cellA > cellB) return 1 * sortDirection;
        return 0;
    });
    document.querySelectorAll('.sort-arrow').forEach(arrow => arrow.innerHTML = '&#8597;');
    document.getElementById(`sort-arrow-${columnIndex}`).innerHTML = sortDirection === 1 ? '&#8593;' : '&#8595;';
    paginateTable(filteredData);
}

function paginateTable(data) {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(data.length / rowsPerPage);
    pagination.innerHTML = '';

    const createPageButton = (text, pageNumber, disabled = false) => {
        const button = document.createElement('button');
        button.textContent = text;
        button.disabled = disabled;
        button.addEventListener('click', () => {
            currentPage = pageNumber;
            renderTable(data.slice((pageNumber - 1) * rowsPerPage, pageNumber * rowsPerPage));
            updateTableInfo(data.length, pageNumber);
            paginateTable(data);
        });
        const li = document.createElement('li');
        li.appendChild(button);
        pagination.appendChild(li);
    };

    if (currentPage > 1) {
        createPageButton('Previous', currentPage - 1);
    }

    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        createPageButton(i, i, i === currentPage);
    }

    if (currentPage < totalPages) {
        createPageButton('Next', currentPage + 1);
    }

    renderTable(data.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage));
    updateTableInfo(data.length, currentPage);
}

function updateTableInfo(totalEntries, page) {
    const startEntry = (page - 1) * rowsPerPage + 1;
    const endEntry = Math.min(page * rowsPerPage, totalEntries);
    const tableInfo = document.getElementById('tableInfo');
    tableInfo.textContent = `Showing ${startEntry} to ${endEntry} of ${totalEntries} entries`;
}

function changeEntriesPerPage() {
    rowsPerPage = parseInt(document.getElementById('entriesCount').value, 10);
    currentPage = 1;
    paginateTable(filteredData);
}

document.addEventListener('DOMContentLoaded', () => {
    paginateTable(tableData);
});

