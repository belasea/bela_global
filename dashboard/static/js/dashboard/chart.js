// Order Status Chart
const ctx1 = document.getElementById('orderStatusChart').getContext('2d');
    new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Apr'],
        datasets: [
            { label: 'Success', data: [1], backgroundColor: '#0d6efd', barThickness: 60 },
            { label: 'Pending', data: [1], backgroundColor: '#dc3545', barThickness: 60 },
            { label: 'Failed', data: [1], backgroundColor: '#ffc107', barThickness: 60 }
        ]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 1 } }
    }
});

// Sales Revenue Chart
const ctx2 = document.getElementById('salesRevenueChart').getContext('2d');
    new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['Apr'],
        datasets: [{
            data: [560],
            backgroundColor: '#3b82f6',
            borderRadius: 5,
            barThickness: 100
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 600 } }
    }
});