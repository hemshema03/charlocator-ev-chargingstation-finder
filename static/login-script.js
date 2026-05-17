const loginForm = document.querySelector("#login");
const createAccountForm = document.querySelector("#createAccount");
const loginLink = document.querySelector("#loginLink");
const createAccountLink = document.querySelector("#createAccountLink");

function showForm(formToShow, formToHide) {
    formToHide.classList.add("form--hidden");
    formToShow.classList.remove("form--hidden");

    formToShow.animate(
        [
            { opacity: 0, transform: "translateY(18px) scale(0.98)" },
            { opacity: 1, transform: "translateY(0) scale(1)" }
        ],
        {
            duration: 350,
            easing: "ease-out"
        }
    );

    clearAllErrors();
}

function clearAllErrors() {
    document.querySelectorAll(".form__message--error").forEach((box) => {
        box.textContent = "";
    });

    document.querySelectorAll(".form__input-error-message").forEach((box) => {
        box.textContent = "";
    });

    document.querySelectorAll(".form__input").forEach((input) => {
        input.classList.remove("form__input--error");
    });
}

function setError(input, message) {
    const group = input.closest(".form__input-group");
    const errorBox = group.querySelector(".form__input-error-message");

    input.classList.add("form__input--error");

    if (errorBox) {
        errorBox.textContent = message;
    }
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

if (loginLink) {
    loginLink.addEventListener("click", (event) => {
        event.preventDefault();
        showForm(loginForm, createAccountForm);
    });
}

if (createAccountLink) {
    createAccountLink.addEventListener("click", (event) => {
        event.preventDefault();
        showForm(createAccountForm, loginForm);
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
        clearAllErrors();

        const username = loginForm.querySelector("#username");
        const password = loginForm.querySelector("#password");
        const errorContainer = loginForm.querySelector(".form__message--error");

        let hasError = false;

        if (!username.value.trim()) {
            setError(username, "Username or email is required");
            hasError = true;
        }

        if (!password.value.trim()) {
            setError(password, "Password is required");
            hasError = true;
        }

        if (hasError) {
            event.preventDefault();
            errorContainer.textContent = "Please correct the highlighted fields.";
        }
    });
}

if (createAccountForm) {
    createAccountForm.addEventListener("submit", (event) => {
        clearAllErrors();

        const username = createAccountForm.querySelector("#signupUsername");
        const email = createAccountForm.querySelector('input[name="email"]');
        const password = createAccountForm.querySelector('input[name="password"]');
        const confirmPassword = createAccountForm.querySelector('input[name="confirmPassword"]');
        const errorContainer = createAccountForm.querySelector(".form__message--error");

        let hasError = false;

        if (!username.value.trim()) {
            setError(username, "Username is required");
            hasError = true;
        } else if (username.value.trim().length < 3) {
            setError(username, "Username must be at least 3 characters");
            hasError = true;
        }

        if (!email.value.trim()) {
            setError(email, "Email address is required");
            hasError = true;
        } else if (!isValidEmail(email.value.trim())) {
            setError(email, "Enter a valid email address");
            hasError = true;
        }

        if (!password.value.trim()) {
            setError(password, "Password is required");
            hasError = true;
        } else if (password.value.length < 6) {
            setError(password, "Password must be at least 6 characters");
            hasError = true;
        }

        if (!confirmPassword.value.trim()) {
            setError(confirmPassword, "Confirm your password");
            hasError = true;
        } else if (password.value !== confirmPassword.value) {
            setError(confirmPassword, "Passwords do not match");
            hasError = true;
        }

        if (hasError) {
            event.preventDefault();
            errorContainer.textContent = "Please correct the highlighted fields.";
        }
    });
}