const API_URL = "http://127.0.0.1:8000";

// =====================================================
// AUTH HELPERS
// =====================================================

function getToken() {
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        ""
    );
}

function getUser() {
    const userData = localStorage.getItem("user");

    if (!userData) return null;

    try {
        return JSON.parse(userData);
    } catch (error) {
        console.error("Invalid user data:", error);

        localStorage.removeItem("user");
        localStorage.removeItem("token");
        localStorage.removeItem("access_token");

        return null;
    }
}

// =====================================================
// MODALS
// =====================================================

function openLogin() {
    closeModals();

    const modal = document.getElementById("loginModal");
    const message = document.getElementById("loginMessage");

    if (modal) modal.classList.add("active");

    if (message) {
        message.textContent = "";
        message.style.color = "";
    }
}

function openRegister() {
    closeModals();

    const modal = document.getElementById("registerModal");
    const message = document.getElementById("registerMessage");

    if (modal) modal.classList.add("active");

    if (message) {
        message.textContent = "";
        message.style.color = "";
    }
}

function closeModals() {
    const loginModal = document.getElementById("loginModal");
    const registerModal = document.getElementById("registerModal");

    if (loginModal) loginModal.classList.remove("active");
    if (registerModal) registerModal.classList.remove("active");
}

function switchToRegister() {
    openRegister();
}

function switchToLogin() {
    openLogin();
}

// =====================================================
// CLOSE MODAL
// =====================================================

document.addEventListener("click", function (event) {
    if (
        event.target &&
        event.target.classList &&
        event.target.classList.contains("modal")
    ) {
        closeModals();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeModals();
    }
});

// =====================================================
// REGISTER
// =====================================================

async function register() {
    const nameInput = document.getElementById("registerName");
    const emailInput = document.getElementById("registerEmail");
    const passwordInput = document.getElementById("registerPassword");
    const roleInput = document.getElementById("registerRole");
    const message = document.getElementById("registerMessage");

    if (!nameInput || !emailInput || !passwordInput || !roleInput || !message) {
        return;
    }

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const role = roleInput.value;

    message.textContent = "";
    message.style.color = "";

    if (!name || !email || !password) {
        message.textContent = "Please fill all fields.";
        message.style.color = "#d62828";
        return;
    }

    if (password.length < 6) {
        message.textContent = "Password must be at least 6 characters.";
        message.style.color = "#d62828";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                role: role
            })
        });

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (!response.ok) {
            message.textContent =
                data.detail || "Registration failed.";
            message.style.color = "#d62828";
            return;
        }

        message.textContent = "Account created successfully! ✅";
        message.style.color = "#16803c";

        passwordInput.value = "";

        setTimeout(function () {
            closeModals();

            const loginEmail = document.getElementById("loginEmail");

            if (loginEmail) {
                loginEmail.value = email;
            }

            openLogin();

            const loginMessage =
                document.getElementById("loginMessage");

            if (loginMessage) {
                loginMessage.textContent =
                    "Account created. Please login.";
                loginMessage.style.color = "#16803c";
            }
        }, 1000);

    } catch (error) {
        console.error("Register error:", error);

        message.textContent =
            "Cannot connect to backend. Make sure FastAPI is running.";
        message.style.color = "#d62828";
    }
}

// =====================================================
// LOGIN
// =====================================================

async function login() {
    const emailInput = document.getElementById("loginEmail");
    const passwordInput = document.getElementById("loginPassword");
    const message = document.getElementById("loginMessage");

    if (!emailInput || !passwordInput || !message) {
        return;
    }

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    message.textContent = "";
    message.style.color = "";

    if (!email || !password) {
        message.textContent =
            "Please enter email and password.";
        message.style.color = "#d62828";
        return;
    }

    try {
        message.textContent = "Logging in...";
        message.style.color = "#777";

        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        console.log("LOGIN RESPONSE:", data);

        if (!response.ok) {
            message.textContent =
                data.detail || "Invalid email or password.";
            message.style.color = "#d62828";
            return;
        }

        const accessToken =
            data.access_token || data.token;

        if (!accessToken) {
            console.error("No token received:", data);

            message.textContent =
                "Login failed: no access token received.";
            message.style.color = "#d62828";
            return;
        }

        const user = data.user;

        if (!user) {
            console.error("No user received:", data);

            message.textContent =
                "Login failed: user information not received.";
            message.style.color = "#d62828";
            return;
        }

        // Normalize role
        if (user.role) {
            user.role = String(user.role).toLowerCase().trim();
        }

        // Save authentication
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("token", accessToken);
        localStorage.setItem("user", JSON.stringify(user));

        console.log("TOKEN SAVED:", accessToken);
        console.log("USER SAVED:", user);
        console.log("USER ROLE:", user.role);

        message.textContent = "Login successful! ✅";
        message.style.color = "#16803c";

        updateNavbar(user);

        setTimeout(function () {
            closeModals();

            // Employer
            if (user.role === "employer") {
                window.location.href = "employer.html";
                return;
            }

            // Job seeker
            if (
                user.role === "job_seeker" ||
                user.role === "jobseeker"
            ) {
                window.location.href = "index.html";
                return;
            }

            // Default
            window.location.href = "index.html";

        }, 700);

    } catch (error) {
        console.error("Login error:", error);

        message.textContent =
            "Cannot connect to backend. Make sure FastAPI is running.";
        message.style.color = "#d62828";
    }
}

