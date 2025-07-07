let rowsPerPage = 5;
let currentPage = 1;
let sortColumn = -1;
let sortDirection = 1; // 1 for ascending, -1 for descending
let filteredData = [...tableData];

console.log(UserGroup);
const buttonText = (UserGroup === 'MANAGEMENT' || UserGroup === 'BMEADMIN') ? "View" : "VIEW";
console.log(buttonText);
let modalText;

if (UserGroup === 'BMEADMIN' && Status === 'REQUESTED') {
    modalText = 'pr_ModalBM';
    console.log("REQ")
} else {
    modalText = (UserGroup === 'BMEADMIN') ? 'pr_ModalBME' : 'pr_ModalAdmin';
    console.log("NP")
}

function renderTable(data) {
    const tableBody = document.getElementById('prTableBody');
    tableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.PR_No}</td>
            <td>${row.Asset_Name}</td>
            <td>${row.Need}</td>
            <td>${row.Features}</td>
            <td>${row.Requested_Date}</td>
            <td>${row.Department}</td>
            <td>${row.Status}</td>
            <td> <a href="#pr_ModalView" onclick="prModal('${row.PR_No}','${row.Asset_Name}','${row.Need}','${row.Features}','${row.Requested_Date}','${row.Department}','${row.Status}')" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                    <i class="fas fa-info"></i>View</a>
            </td>`;
        tableBody.appendChild(tr);
    });
}

function prModal(PR_No, Asset_Name, Need, Features, Requested_Date, Department, Status) {
    console.log("prModalfunction")

    if (UserGroup === 'BMEADMIN' && Status === 'REQUESTED') {
        modalText = 'pr_ModalBM';
        console.log("REQ")
    } else {
        modalText = (UserGroup === 'BMEADMIN') ? 'pr_ModalBME' : 'pr_ModalAdmin';
        console.log("NP")
    }

    document.getElementById("PR_No").value = PR_No;
    document.getElementById("Asset_Name").value = Asset_Name;
    document.getElementById("Need").value = Need;
    document.getElementById("Features").value = Features;
    console.log(Requested_Date);
    const date = Requested_Date;
    document.getElementById("Requested_Date").value = Requested_Date;
    document.getElementById("Department").value = Department;
    document.getElementById("Status").value = Status;
}

function saveState() {
    const state = {
        currentPage,
        sortColumn,
        sortDirection,
        filterValues: [...document.getElementsByClassName('search-box')].map(input => input.value)
    };
    localStorage.setItem('prtableState', JSON.stringify(state));
}

function loadState() {
    const savedState = localStorage.getItem('prtableState');
    if (savedState) {
        const state = JSON.parse(savedState);
        currentPage = state.currentPage || 1;
        sortColumn = state.sortColumn;
        sortDirection = state.sortDirection;

        const filterInputs = document.getElementsByClassName('search-box');
        state.filterValues.forEach((value, index) => {
            if (filterInputs[index]) {
                filterInputs[index].value = value;
            }
        });

        filterTable();
        applySorting();
    }
}

function applySorting() {
    if (sortColumn !== -1) {
        filteredData.sort((a, b) => {
            let cellA = Object.values(a)[sortColumn];
            let cellB = Object.values(b)[sortColumn];
            let comparison = 0;

            if (sortColumn === 6) { // Handle date column
                const dateA = parseCustomDate(cellA);
                const dateB = parseCustomDate(cellB);
                comparison = dateA - dateB;
            } else {
                // Handle string comparison
                cellA = typeof cellA === 'string' ? cellA.toLowerCase() : cellA;
                cellB = typeof cellB === 'string' ? cellB.toLowerCase() : cellB;
                if (cellA < cellB) comparison = -1;
                else if (cellA > cellB) comparison = 1;
                else comparison = 0;
            }

            return comparison * sortDirection;
        });
    }
    paginateTable(filteredData);
    setSortArrow();
}

function setSortArrow() {
    document.querySelectorAll('.sort-arrow').forEach((arrow, index) => {
        arrow.innerHTML = '&#8597;';
        if (index === sortColumn) {
            arrow.innerHTML = sortDirection === 1 ? '&#8593;' : '&#8595;';
        }
    });
}

function filterTable() {
    filteredData = tableData.filter(row => {
        return [...document.getElementsByClassName('search-box')].every((input, index) => {
            const value = input.value.toLowerCase();
            return Object.values(row)[index].toLowerCase().includes(value);
        });
    });
    // After filtering, apply sorting and pagination
    applySorting();
    paginateTable(filteredData);
    saveState();  // Save state after filtering
}

function sortTable(columnIndex) {
    if (sortColumn === columnIndex) {
        sortDirection *= -1;
    } else {
        sortColumn = columnIndex;
        sortDirection = 1;
    }
    applySorting();
    setSortArrow(); // Update the sort arrows after sorting
    saveState(); // Save state after sorting
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
            saveState(); // Save the current page state
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

// Save filter state when any search input changes
document.querySelectorAll('.search-box').forEach(input => {
    input.addEventListener('input', () => {
        filterTable();  // Trigger filtering and save state
    });
});

// Load state on page load
document.addEventListener('DOMContentLoaded', () => {
    loadState();  // Load saved filtering, pagination, and sorting state
    setSortArrow(); // Set the sort arrow based on loaded state
    paginateTable(filteredData); // Ensure the data is displayed correctly based on saved current page
});

// Function to download the table data as an Excel file
function downloadTableAsExcel() {
    const data = filteredData.map(row => ({
        'PR_No': row.PR_No,
        'Asset Name': row.Asset_Name,
        'Need': row.Need,
        'Features': row.Features,
        'Requested_Date': row.Requested_Date,
        'Department': row.Department,
        'Status': row.Status,
    }));

    // Convert data to CSV format
    const csvRows = [];
    const headers = Object.keys(data[0]);
    csvRows.push(headers.join(',')); // Add headers

    for (const row of data) {
        csvRows.push(headers.map(field => JSON.stringify(row[field], (key, value) => value === null ? '' : value)).join(','));
    }

    // Create a blob and download it
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', 'PRTable_data.csv');
    a.style.visibility = 'hidden';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
// Attach the event listener to the button
document.getElementById('downloadBtn').addEventListener('click', downloadTableAsExcel);

function formatDateToDatetimeLocal(dateInput) {
    const date = new Date(dateInput);  // Convert string to Date object
    if (isNaN(date)) {
        console.error("Invalid date:", dateInput);
        return ""; // Return empty string if invalid
    }

    const pad = num => num.toString().padStart(2, '0');

    const yyyy = date.getFullYear();
    const MM = pad(date.getMonth() + 1);
    const dd = pad(date.getDate());
    const hh = pad(date.getHours());
    const mm = pad(date.getMinutes());

    return `${yyyy}-${MM}-${dd}T${hh}:${mm}`;
}

function parseCustomDate(dateStr) {
    // Clean up the date string for parsing
    let cleaned = dateStr.replace(/\./g, '') // Remove periods in month and time
        .replace(/, /g, ' ') // Replace commas with spaces
        .replace(/(a|p)m/gi, (match) => match.toUpperCase());
    return new Date(cleaned);
}
