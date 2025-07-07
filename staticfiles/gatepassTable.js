let rowsPerPage = 5;
let currentPage = 1;  // Default to page 1
let sortColumn = -1;
let sortDirection = 1; // 1 for ascending, -1 for descending
let filteredData = [...tableData];

// Save current state (pagination, sorting, filtering) to localStorage
function saveState() {
    const state = {
        currentPage,
        sortColumn,
        sortDirection,
        filterValues: [...document.getElementsByClassName('search-box')].map(input => input.value)
    };
    localStorage.setItem('gttableState', JSON.stringify(state));
}

// Load the saved state from localStorage
function loadState() {
    const savedState = localStorage.getItem('gttableState');
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

            // Special handling for Gatepass_Number (assume it's in column 0)
            if (sortColumn === 0) {
                const numA = parseInt(cellA.split('-')[1], 10) || 0; // Extract numeric part
                const numB = parseInt(cellB.split('-')[1], 10) || 0; // Extract numeric part
                return (numA - numB) * sortDirection;
            }

            // Default sorting for other columns
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
    const tableBody = document.getElementById('gttableBody');
    const userRole = document.getElementById('UserRole').value;
    console.log(userRole);
    tableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td>${row.passid}</td>
        <td>${row.asset}</td>
        <td>${row.desc}</td>
        <td>${row.outdate}</td>
        <td>${row.indate}</td>
        <td>${row.status}</td>
        <td>
            ${userRole === "MANAGEMENT" && row.status === "SEND_OUT"
                ? `<a href="#gatePassViewModal1" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                            <i class="fas fa-info"></i>VIEW
                    </a>`
                : userRole === "MANAGEMENT" && row.status === "ADMIN_Approval_Pending"
                    ? `<a href="#gatePassViewModal2" onclick="modal2ajax('${row.passid}')" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                            <i class="fas fa-info"></i>Approve
                    </a>`
                    : userRole === "BMEADMIN" && row.status === "SEND_OUT" || userRole === "BMEADMIN" && row.status === "ADMIN_Approval_Pending"
                        ? `<a href="#gatePassViewModal1" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                            <i class="fas fa-info"></i>VIEW
                    </a>`
                        : userRole === "BMEADMIN" && row.status === "Approved"
                            ? `<a href="#gatePassViewModal3" onclick="modal3ajax('${row.passid}')" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                                <i class="fas fa-info"></i>SEND
                    </a>`
                            : userRole === "MANAGEMENT" && row.status === "Approved"
                                ? `<a href="#gatePassViewModal1" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                                    <i class="fas fa-info"></i>VIEW
                    </a>`
                                : userRole === "NURSING"
                                    ? `<a href="#gatePassViewModal1" class="edit-btn btn btn-warning btn-sm" data-toggle="modal">
                                            <i class="fas fa-info"></i>VIEW
                    </a>`
                                    : ''
            }       
        </td>`;
        tableBody.appendChild(tr);
    });
}

function filterTable() {
    // Always filter from the original `tableData`
    filteredData = tableData.filter(row => {
        return [...document.getElementsByClassName('search-box')].every((input, index) => {
            const value = input.value.toLowerCase();
            return Object.values(row)[index].toLowerCase().includes(value);
        });
    });

    // After filtering, apply sorting and reset pagination to the first page
    currentPage = 1; // Reset to the first page after filtering
    applySorting();
    paginateTable(filteredData);
    saveState(); // Save state after filtering
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

function wodata_ajax(passid, asset, desc, outdate, indate, status) 
{

    //var field = document.getElementById("workassetid");
    //field.value = assetid;
    //var field4 = document.getElementById("assetname");
    //field4.value = equipment;
    // var field5 = document.getElementById("make");
    //field5.value = make;
    //var field6 = document.getElementById("model");
    //field6.value = model;
    //var field8 = document.getElementById("slno");
    // field8.value = serialNumber;
    //var field8 = document.getElementById("dept");
    //field8.value = department;
    $.ajax({
        url: '/addwo_ajax/',
        type: 'GET',
        dataType: 'json',
        success: function (wodata) {
            // update the form field with the returned data
            console.log(gtp_data.pass_id);
            //var field2 = document.getElementById("workid");
            //field2.value = wodata.key;
            //var field3 = document.getElementById("workdate");
            //field3.value = wodata.date;
            //var field9 = document.getElementById("stat");
            //field9.value = "RELEASED";
        }
    });
}
// Function to download the table data as an Excel file
function downloadTableAsExcel() {
    const data = filteredData.map(row => ({
        'Asset Number': row.assetNumber,
        'Equipment': row.equipment,
        'Make': row.make,
        'Model': row.model,
        'Serial Number': row.serialNumber,
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

document.getElementById('gttableBody').addEventListener('click', function (event) {
    if (event.target.closest('.edit-btn')) {
        const row = event.target.closest('tr');
        const id = row.querySelector('td').textContent.trim(); // Extract and clean the ID
        //const id = row.querySelector('td').textContent;
        console.log('Row ID:', id);
        var field2 = document.getElementById("gatePassNumber");
        field2.value = id;
        let rl = `/gatePass_ajax/${id}/`;
        $.ajax({
            url: rl,
            type: 'GET',
            dataType: 'json',
            success: function (wodata) {
                // update the form field with the returned data
                console.log(wodata);

                var item_field = document.getElementById("item");
                item_field.value = wodata.gtp_data.asset_name;

                var sendOut_field = document.getElementById("sendOutDate");
                let out_date = wodata.gtp_data.out_date;
                let formattedDate = out_date.replace("Z", "").slice(0, 16);
                sendOut_field.value = formattedDate;

                var assetNumber_field = document.getElementById("assetNumber");
                assetNumber_field.value = wodata.gtp_data.asset;

                var serialNumber_field = document.getElementById("serialNumber");
                serialNumber_field.value = wodata.gtp_data.serial;
                

                var collectedBy_field = document.getElementById("collectedBy");
                collectedBy_field.value = wodata.gtp_data.collector_name;

                var sendTo_field = document.getElementById("sendTo");
                sendTo_field.value = wodata.gtp_data.send_to;

                var sendBy_field = document.getElementById("sendBy");
                sendBy_field.value = wodata.gtp_data.sender_name;

                var contactNumber_field = document.getElementById("contactNumber");
                contactNumber_field.value = wodata.gtp_data.contact_num;
            }
        });
    }
});
// Attach the event listener to the button

//document.getElementById('downloadBtn').addEventListener('click', downloadTableAsExcel);

function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

function saveStatus() {
    var pass_id = document.getElementById('gatePassNumber').value;

    $.ajax({
        type: 'POST',
        url: 'gtSend_ajax', // Django view URL
        data: {
            'pass_id': pass_id,
            'csrfmiddlewaretoken': getCSRFToken(), // Dynamically get CSRF token
        },
        success: function (response) {
            if (response.success) {
                $('#gatePassViewModal').modal('hide'); // Close modal
            } else {
                alert("Error saving data");
            }
        },
        error: function () {
            alert("An error occurred");
        }
    });
}

function modal2ajax(id) {
    //var field2 = document.getElementById("gatePassNumber");
    //field2.value = id;
    console.log(id);
    console.log("modal2ajax");
    let rl = `/gatePass_ajax/${id}/`;
    $.ajax({
        url: rl,
        type: 'GET',
        dataType: 'json',
        success: function (wodata) {
            // update the form field with the returned data
            console.log(wodata);

            var field2 = document.getElementById("gatePassNumber3");
            var field1 = document.getElementById("pass_id");
            field1.value = wodata.gtp_data.pass_id;
            field2.value = wodata.gtp_data.pass_id;

            var field3 = document.getElementById("item2");
            field3.value = wodata.gtp_data.asset_name;

            var field4 = document.getElementById("sendOutDate2");
            let out_date = wodata.gtp_data.out_date;
            let formattedDate = out_date.replace("Z", "").slice(0, 16);
            field4.value = formattedDate;

            var field5 = document.getElementById("assetNumber2");
            field5.value = wodata.gtp_data.asset;

            var field6 = document.getElementById("serialNumber2");
            field6.value = wodata.gtp_data.serial;

            var field7 = document.getElementById("collectedBy2");
            field7.value = wodata.gtp_data.collector_name;

            var field9 = document.getElementById("sendTo2");
            field9.value = wodata.gtp_data.send_to;

            var field10 = document.getElementById("sendBy2");
            field10.value = wodata.gtp_data.sender_name;

            var field10 = document.getElementById("contactNumber2");
            field10.value = wodata.gtp_data.contact_num;
        }
    });
}

function modal3ajax(id) {
    //var field2 = document.getElementById("gatePassNumber");
    //field2.value = id;
    console.log(id);
    console.log("modal3ajax");
    let rl = `/gatePass_ajax/${id}/`;
    $.ajax({
        url: rl,
        type: 'GET',
        dataType: 'json',
        success: function (wodata) {
            // update the form field with the returned data
            console.log(wodata);

            var field2 = document.getElementById("gatePassNumber3");
            var field1 = document.getElementById("pass_id");
            field1.value = wodata.gtp_data.pass_id;
            field2.value = wodata.gtp_data.pass_id;

            var field3 = document.getElementById("item3");
            field3.value = wodata.gtp_data.asset_name;

            var field4 = document.getElementById("sendOutDate3");
            let out_date = wodata.gtp_data.out_date;
            let formattedDate = out_date.replace("Z", "").slice(0, 16);
            field4.value = formattedDate;

            var field5 = document.getElementById("assetNumber3");
            field5.value = wodata.gtp_data.asset;

            var field6 = document.getElementById("serialNumber3");
            field6.value = wodata.gtp_data.serial;

            var field7 = document.getElementById("collectedBy3");
            field7.value = wodata.gtp_data.collector_name;

            var field9 = document.getElementById("sendTo3");
            field9.value = wodata.gtp_data.send_to;

            var field10 = document.getElementById("sendBy3");
            field10.value = wodata.gtp_data.sender_name;

            var field10 = document.getElementById("contactNumber3");
            field10.value = wodata.gtp_data.contact_num;
        }
    });
}