$(document).ready(function () {
    // Initialize table state
    let currentPage = 1;
    let pageLength = 10;
    let sortColumn = 'assetid';
    let sortDirection = 'asc';
    let searchTerms = ['', '', '', '', '', '', '', '']; // For each column

    // Load state from localStorage
    function loadState() {
        const state = localStorage.getItem('assetTableState');
        if (state) {
            try {
                const parsed = JSON.parse(state);
                currentPage = parsed.currentPage || 1;
                pageLength = parsed.pageLength || 10;
                sortColumn = parsed.sortColumn || 'assetid';
                sortDirection = parsed.sortDirection || 'asc';
                searchTerms = parsed.searchTerms || ['', '', '', '', '', '', '', ''];

                // Apply to UI
                $('#pageLengthSelect').val(pageLength);
                $('.search-input').each(function (index) {
                    $(this).val(searchTerms[index] || '');
                });
            } catch (e) {
                console.error('Error loading state:', e);
            }
        }
    }

    // Save state to localStorage
    function saveState() {
        const state = {
            currentPage: currentPage,
            pageLength: pageLength,
            sortColumn: sortColumn,
            sortDirection: sortDirection,
            searchTerms: searchTerms
        };
        localStorage.setItem('assetTableState', JSON.stringify(state));
    }

    // Function to fetch data from server
    function fetchData() {
        const assetcat = document.getElementById("assetcat");
        console.log(assetcat.value);
        const params = {
            start: (currentPage - 1) * pageLength,
            length: pageLength,
            sort_column: sortColumn,
            sort_direction: sortDirection,
            search_terms: JSON.stringify(searchTerms),
            assettype: assetcat.value
        };

        // Show loading indicator
        $('#assetTableBody').html('<tr><td colspan="9" class="text-center"><div class="spinner-border text-primary" role="status"></div></td></tr>');

        $.ajax({
            url: '{% url "asset_data" %}',
            type: 'GET',
            data: params,
            success: function (response) {
                renderTable(response);
                renderPagination(response);
                saveState();
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                $('#assetTableBody').html('<tr><td colspan="9" class="text-center text-danger">Error loading data</td></tr>');
            }
        });
    }

    // Function to render table body
    function renderTable(data) {
        const tbody = $('#assetTableBody');
        tbody.empty();

        if (data.data.length === 0) {
            tbody.append('<tr><td colspan="9" class="text-center">No matching records found</td></tr>');
            return;
        }

        $.each(data.data, function (i, asset) {
            const row = $('<tr>');
            row.append($('<td>').text(asset.assetid));
            row.append($('<td>').text(asset.assetname));
            row.append($('<td>').text(asset.asset_make));
            row.append($('<td>').text(asset.asset_model));
            row.append($('<td>').text(asset.slno));
            row.append($('<td>').text(asset.dept));
            row.append($('<td>').text(asset.pmstat));
            row.append($('<td>').text(asset.calstat));
            const actionBtn = $('<button>').addClass('btn btn-sm btn-info view-btn').text('View').attr('data-id', asset.assetid);
            row.append($('<td>').append(actionBtn));
            tbody.append(row);
        });

        // Update table info
        const start = (currentPage - 1) * pageLength + 1;
        const end = start + data.data.length - 1;
        const total = data.recordsFiltered;
        $('#assetTableInfo').text(`Showing ${start} to ${end} of ${total} entries`);
    }

    // Function to render pagination
    function renderPagination(data) {
        const pagination = $('#assetTablePagination');
        pagination.empty();

        const totalPages = Math.ceil(data.recordsFiltered / pageLength);
        if (totalPages <= 1) return;

        // Previous button
        const prevLi = $('<li>').addClass('page-item').toggleClass('disabled', currentPage === 1);
        prevLi.append($('<a>').addClass('page-link').attr('href', '#').html('&laquo;').click(function (e) {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                fetchData();
            }
        }));
        pagination.append(prevLi);

        // Page numbers
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageLi = $('<li>').addClass('page-item').toggleClass('active', i === currentPage);
            pageLi.append($('<a>').addClass('page-link').attr('href', '#').text(i).click(function (e) {
                e.preventDefault();
                currentPage = i;
                fetchData();
            }));
            pagination.append(pageLi);
        }

        // Next button
        const nextLi = $('<li>').addClass('page-item').toggleClass('disabled', currentPage === totalPages);
        nextLi.append($('<a>').addClass('page-link').attr('href', '#').html('&raquo;').click(function (e) {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                fetchData();
            }
        }));
        pagination.append(nextLi);
    }

    // Handle sort when clicking on header
    $('th[data-column]').click(function () {
        const column = $(this).data('column');

        // Update sort direction if same column clicked
        if (sortColumn === column) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortColumn = column;
            sortDirection = 'asc';
        }

        // Reset to first page when sorting changes
        currentPage = 1;

        // Update UI
        $('.sort-icon').html('↑↓');
        $(this).find('.sort-icon').html(sortDirection === 'asc' ? '↑' : '↓');

        fetchData();
    });

    // Handle search input
    $('.search-input').on('input', function () {
        const colIndex = $(this).data('column');
        searchTerms[colIndex] = $(this).val();

        // Reset to first page when search changes
        currentPage = 1;

        // Use debounce to prevent too many requests
        clearTimeout($(this).data('timeout'));
        $(this).data('timeout', setTimeout(fetchData, 500));
    });

    // Handle page length change
    $('#pageLengthSelect').change(function () {
        pageLength = parseInt($(this).val());
        currentPage = 1;
        fetchData();
    });

    // Handle view button click
    $(document).on('click', '.view-btn', function () {
        const assetId = $(this).data('id');
        $.ajax({
            url: '{% url "asset_quickview" asset_id="0000" %}'.replace('0000', assetId),
            type: 'GET',
            beforeSend: function () {
                $('#modalContent').html('<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div></div>');
            },
            success: function (response) {
                $('#modalContent').html(response);
                $('#viewAssetModal').modal('show');
            },
            error: function () {
                $('#modalContent').html('<div class="alert alert-danger">Error loading asset details</div>');
            }
        });
    });

    // Initialize
    loadState();
    fetchData();

    // Set initial sort indicator
    $(`th[data-column="${sortColumn}"] .sort-icon`).html(sortDirection === 'asc' ? '↑' : '↓');
});
