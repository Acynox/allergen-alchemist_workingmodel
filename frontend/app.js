const API_URL = "http://localhost:8000";

// DOM Elements - Recipe Analysis
const recipeInput = document.getElementById("recipe-input");
const allergenCheckboxes = document.getElementById("allergen-checkboxes");
const analyzeRecipeBtn = document.getElementById("analyze-recipe-btn");
const recipeResultsSection = document.getElementById("recipe-results-section");
const recipeTitleDisplay = document.getElementById("recipe-title-display");
const recipeIssuesList = document.getElementById("recipe-issues-list");
const loadingIndicator = document.getElementById("loading-indicator");
const errorMessage = document.getElementById("error-message");
const errorText = document.getElementById("error-text");

// DOM Elements - Diet Plan
const dietAllergenCheckboxes = document.getElementById("diet-allergen-checkboxes");
const dietPreference = document.getElementById("diet-preference");
const generateDietBtn = document.getElementById("generate-diet-btn");
const dietLoading = document.getElementById("diet-loading");
const dietError = document.getElementById("diet-error");
const dietErrorText = document.getElementById("diet-error-text");
const dietResults = document.getElementById("diet-results");
const dietPlanGrid = document.getElementById("diet-plan-grid");

// DOM Elements - Nutrition
const nutritionRecipeInput = document.getElementById("nutrition-recipe-input");
const analyzeNutritionBtn = document.getElementById("analyze-nutrition-btn");
const nutritionLoading = document.getElementById("nutrition-loading");
const nutritionError = document.getElementById("nutrition-error");
const nutritionErrorText = document.getElementById("nutrition-error-text");
const nutritionResults = document.getElementById("nutrition-results");
const nutritionRecipeTitle = document.getElementById("nutrition-recipe-title");
const nutritionCards = document.getElementById("nutrition-cards");

// Modal Elements
const moleculeModal = document.getElementById("molecule-modal");
const closeModal = document.querySelector(".close-modal");
const moleculeList = document.getElementById("molecule-list");

// Tab Navigation
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        // Remove active from all
        tabBtns.forEach(b => b.classList.remove("active"));
        tabContents.forEach(c => {
            c.classList.remove("active");
            c.classList.add("hidden");
        });

        // Add active to clicked
        btn.classList.add("active");
        const tabId = btn.getAttribute("data-tab");
        const content = document.getElementById(`tab-${tabId}`);
        content.classList.remove("hidden");
        content.classList.add("active");
    });
});

// Init
async function init() {
    try {
        await fetchAllergens();
    } catch (err) {
        console.error("Failed to load allergen data:", err);
    }
}

async function fetchAllergens() {
    const res = await fetch(`${API_URL}/allergens`);
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();

    // Populate both allergen checkbox groups
    [allergenCheckboxes, dietAllergenCheckboxes].forEach(container => {
        container.innerHTML = "";
        data.forEach(allergen => {
            const label = document.createElement("label");
            label.className = "checkbox-label";
            const niceName = formatAllergen(allergen);
            label.innerHTML = `
                <input type="checkbox" value="${allergen}">
                <span>${niceName}</span>
            `;
            container.appendChild(label);
        });
    });
}

function formatAllergen(str) {
    return str.replace(/_/g, " ");
}

// --- Recipe Analysis ---
analyzeRecipeBtn.addEventListener("click", async () => {
    const recipeName = recipeInput.value.trim();
    const checkedBoxes = document.querySelectorAll("#allergen-checkboxes input:checked");
    const selectedAllergens = Array.from(checkedBoxes).map(cb => cb.value);

    recipeResultsSection.classList.add("hidden");
    errorMessage.classList.add("hidden");
    recipeIssuesList.innerHTML = "";

    if (!recipeName) {
        showError("Please enter a recipe name.");
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_URL}/analyze_recipe`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                recipe_name: recipeName,
                user_allergens: selectedAllergens
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `Server returned ${response.status}`);
        }

        const data = await response.json();
        recipeTitleDisplay.textContent = `Results for: ${data.recipe_title}`;
        recipeResultsSection.classList.remove("hidden");

        if (!data.found_issues) {
            recipeIssuesList.innerHTML = `<div class="safe-message"><i class="fa-solid fa-check-circle"></i> No allergen issues found in this recipe based on your profile!</div>`;
        } else {
            data.substitutions.forEach(issue => {
                const issueDiv = document.createElement("div");
                issueDiv.className = "recipe-issue-card";

                const subs = issue.substitutes.slice(0, 5);

                let subsHTML = "";
                if (subs.length > 0) {
                    subsHTML = subs.map(sub => {
                        return `
                            <div class="mini-sub-card">
                                ${sub.verified ? '<i class="fa-solid fa-check verified-icon" title="Culinary Verified"></i>' : ''}
                                <span class="sub-name">${sub.name}</span>
                                <span class="sub-score">${(sub.score * 100).toFixed(0)}% Match</span>
                                <button class="view-synergy-btn secondary-btn" data-molecules="${sub.common_molecules.join(', ')}">
                                    <i class="fa-solid fa-atom"></i> View Chemistry
                                </button>
                            </div>
                        `;
                    }).join("");
                } else {
                    subsHTML = "<p>No suitable substitutes found in our database.</p>";
                }

                issueDiv.innerHTML = `
                    <div class="issue-header">
                        <h3><i class="fa-solid fa-triangle-exclamation"></i> Contains Allergen: <span>${issue.original_ingredient}</span></h3>
                    </div>
                    <div class="issue-subs">
                        <p>Suggested Substitutes:</p>
                        <div class="mini-grid">
                            ${subsHTML}
                        </div>
                    </div>
                `;
                recipeIssuesList.appendChild(issueDiv);
            });
        }

    } catch (err) {
        showError(err.message);
    } finally {
        hideLoading();
    }
});

// --- Diet Plan Generation ---
generateDietBtn.addEventListener("click", async () => {
    const checkedBoxes = document.querySelectorAll("#diet-allergen-checkboxes input:checked");
    const selectedAllergens = Array.from(checkedBoxes).map(cb => cb.value);
    const preference = dietPreference.value;

    dietResults.classList.add("hidden");
    dietError.classList.add("hidden");
    dietPlanGrid.innerHTML = "";
    dietLoading.classList.remove("hidden");

    try {
        const response = await fetch(`${API_URL}/generate_diet_plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_allergens: selectedAllergens,
                diet_preference: preference
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `Server returned ${response.status}`);
        }

        const data = await response.json();
        displayDietPlan(data.weekly_plan);
        dietResults.classList.remove("hidden");

    } catch (err) {
        dietError.classList.remove("hidden");
        dietErrorText.textContent = err.message;
    } finally {
        dietLoading.classList.add("hidden");
    }
});

