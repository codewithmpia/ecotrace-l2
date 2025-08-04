document.addEventListener("DOMContentLoaded", () => {
    const $ = (s) => document.querySelector(s);
    const $$ = (s) => document.querySelectorAll(s);

    // Variables globales
    const state = {
        activeCategory: null,
        currentMonth: new Date().getMonth(),
        currentYear: new Date().getFullYear(),
        selectedDate: new Date($("#date").value || new Date()),
        today: new Date(),
    };

    const els = {
        dropdowns: $$(".custom-dropdown"),
        categoryOptions: $$(".category-option"),
        activitySelectors: $$(".category-activities"),
        unitDisplay: $("#unit-display"),
        selectedActivityInput: $("#selected_activity_id"),
        dateDropdown: $(".custom-date-dropdown"),
        form: $("#activityForm"),
    };

    // Utilitaires
    const toggle = (el, className = "hidden") =>
        el.classList.toggle(className);
    const add = (el, className) => el.classList.add(className);
    const remove = (el, className) => el.classList.remove(className);
    const hasClass = (el, className) => el.classList.contains(className);

    // Fermeture globale
    const closeAll = () => {
        els.dropdowns.forEach((d) => {
            add(d.querySelector(".options-container"), "hidden");
            const chevron = d.querySelector(".chevron-icon");
            if (chevron) chevron.style.transform = "rotate(0deg)";
        });
        if (els.dateDropdown) {
            add(
                els.dateDropdown.querySelector(".calendar-container"),
                "hidden",
            );
            const chevron = els.dateDropdown.querySelector(
                ".calendar-chevron-icon",
            );
            if (chevron) chevron.style.transform = "rotate(0deg)";
        }
    };

    // Délégation d'événements pour tous les dropdowns
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".custom-dropdown, .custom-date-dropdown"))
            closeAll();

        // Dropdown toggle
        const selectedOption = e.target.closest(".selected-option");
        if (selectedOption) {
            e.stopPropagation();
            const dropdown = selectedOption.closest(".custom-dropdown");
            const container = dropdown.querySelector(".options-container");
            const chevron = dropdown.querySelector(".chevron-icon");
            const isOpen = !hasClass(container, "hidden");

            closeAll();
            if (!isOpen) {
                remove(container, "hidden");
                if (chevron) chevron.style.transform = "rotate(180deg)";
            }
        }

        // Option selection
        const option = e.target.closest(".option");
        if (option) {
            const dropdown = option.closest(".custom-dropdown");
            const selectedOption =
                dropdown.querySelector(".selected-option");
            const selectedText =
                selectedOption.querySelector(".selected-text");
            const { value, unit } = option.dataset;
            const text = option.textContent;

            selectedText.textContent = text;
            selectedText.classList.toggle(
                "text-gray-500",
                text.includes("Sélectionnez"),
            );

            if (state.activeCategory === dropdown.dataset.target) {
                els.selectedActivityInput.value = value;
            }

            els.unitDisplay.textContent = unit ? `(${unit})` : "";
            closeAll();

            dropdown
                .querySelectorAll(".option")
                .forEach((opt) => remove(opt, "bg-emerald-50"));
            add(option, "bg-emerald-50");
        }

        // Category selection
        const categoryOption = e.target.closest(".category-option");
        if (categoryOption) {
            state.activeCategory = categoryOption.dataset.category;

            // Reset all categories
            els.categoryOptions.forEach((opt) => {
                const label = opt.querySelector("label");
                label.className =
                    label.className
                        .replace(/border-emerald-500|bg-emerald-50/g, "")
                        .trim() + " border-gray-200";
            });

            // Activate selected
            const label = categoryOption.querySelector("label");
            label.className =
                label.className.replace("border-gray-200", "") +
                " border-emerald-500 bg-emerald-50";
            categoryOption.querySelector('input[type="radio"]').checked =
                true;

            // Show/hide selectors
            els.activitySelectors.forEach((s) => add(s, "hidden"));
            const selector = $(`#${state.activeCategory}Activities`);
            if (selector) {
                remove(selector, "hidden");
                const dropdown = selector.querySelector(".custom-dropdown");
                const selectedText =
                    dropdown?.querySelector(".selected-text");
                if (selectedText) {
                    const types = {
                        transport: "transport",
                        food: "d'aliment",
                        energy: "d'énergie",
                        consumption: "consommation",
                    };
                    selectedText.textContent = `Sélectionnez un type de ${types[state.activeCategory]}`;
                    add(selectedText, "text-gray-500");
                }
            }

            els.selectedActivityInput.value = "";
            els.unitDisplay.textContent = "";
        }
    });

    // Calendrier optimisé
    if (els.dateDropdown) {
        const cal = {
            selectedDate: els.dateDropdown.querySelector(".selected-date"),
            selectedDateText: els.dateDropdown.querySelector(
                ".selected-date-text",
            ),
            container: els.dateDropdown.querySelector(
                ".calendar-container",
            ),
            chevron: els.dateDropdown.querySelector(
                ".calendar-chevron-icon",
            ),
            input: $("#date"),
            monthYear: els.dateDropdown.querySelector(".month-year"),
            grid: els.dateDropdown.querySelector(".days-grid"),
        };

        const formatDate = (d) =>
            d.toLocaleDateString("fr-FR", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            });
        const formatInput = (d) => d.toISOString().split("T")[0];

        const generateCalendar = () => {
            cal.grid.innerHTML = "";
            const monthNames = [
                "Janvier",
                "Février",
                "Mars",
                "Avril",
                "Mai",
                "Juin",
                "Juillet",
                "Août",
                "Septembre",
                "Octobre",
                "Novembre",
                "Décembre",
            ];
            cal.monthYear.textContent = `${monthNames[state.currentMonth]} ${state.currentYear}`;

            const firstDay = new Date(
                state.currentYear,
                state.currentMonth,
                1,
            ).getDay();
            const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;
            const daysInMonth = new Date(
                state.currentYear,
                state.currentMonth + 1,
                0,
            ).getDate();

            // Empty cells + days
            for (let i = 0; i < adjustedFirstDay + daysInMonth; i++) {
                const cell = document.createElement("div");
                if (i < adjustedFirstDay) {
                    cell.className = "text-center py-2";
                } else {
                    const day = i - adjustedFirstDay + 1;
                    const currentDate = new Date(
                        state.currentYear,
                        state.currentMonth,
                        day,
                    );
                    const isFuture = currentDate > state.today;
                    const isSelected =
                        currentDate.toDateString() ===
                        state.selectedDate.toDateString();
                    const isToday =
                        currentDate.toDateString() ===
                        state.today.toDateString();

                    cell.className = `text-center py-2 cursor-pointer rounded-lg text-sm font-medium transition-all duration-200 ${isSelected
                            ? "bg-emerald-600 text-white shadow-lg"
                            : isToday
                                ? "bg-emerald-100 text-emerald-800 ring-2 ring-emerald-200"
                                : isFuture
                                    ? "text-gray-300 cursor-not-allowed"
                                    : "hover:bg-emerald-50 hover:text-emerald-700"
                        }`;
                    cell.textContent = day;

                    if (!isFuture) {
                        cell.onclick = () => {
                            state.selectedDate = currentDate;
                            cal.selectedDateText.textContent =
                                formatDate(currentDate);
                            remove(cal.selectedDateText, "text-gray-500");
                            add(cal.selectedDate, "border-emerald-500");
                            cal.input.value = formatInput(currentDate);
                            generateCalendar();
                            closeAll();
                        };
                    }
                }
                cal.grid.appendChild(cell);
            }
        };

        // Calendar events
        cal.selectedDate.onclick = (e) => {
            e.stopPropagation();
            const isOpen = !hasClass(cal.container, "hidden");
            closeAll();
            if (!isOpen) {
                remove(cal.container, "hidden");
                cal.chevron.style.transform = "rotate(180deg)";
                state.currentMonth = state.selectedDate.getMonth();
                state.currentYear = state.selectedDate.getFullYear();
                generateCalendar();

                // Ajuster la position si le calendrier sort du viewport
                setTimeout(() => {
                    const rect = cal.container.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;

                    if (rect.bottom > viewportHeight - 20) {
                        // Positionner le calendrier au-dessus du champ
                        cal.container.style.bottom = "100%";
                        cal.container.style.top = "auto";
                        cal.container.style.marginBottom = "8px";
                        cal.container.style.marginTop = "0";
                    } else {
                        // Position par défaut (en dessous)
                        cal.container.style.top = "100%";
                        cal.container.style.bottom = "auto";
                        cal.container.style.marginTop = "8px";
                        cal.container.style.marginBottom = "0";
                    }
                }, 10);
            }
        };

        // Navigation
        els.dateDropdown.querySelector(".prev-month").onclick = () => {
            state.currentMonth--;
            if (state.currentMonth < 0) {
                state.currentMonth = 11;
                state.currentYear--;
            }
            generateCalendar();
        };

        els.dateDropdown.querySelector(".next-month").onclick = () => {
            state.currentMonth++;
            if (state.currentMonth > 11) {
                state.currentMonth = 0;
                state.currentYear++;
            }
            generateCalendar();
        };

        els.dateDropdown.querySelector(".today-btn").onclick = () => {
            state.selectedDate = new Date();
            state.currentMonth = state.today.getMonth();
            state.currentYear = state.today.getFullYear();
            cal.selectedDateText.textContent = formatDate(
                state.selectedDate,
            );
            remove(cal.selectedDateText, "text-gray-500");
            add(cal.selectedDate, "border-emerald-500");
            cal.input.value = formatInput(state.selectedDate);
            generateCalendar();
        };

        els.dateDropdown.querySelector(".close-calendar-btn").onclick =
            closeAll;

        generateCalendar();
    }

    // Validation optimisée
    els.form.onsubmit = (e) => {
        const errors = [
            {
                test: !$('input[name="category"]:checked'),
                msg: "Veuillez sélectionner une catégorie.",
            },
            {
                test: !els.selectedActivityInput.value,
                msg: "Veuillez sélectionner une activité spécifique.",
            },
            {
                test:
                    !$("#quantity").value ||
                    parseFloat($("#quantity").value) <= 0,
                msg: "Veuillez saisir une quantité valide (supérieure à zéro).",
            },
            {
                test: !$("#date").value,
                msg: "Veuillez sélectionner une date.",
            },
        ]
            .filter((v) => v.test)
            .map((v) => v.msg);

        if (errors.length) {
            e.preventDefault();
            $$(".error-message").forEach((el) => el.remove());

            errors.forEach((msg) => {
                const div = document.createElement("div");
                div.className =
                    "error-message w-full relative flex items-center justify-between p-4 mb-4 rounded-xl border border-solid border-red-300 text-red-800 bg-red-50 shadow-sm";
                div.innerHTML = `
                            <div class="flex items-center gap-3">
                                <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.992-.833-2.732 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"/>
                                </svg>
                                <span class="font-medium">${msg}</span>
                            </div>
                        `;
                els.form.parentNode.insertBefore(div, els.form);
                setTimeout(() => div.remove(), 5000);
            });
        }
    };
});