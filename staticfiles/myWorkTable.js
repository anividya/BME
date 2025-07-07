let rowsPerPage = 5;
let currentPage = 1;
let sortColumn = -1;
let sortDirection = 1; // 1 for ascending, -1 for descending
let filteredData = [...tableData];

console.log(UserGroup);
//const buttonText = (UserGroup === 'BMEADMIN' || UserGroup === 'BMESTAFF') ? 'Take_WO' : UserGroup === 'NURSING' ? 'View' : 'View';
const buttonText = (UserGroup === 'BMEADMIN' || UserGroup === 'BMESTAFF') ? "Attend" : "View";
const modalText = (UserGroup === 'BMEADMIN' || UserGroup === 'BMESTAFF') ? 'viewwoModalBME' : 'woviewonly';
//const modalText = 'viewwoModalBME';
function saveState() {
    const state = {
        currentPage,
        sortColumn,
        sortDirection,
        filterValues: [...document.getElementsByClassName('search-box')].map(input => input.value)
    };
    localStorage.setItem('myWorktableState', JSON.stringify(state));
}

// Load the saved state from localStorage
function loadState() {
    const savedState = localStorage.getItem('myWorktableState');
    if (savedState) {
        const state = JSON.parse(savedState);
        currentPage = state.currentPage || 1;  // Load the saved current page
        sortColumn = state.sortColumn;
        sortDirection = state.sortDirection;

        // Restore filter inputs
        const filterInputs = document.getElementsByClassName('search-box');
        state.filterValues.forEach((value, index) => {
            if (filterInputs[index]) {
                filterInputs[index].value = value;
            }
        });

        // Apply filtering, sorting, and pagination based on loaded state
        filterTable();
        applySorting();
    }
}

function applySorting() {
    if (sortColumn !== -1) {
        filteredData.sort((a, b) => {
            const cellA = Object.values(a)[sortColumn];
            const cellB = Object.values(b)[sortColumn];
            if (cellA < cellB) return -1 * sortDirection;
            if (cellA > cellB) return 1 * sortDirection;
            return 0;
        });
    }
    paginateTable(filteredData); // This will paginate using the saved `currentPage`
}

function setSortArrow() {
    document.querySelectorAll('.sort-arrow').forEach((arrow, index) => {
        arrow.innerHTML = '&#8597;'; // Reset all arrows to neutral
        if (index === sortColumn) {
            arrow.innerHTML = sortDirection === 1 ? '&#8593;' : '&#8595;'; // Set arrow based on sort direction
        }
    });
}

function renderTable(data) {
    const tableBody = document.getElementById('myWorktableBody');
    tableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.Work_ID}</td>
            <td>${row.Asset_Number}</td>
            <td>${row.Equipment}</td>
            <td>${row.model}</td>
            <td>${row.Description}</td>
            <td>${row.Department}</td>
            <td>${row.Work_Date}</td>
            <td>${row.Requested_By}</td>
            <td>${row.Status}</td>
            <td>
                <a href="attendwo/${row.Work_ID}" class="btn btn-warning btn-sm">
                <i class="fas fa-info"></i>${buttonText}
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
        'Work ID': row.Work_ID,
        'Asset Number': row.Asset_Number,
        'Equipment': row.Equipment,
        'Model': row.model,
        'Compliant': row.Description,
        'Department': row.Department,
        'Work Date': row.Work_Date,
        'Requested By': row.Requested_By,
        'Status': row.status,
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
    a.setAttribute('download', 'table_data.csv');
    a.style.visibility = 'hidden';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
// Attach the event listener to the button
document.getElementById('downloadBtn').addEventListener('click', downloadTableAsExcel);