function displayDietPlan(weeklyPlan) {
    dietPlanGrid.innerHTML = "";
    weeklyPlan.forEach(day => {
        const dayCard = document.createElement("div");
        dayCard.className = "day-card";
        dayCard.innerHTML = `
            <h3><i class="fa-solid fa-calendar-day"></i> ${day.day}</h3>
            <div class="meal-section">
                <h4><i class="fa-solid fa-mug-hot"></i> Breakfast</h4>
                <p>${day.breakfast}</p>
            </div>
            <div class="meal-section">
                <h4><i class="fa-solid fa-bowl-food"></i> Lunch</h4>
                <p>${day.lunch}</p>
            </div>
            <div class="meal-section">
                <h4><i class="fa-solid fa-pizza-slice"></i> Dinner</h4>
                <p>${day.dinner}</p>
            </div>
        `;
        dietPlanGrid.appendChild(dayCard);
    });
}

// --- Nutrition Analysis ---
analyzeNutritionBtn.addEventListener("click", async () => {
    const recipeName = nutritionRecipeInput.value.trim();

    nutritionResults.classList.add("hidden");
    nutritionError.classList.add("hidden");
    nutritionCards.innerHTML = "";

    if (!recipeName) {
        nutritionError.classList.remove("hidden");
        nutritionErrorText.textContent = "Please enter a recipe name.";
        return;
    }

    nutritionLoading.classList.remove("hidden");

    try {
        const response = await fetch(`${API_URL}/get_nutrition`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                recipe_name: recipeName
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `Server returned ${response.status}`);
        }

        const data = await response.json();
        displayNutrition(data);
        nutritionResults.classList.remove("hidden");

    } catch (err) {
        nutritionError.classList.remove("hidden");
        nutritionErrorText.textContent = err.message;
    } finally {
        nutritionLoading.classList.add("hidden");
    }
});

function displayNutrition(data) {
    nutritionRecipeTitle.textContent = `Nutritional Information: ${data.recipe_title}`;
    nutritionCards.innerHTML = "";

    const nutrients = [
        { label: "Calories", value: data.calories, unit: "kcal", icon: "fa-fire" },
        { label: "Protein", value: data.protein, unit: "g", icon: "fa-drumstick-bite" },
        { label: "Carbs", value: data.carbs, unit: "g", icon: "fa-bread-slice" },
        { label: "Fat", value: data.fat, unit: "g", icon: "fa-droplet" },
        { label: "Fiber", value: data.fiber, unit: "g", icon: "fa-wheat-awn" },
        { label: "Sugar", value: data.sugar, unit: "g", icon: "fa-candy-cane" }
    ];

    nutrients.forEach(nutrient => {
        const card = document.createElement("div");
        card.className = "nutrition-card";
        card.innerHTML = `
            <div class="icon"><i class="fa-solid ${nutrient.icon}"></i></div>
            <div class="value">${nutrient.value}${nutrient.unit}</div>
            <div class="label">${nutrient.label}</div>
        `;
        nutritionCards.appendChild(card);
    });
}

// Utility Functions
function showLoading() {
    if (loadingIndicator) loadingIndicator.classList.remove("hidden");
}

function hideLoading() {
    if (loadingIndicator) loadingIndicator.classList.add("hidden");
}

function showError(msg) {
    errorMessage.classList.remove("hidden");
    errorText.textContent = msg;
}

// Modal Logic - Event Delegation for dynamically created buttons
document.addEventListener('click', (e) => {
    if (e.target.closest('.view-synergy-btn')) {
        const btn = e.target.closest('.view-synergy-btn');
        const moleculesStr = btn.getAttribute('data-molecules');
        const molecules = moleculesStr ? moleculesStr.split(', ').filter(m => m.trim()) : [];

        moleculeList.innerHTML = "";
        if (!molecules || molecules.length === 0) {
            moleculeList.innerHTML = "<p>No shared flavor molecules identified.</p>";
        } else {
            molecules.forEach(mol => {
                const tag = document.createElement("span");
                tag.className = "molecule-tag";
                tag.textContent = mol;
                moleculeList.appendChild(tag);
            });
        }
        moleculeModal.classList.add("active");
    }
});

closeModal.addEventListener("click", () => {
    moleculeModal.classList.remove("active");
});

window.onclick = function (event) {
    if (event.target == moleculeModal) {
        moleculeModal.classList.remove("active");
    }
}

// Start
init();
