
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // SIGNUP PASSWORD VALIDATION
    // =====================================

    const signupForm = document.querySelector(".auth-form");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm_password");

    if (signupForm && password && confirmPassword) {

        signupForm.addEventListener("submit", function (event) {

            if (password.value !== confirmPassword.value) {
                event.preventDefault();

                alert("Passwords do not match. Please try again.");

                confirmPassword.focus();
                return;
            }

            if (password.value.length < 8) {
                event.preventDefault();

                alert("Password must contain at least 8 characters.");

                password.focus();
            }
        });

    }

    // =====================================
    // FORM INPUT FOCUS EFFECT
    // =====================================

    const formInputs = document.querySelectorAll(
        ".form-field input, .form-field select, .form-field textarea"
    );

    formInputs.forEach(function (input) {

        input.addEventListener("focus", function () {
            input.parentElement.classList.add("field-focused");
        });

        input.addEventListener("blur", function () {
            input.parentElement.classList.remove("field-focused");
        });

    });

});
