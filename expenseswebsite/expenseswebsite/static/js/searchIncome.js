const searchField = document.querySelector('#searchField');
const originalTable = document.getElementById('originalTable');
const filteredTable = document.getElementById('filteredTable');
const paginationContainer = document.querySelector('.pagination-container');

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value.trim();

    console.log('Search value:', searchValue);

    if (searchValue.length > 0) {
        fetch("search-income", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log('Data received from server:', data);

            if (data.length === 0) {
                console.log('No results found.');
                filteredTable.innerHTML = '<p>No results found</p>';
                originalTable.style.display = 'none';
                filteredTable.style.display = 'block';
                paginationContainer.style.display = 'none';
            } else {
                let html = '<table class="table table-striped table-hover table-group-divider"><thead class="table-group-divider"><tr><th>Amount (Currency)</th><th>Source</th><th>Description</th><th>Date</th><th></th></tr></thead><tbody>';
                data.forEach(income => {
                    html += `<tr><td>${income.amount}</td><td>${income.source_name}</td><td>${income.description}</td><td>${income.income_date}</td><td><a href="{% url 'income-edit' %}?id=${income.id}" class="btn btn-secondary">Edit</a></td></tr>`;
                });
                html += '</tbody></table>';
                filteredTable.innerHTML = html;
                originalTable.style.display = 'none';
                filteredTable.style.display = 'block';
                paginationContainer.style.display = 'block';
            }
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });
    } else {
        originalTable.style.display = 'block';
        filteredTable.style.display = 'none';
        filteredTable.innerHTML = ''; 
        paginationContainer.style.display = 'block';
    }
});