// =====================================================
// NAVBAR
// =====================================================

function updateNavbar(user) {
    const applicationsButton =
        document.getElementById("applicationsButton");

    const employerButton =
        document.getElementById("employerButton");

    const loginButton =
        document.getElementById("loginButton");

    const registerButton =
        document.getElementById("registerButton");

    const logoutButton =
        document.getElementById("logoutButton");

    const userName =
        document.getElementById("userName");

    // Reset
    if (applicationsButton)
        applicationsButton.style.display = "none";

    if (employerButton)
        employerButton.style.display = "none";

    if (loginButton)
        loginButton.style.display = "inline-block";

    if (registerButton)
        registerButton.style.display = "inline-block";

    if (logoutButton)
        logoutButton.style.display = "none";

    if (userName)
        userName.style.display = "none";

    if (!user) return;

    // Logged in
    if (loginButton)
        loginButton.style.display = "none";

    if (registerButton)
        registerButton.style.display = "none";

    if (logoutButton)
        logoutButton.style.display = "inline-block";

    if (userName) {
        userName.textContent = "Hi, " + (user.name || "User");
        userName.style.display = "inline-block";
    }

    // Job seeker
    if (
        user.role === "job_seeker" ||
        user.role === "jobseeker"
    ) {
        if (applicationsButton)
            applicationsButton.style.display = "inline-block";
    }

    // Employer
    if (user.role === "employer") {
        if (employerButton)
            employerButton.style.display = "inline-block";
    }
}

// =====================================================
// LOAD JOBS
// =====================================================

