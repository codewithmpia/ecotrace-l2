// Animation des statistiques au chargement
document.addEventListener('DOMContentLoaded', function () {
    updateStatistics();
    createCharts();

    // Animation des cartes statistiques
    const stats = document.querySelectorAll('[class*="text-2xl font-bold"]');
    stats.forEach((stat, index) => {
        stat.style.opacity = '0';
        stat.style.transform = 'translateY(20px)';
        setTimeout(() => {
            stat.style.transition = 'all 0.6s ease-out';
            stat.style.opacity = '1';
            stat.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

function updateStatistics() {
    if (monthlySummary) {
        // Total mensuel
        document.getElementById('totalEmissions').textContent = monthlySummary.total ? monthlySummary.total.toFixed(2) : '0.00';

        // Moyenne quotidienne
        document.getElementById('dailyAverage').textContent = monthlySummary.daily_average ? monthlySummary.daily_average.toFixed(2) : '0.00';

        // Catégorie principale
        if (monthlySummary.by_category) {
            const categories = monthlySummary.by_category;
            const topCategoryKey = Object.keys(categories).reduce((a, b) => categories[a] > categories[b] ? a : b);
            const categoryLabels = {
                transport: 'Transport',
                food: 'Alimentation',
                energy: 'Énergie',
                consumption: 'Consommation'
            };

            document.getElementById('topCategory').textContent = categoryLabels[topCategoryKey] || topCategoryKey;
            document.getElementById('topCategoryValue').textContent = categories[topCategoryKey].toFixed(2) + ' kgCO₂e';
        }
    }
}

function createCharts() {
    // 1. Graphique par catégorie (données actuelles)
    createCurrentCategoryChart();

    // 2. Graphique évolution hebdomadaire
    createWeeklyTrendChart();

    // 3. Graphique comparaison mensuelle par catégorie
    createMonthlyCategoryChart();
}

function createCurrentCategoryChart() {
    if (!categoriesData) return;

    const categoryColors = {
        transport: '#3B82F6', // blue-500
        food: '#F97316', // orange-500
        energy: '#EF4444', // red-500
        consumption: '#8B5CF6' // purple-500
    };

    const categoryLabels = {
        transport: 'Transport',
        food: 'Alimentation',
        energy: 'Énergie',
        consumption: 'Consommation'
    };

    const ctx = document.getElementById('categoryChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoriesData).map(cat => categoryLabels[cat] || cat),
            datasets: [{
                data: Object.values(categoriesData),
                backgroundColor: Object.keys(categoriesData).map(cat => categoryColors[cat] || '#6B7280'),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed.toFixed(2)} kgCO₂e (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createWeeklyTrendChart() {
    if (!weeklyData || weeklyData.length === 0) return;

    const ctx = document.getElementById('weeklyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeklyData.map(day => day.display_date),
            datasets: [{
                label: 'Émissions quotidiennes (kgCO₂e)',
                data: weeklyData.map(day => day.emissions),
                borderColor: '#10B981', // emerald-500
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#10B981',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#10B981',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'kgCO₂e'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Jour'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createMonthlyCategoryChart() {
    if (!monthlySummary || !monthlySummary.by_category) return;

    const categoryColors = {
        transport: '#3B82F6',
        food: '#F97316',
        energy: '#EF4444',
        consumption: '#8B5CF6'
    };

    const categoryLabels = {
        transport: 'Transport',
        food: 'Alimentation',
        energy: 'Énergie',
        consumption: 'Consommation'
    };

    const categories = monthlySummary.by_category;

    const ctx = document.getElementById('monthlyCategoryChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(categories).map(cat => categoryLabels[cat] || cat),
            datasets: [{
                label: 'Émissions mensuelles (kgCO₂e)',
                data: Object.values(categories),
                backgroundColor: Object.keys(categories).map(cat => categoryColors[cat] || '#6B7280'),
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'kgCO₂e'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Gestion des filtres de recommandations
document.addEventListener('DOMContentLoaded', function () {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const recommendationCards = document.querySelectorAll('.recommendation-card');
    const noRecommendationsMessage = document.getElementById('no-recommendations');

    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            const filter = this.getAttribute('data-filter');

            // Update active button
            filterButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-emerald-100', 'text-emerald-700');
                btn.classList.add('bg-gray-100', 'text-gray-600');
            });

            this.classList.add('active', 'bg-emerald-100', 'text-emerald-700');
            this.classList.remove('bg-gray-100', 'text-gray-600');

            // Filter recommendations
            let visibleCount = 0;

            recommendationCards.forEach(card => {
                const impact = card.getAttribute('data-impact');
                const ease = card.getAttribute('data-ease');
                let shouldShow = false;

                switch (filter) {
                    case 'all':
                        shouldShow = true;
                        break;
                    case 'high-impact':
                        shouldShow = impact === 'Élevé';
                        break;
                    case 'easy':
                        shouldShow = ease === 'Facile';
                        break;
                }

                if (shouldShow) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Show/hide no results message
            if (visibleCount === 0) {
                noRecommendationsMessage.classList.remove('hidden');
            } else {
                noRecommendationsMessage.classList.add('hidden');
            }
        });
    });
});