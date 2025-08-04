document.addEventListener('DOMContentLoaded', function () {
    // Utilitaires pour sélection DOM
    const $ = (selector) => document.querySelector(selector);
    const $$ = (selector) => document.querySelectorAll(selector);

    const hasActivities = activitiesData && activitiesData.length > 0;

    // Initialisation si des activités existent
    if (hasActivities) {
        calculateHistoryStats();
        createHistoryChart();
        createCategoryChart();
    }

    /**
     * Calcul et affichage des statistiques de l'historique
     */
    function calculateHistoryStats() {
        // Calcul du total des émissions
        const totalEmissions = activitiesData.reduce((sum, activity) => sum + parseFloat(activity.emissions), 0);
        const totalElement = $('#totalHistoryEmissions');
        if (totalElement) {
            totalElement.textContent = totalEmissions.toFixed(2);
        }

        // Calcul des dates de première et dernière activité
        const sortedDates = activitiesData
            .map(activity => new Date(activity.date))
            .sort((a, b) => a - b);

        if (sortedDates.length > 0) {
            const firstDate = sortedDates[0];
            const lastDate = sortedDates[sortedDates.length - 1];

            const firstElement = $('#firstActivityDate');
            const lastElement = $('#lastActivityDate');

            if (firstElement) {
                firstElement.textContent = firstDate.toLocaleDateString('fr-FR', {
                    day: 'numeric',
                    month: 'short'
                });
            }

            if (lastElement) {
                lastElement.textContent = lastDate.toLocaleDateString('fr-FR', {
                    day: 'numeric',
                    month: 'short'
                });
            }
        }
    }

    /**
     * Création du graphique d'évolution des émissions
     */
    function createHistoryChart() {
        const ctx = $('#historyTrendChart');
        if (!ctx) return;

        // Regroupement des données par jour
        const dailyEmissions = {};
        activitiesData.forEach(activity => {
            const date = new Date(activity.date);
            const dateKey = date.toISOString().split('T')[0]; // Format YYYY-MM-DD

            if (!dailyEmissions[dateKey]) {
                dailyEmissions[dateKey] = 0;
            }
            dailyEmissions[dateKey] += parseFloat(activity.emissions);
        });

        // Préparation des données pour Chart.js
        const sortedDates = Object.keys(dailyEmissions).sort();
        const labels = sortedDates.map(dateStr => {
            const date = new Date(dateStr);
            return date.toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'short'
            });
        });
        const data = sortedDates.map(dateStr => dailyEmissions[dateStr]);

        new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Émissions journalières (kgCO₂e)',
                    data: data,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#10B981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
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
                        borderWidth: 1,
                        callbacks: {
                            label: function (context) {
                                return `${context.parsed.y.toFixed(2)} kgCO₂e`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'kgCO₂e',
                            font: { size: 12, weight: 'bold' }
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date',
                            font: { size: 12, weight: 'bold' }
                        },
                        grid: { display: false }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    /**
     * Création du graphique de répartition par catégorie
     */
    function createCategoryChart() {
        const ctx = $('#categoryDistributionChart');
        if (!ctx) return;

        // Configuration des couleurs par catégorie
        const categoryConfig = {
            'transport': { label: 'Transport', color: '#3B82F6' },
            'food': { label: 'Alimentation', color: '#F97316' },
            'energy': { label: 'Énergie', color: '#EF4444' },
            'consumption': { label: 'Consommation', color: '#A855F7' }
        };

        // Regroupement des émissions par catégorie
        const categoryEmissions = {};
        activitiesData.forEach(activity => {
            const category = activity.category;
            if (!categoryEmissions[category]) {
                categoryEmissions[category] = 0;
            }
            categoryEmissions[category] += parseFloat(activity.emissions);
        });

        // Préparation des données pour Chart.js
        const categories = Object.keys(categoryEmissions);
        const labels = categories.map(cat => categoryConfig[cat]?.label || cat);
        const data = categories.map(cat => categoryEmissions[cat]);
        const colors = categories.map(cat => categoryConfig[cat]?.color || '#6B7280');

        new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#ffffff',
                    borderWidth: 3,
                    hoverBorderWidth: 4
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
                            usePointStyle: true,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#10B981',
                        borderWidth: 1,
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed.toFixed(2)} kgCO₂e (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    /**
     * Initialisation du système de tri
     */
    function initializeSorting() {
        const sortButtons = $('.sort-btn');

        sortButtons.forEach(button => {
            button.addEventListener('click', function () {
                const sortType = this.dataset.sort;

                // Mise à jour de l'état visuel des boutons
                sortButtons.forEach(btn => {
                    btn.classList.remove('active', 'bg-emerald-100', 'text-emerald-700');
                    btn.classList.add('bg-emerald-50', 'text-emerald-600');
                });

                this.classList.add('active', 'bg-emerald-100', 'text-emerald-700');
                this.classList.remove('bg-emerald-50', 'text-emerald-600');

                // Application du tri
                sortActivities(sortType);
            });
        });
    }

    /**
     * Tri des activités selon le critère choisi
     */
    function sortActivities(sortType) {
        const tableBody = $('#activitiesTableBody');
        const cardsContainer = $('#activitiesCards');

        // Tri du tableau (desktop)
        if (tableBody) {
            const rows = Array.from(tableBody.querySelectorAll('.activity-row'));
            rows.sort((a, b) => compareElements(a, b, sortType));
            rows.forEach(row => tableBody.appendChild(row));
        }

        // Tri des cartes (mobile)
        if (cardsContainer) {
            const cards = Array.from(cardsContainer.querySelectorAll('.activity-card'));
            cards.sort((a, b) => compareElements(a, b, sortType));
            cards.forEach(card => cardsContainer.appendChild(card));
        }
    }

    /**
     * Fonction de comparaison pour le tri
     */
    function compareElements(a, b, sortType) {
        switch (sortType) {
            case 'date-desc':
                return new Date(b.dataset.date) - new Date(a.dataset.date);
            case 'emissions-desc':
                return parseFloat(b.dataset.emissions) - parseFloat(a.dataset.emissions);
            case 'category':
                return a.dataset.category.localeCompare(b.dataset.category, 'fr');
            default:
                return 0;
        }
    }
});