async function loadJobs() {
    const container =
        document.getElementById("jobsContainer");

    if (!container) return;

    try {
        const response =
            await fetch(`${API_URL}/jobs`);

        let jobs = [];

        try {
            jobs = await response.json();
        } catch {
            jobs = [];
        }

        if (!response.ok) {
            throw new Error(
                jobs.detail || "Unable to load jobs."
            );
        }

        if (!Array.isArray(jobs) || jobs.length === 0) {
            container.innerHTML = `
                <div class="job-card">
                    <h3>No Jobs Available</h3>
                    <p>
                        Check back later for new opportunities.
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = "";

        jobs.forEach(function (job) {
            const card =
                document.createElement("div");

            card.className = "job-card";

            const description =
                job.description || "";

            card.innerHTML = `
                <div class="job-top">

                    <div class="job-icon">
                        💼
                    </div>

                    <div class="job-type">
                        ${escapeHTML(job.job_type || "Job")}
                    </div>

                </div>

                <h3>
                    ${escapeHTML(job.title || "Untitled Job")}
                </h3>

                <div class="company">
                    ${escapeHTML(job.company || "Company")}
                </div>

                <div class="location">
                    📍
                    ${escapeHTML(
                        job.location ||
                        "Location not specified"
                    )}
                </div>

                <div class="description">
                    ${escapeHTML(
                        description.length > 120
                            ? description.substring(0, 120) + "..."
                            : description
                    )}
                </div>

                <div class="job-bottom">

                    <strong>
                        ${escapeHTML(
                            job.salary ||
                            "Salary not specified"
                        )}
                    </strong>

                    <button
                        class="apply-btn"
                        onclick="applyForJob(${Number(job.id)})">

                        Apply Now

                    </button>

                </div>
            `;

            container.appendChild(card);
        });

    } catch (error) {
        console.error("Load jobs error:", error);

        container.innerHTML = `
            <div class="job-card">

                <h3>
                    Unable to Load Jobs
                </h3>

                <p>
                    ${escapeHTML(error.message)}
                </p>

            </div>
        `;
    }
}

// =====================================================
// APPLY
// =====================================================

async function applyForJob(jobId) {
    const token = getToken();
    const user = getUser();

    if (!token || !user) {
        alert("Please login first to apply for a job.");
        openLogin();
        return;
    }

    if (
        user.role !== "job_seeker" &&
        user.role !== "jobseeker"
    ) {
        alert("Only job seekers can apply for jobs.");
        return;
    }

    try {
        const response =
            await fetch(
                `${API_URL}/jobs/${jobId}/apply`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({
                        user_id: user.id
                    })
                }
            );

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (
            response.status === 401 ||
            response.status === 403
        ) {
            alert(
                data.detail ||
                "Your login session has expired."
            );

            logoutUser();
            return;
        }

        if (!response.ok) {
            alert(
                data.detail ||
                "Unable to apply for this job."
            );
            return;
        }

        alert(
            "Application submitted successfully! ✅"
        );

    } catch (error) {
        console.error("Apply error:", error);

        alert(
            "Cannot connect to JobHub backend."
        );
    }
}

// =====================================================
// SEARCH
// =====================================================

async function searchJobs() {
    const searchInput =
        document.getElementById("searchInput");

    const locationInput =
        document.getElementById("locationInput");

    const container =
        document.getElementById("jobsContainer");

    if (!container) return;

    const searchText =
        searchInput
            ? searchInput.value.trim().toLowerCase()
            : "";

    const locationText =
        locationInput
            ? locationInput.value.trim().toLowerCase()
            : "";

    try {
        const response =
            await fetch(`${API_URL}/jobs`);

        let jobs = [];

        try {
            jobs = await response.json();
        } catch {
            jobs = [];
        }

        if (!response.ok) {
            throw new Error(
                jobs.detail || "Unable to search jobs."
            );
        }

        const filtered =
            jobs.filter(function (job) {
                const title =
                    (job.title || "").toLowerCase();

                const company =
                    (job.company || "").toLowerCase();

                const description =
                    (job.description || "").toLowerCase();

                const requirements =
                    (job.requirements || "").toLowerCase();

                const location =
                    (job.location || "").toLowerCase();

                const matchesSearch =
                    !searchText ||
                    title.includes(searchText) ||
                    company.includes(searchText) ||
                    description.includes(searchText) ||
                    requirements.includes(searchText);

                const matchesLocation =
                    !locationText ||
                    location.includes(locationText);

                return (
                    matchesSearch &&
                    matchesLocation
                );
            });

        container.innerHTML = "";

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="job-card">

                    <h3>
                        No Matching Jobs
                    </h3>

                    <p>
                        Try another search.
                    </p>

                </div>
            `;

            return;
        }

        filtered.forEach(function (job) {
            const card =
                document.createElement("div");

            card.className = "job-card";

            const description =
                job.description || "";

            card.innerHTML = `
                <div class="job-top">

                    <div class="job-icon">
                        💼
                    </div>

                    <div class="job-type">
                        ${escapeHTML(
                            job.job_type || "Job"
                        )}
                    </div>

                </div>

                <h3>
                    ${escapeHTML(
                        job.title || "Untitled Job"
                    )}
                </h3>

                <div class="company">
                    ${escapeHTML(
                        job.company || "Company"
                    )}
                </div>

                <div class="location">
                    📍
                    ${escapeHTML(
                        job.location ||
                        "Location not specified"
                    )}
                </div>

                <div class="description">
                    ${escapeHTML(description)}
                </div>

                <div class="job-bottom">

                    <strong>
                        ${escapeHTML(
                            job.salary ||
                            "Salary not specified"
                        )}
                    </strong>

                    <button
                        class="apply-btn"
                        onclick="applyForJob(${Number(job.id)})">

                        Apply Now

                    </button>

                </div>
            `;

            container.appendChild(card);
        });

    } catch (error) {
        console.error("Search error:", error);

        alert("Unable to search jobs.");
    }
}

// =====================================================
// LOGOUT
// =====================================================

function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    updateNavbar(null);

    if (typeof showToast === "function") {
        showToast("Logged out successfully.");
    }

    setTimeout(function () {
        window.location.href = "index.html";
    }, 400);
}

// =====================================================
// HTML ESCAPE
// =====================================================

function escapeHTML(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// =====================================================
// ENTER SEARCH
// =====================================================

document.addEventListener("keydown", function (event) {
    if (
        event.key === "Enter" &&
        (
            document.activeElement?.id === "searchInput" ||
            document.activeElement?.id === "locationInput"
        )
    ) {
        searchJobs();
    }
});

// =====================================================
// INITIALIZE
// =====================================================

document.addEventListener("DOMContentLoaded", function () {
    loadJobs();

    const user = getUser();

    updateNavbar(user);
});