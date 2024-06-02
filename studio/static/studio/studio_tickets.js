document.addEventListener('DOMContentLoaded', function() {
    const ticketsTable = document.getElementById('ticketsTable');
    let currentPage = 1;



    function fetchTickets(page) {
        fetch(`/box/api/tickets/?page=${page}`)
            .then(response => response.json())
            .then(data => renderTickets(data.tickets));
    }




    function renderTickets(tickets) {
    const tbody = ticketsTable.querySelector('tbody');
    tbody.innerHTML = '';  // Clear existing tickets from tbody
    tickets.forEach(ticket => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${ticket.style1}</td>
            <td>${ticket.style2}</td>
            <td>${ticket.occasion}</td>
            <td>${ticket.notes}</td>
            <td><button onclick="chooseTicket(${ticket.id})">Choose</button></td>
        `;
    });
}





    window.chooseTicket = function(ticketId) {
        // Redirect to studio_items.html with the ticketId
        window.location.href = `/studio/items?ticketId=${ticketId}`;
    };

    document.getElementById('nextPage').addEventListener('click', function() {
        currentPage++;
        fetchTickets(currentPage);
    });

    document.getElementById('prevPage').addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            fetchTickets(currentPage);
        }
    });

    // Initial fetch of tickets
    fetchTickets(currentPage);
});
