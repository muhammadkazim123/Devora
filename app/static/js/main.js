
/* =========================================================
   DEVORA — MAIN JAVASCRIPT
   Frontend interactions and user experience
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       01. FLASH MESSAGE HANDLING
       ===================================================== */

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach((message) => {

        const closeButton = message.querySelector(".flash-close");

        const dismissMessage = () => {

            if (!message.isConnected) {
                return;
            }

            message.classList.add("flash-hidden");

            window.setTimeout(() => {
                message.remove();
            }, 300);

        };

        if (closeButton) {
            closeButton.addEventListener("click", dismissMessage);
        }

        window.setTimeout(() => {
            dismissMessage();
        }, 6000);

    });


    /* =====================================================
       02. PASSWORD VISIBILITY TOGGLES
       ===================================================== */

    const passwordToggles = document.querySelectorAll(
        "[data-password-toggle]"
    );

    passwordToggles.forEach((toggle) => {

        const inputId = toggle.dataset.passwordToggle;
        const passwordInput = document.getElementById(inputId);

        if (!passwordInput) {
            return;
        }

        toggle.addEventListener("click", () => {

            const isPassword = passwordInput.type === "password";

            passwordInput.type = isPassword ? "text" : "password";

            toggle.textContent = isPassword ? "Hide" : "Show";

            toggle.setAttribute(
                "aria-label",
                isPassword ? "Hide password" : "Show password"
            );

        });

    });


    /* =====================================================
       03. FORM SUBMISSION PROTECTION
       ===================================================== */

    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {

        form.addEventListener("submit", (event) => {

            if (form.dataset.submitting === "true") {

                event.preventDefault();
                return;

            }

            form.dataset.submitting = "true";

            const submitButton = event.submitter ||
                form.querySelector(
                    'button[type="submit"], input[type="submit"]'
                );

            if (submitButton) {

                submitButton.disabled = true;

                if (submitButton.tagName === "BUTTON") {

                    if (!submitButton.dataset.originalText) {
                        submitButton.dataset.originalText =
                            submitButton.textContent.trim();
                    }

                    submitButton.classList.add("is-loading");

                    submitButton.setAttribute("aria-busy", "true");

                }

            }

        });

    });


    /* =====================================================
       04. IMAGE URL PREVIEW
       ===================================================== */

    const imageUrlInputs = document.querySelectorAll("[data-image-url]");

    imageUrlInputs.forEach((input) => {

        const container = input
            .closest(".form-group")
            ?.querySelector("[data-image-preview-container]");

        if (!container) {
            return;
        }

        const preview = container.querySelector("[data-image-preview]");

        const placeholder = container.querySelector(
            ".profile-image-preview-placeholder"
        );

        if (!preview) {
            return;
        }

        const updatePreview = () => {

            const imageUrl = input.value.trim();

            if (!imageUrl) {

                preview.hidden = true;
                preview.removeAttribute("src");

                if (placeholder) {
                    placeholder.hidden = false;
                }

                return;

            }

            try {

                const parsedUrl = new URL(imageUrl);

                if (
                    parsedUrl.protocol !== "https:" &&
                    parsedUrl.protocol !== "http:"
                ) {
                    throw new Error("Unsupported image URL");
                }

                preview.onload = () => {

                    preview.hidden = false;

                    if (placeholder) {
                        placeholder.hidden = true;
                    }

                };

                preview.onerror = () => {

                    preview.hidden = true;

                    if (placeholder) {
                        placeholder.hidden = false;
                        placeholder.textContent =
                            "Unable to load this image. Check the URL.";
                    }

                };

                preview.src = parsedUrl.href;

            } catch (error) {

                preview.hidden = true;

                if (placeholder) {
                    placeholder.hidden = false;
                    placeholder.textContent =
                        "Enter a valid image URL to preview it.";
                }

            }

        };

        input.addEventListener("input", updatePreview);

        if (input.value.trim()) {
            updatePreview();
        }

    });


    /* =====================================================
       05. IMAGE LOADING ERROR HANDLING
       ===================================================== */

    const images = document.querySelectorAll("img");

    images.forEach((image) => {

        image.addEventListener("error", () => {

            image.classList.add("image-load-error");

            image.setAttribute("data-image-error", "true");

        });

        image.addEventListener("load", () => {

            image.classList.remove("image-load-error");

            image.removeAttribute("data-image-error");

        });

    });


    /* =====================================================
       06. CHARACTER COUNTERS
       ===================================================== */

    const characterInputs = document.querySelectorAll(
        "[data-character-count]"
    );

    characterInputs.forEach((input) => {

        const formGroup = input.closest(".form-group");

        if (!formGroup) {
            return;
        }

        let counter = formGroup.querySelector(
            ".live-character-counter"
        );

        if (!counter) {

            counter = document.createElement("span");

            counter.className = "live-character-counter";

            counter.style.color = "var(--muted-dark)";
            counter.style.fontSize = "10px";
            counter.style.fontFamily = "var(--font-mono)";
            counter.style.textAlign = "right";

            input.insertAdjacentElement("afterend", counter);

        }

        const updateCounter = () => {

            const currentLength = input.value.length;

            const maximumLength = input.maxLength > 0
                ? input.maxLength
                : null;

            counter.textContent = maximumLength
                ? `${currentLength} / ${maximumLength}`
                : `${currentLength} characters`;

            if (
                maximumLength &&
                currentLength >= maximumLength
            ) {

                counter.style.color = "var(--warning)";

            } else {

                counter.style.color = "var(--muted-dark)";

            }

        };

        input.addEventListener("input", updateCounter);

        updateCounter();

    });


    /* =====================================================
       07. DELETE CONFIRMATION
       ===================================================== */

    const confirmationForms = document.querySelectorAll(
        "form[data-confirm]"
    );

    confirmationForms.forEach((form) => {

        form.addEventListener("submit", (event) => {

            const message = form.dataset.confirm ||
                "Are you sure you want to continue?";

            const confirmed = window.confirm(message);

            if (!confirmed) {

                event.preventDefault();

                form.dataset.submitting = "false";

                const submitButtons = form.querySelectorAll(
                    'button[type="submit"], input[type="submit"]'
                );

                submitButtons.forEach((button) => {
                    button.disabled = false;
                });

            }

        });

    });


    /* =====================================================
       08. COMMENT INPUT EXPERIENCE
       ===================================================== */

    const commentInputs = document.querySelectorAll(
        ".comment-input"
    );

    commentInputs.forEach((input) => {

        input.addEventListener("keydown", (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey &&
                input.tagName.toLowerCase() === "textarea"
            ) {

                event.preventDefault();

                const form = input.closest("form");

                if (!form) {
                    return;
                }

                if (typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                } else {
                    form.submit();
                }

            }

        });

    });


    /* =====================================================
       09. CHARACTER INPUT FOCUS EFFECTS
       ===================================================== */

    const textInputs = document.querySelectorAll(
        ".form-input, .post-textarea, .comment-input"
    );

    textInputs.forEach((input) => {

        input.addEventListener("focus", () => {
            input.classList.add("is-focused");
        });

        input.addEventListener("blur", () => {
            input.classList.remove("is-focused");
        });

    });


    /* =====================================================
       10. POST IMAGE FALLBACK
       ===================================================== */

    const postImages = document.querySelectorAll(".post-image");

    postImages.forEach((image) => {

        image.addEventListener("error", () => {

            const container = image.closest(".post-image-container");

            if (!container) {
                return;
            }

            image.hidden = true;

            let errorMessage = container.querySelector(
                ".post-image-error"
            );

            if (!errorMessage) {

                errorMessage = document.createElement("div");

                errorMessage.className = "post-image-error";

                errorMessage.textContent =
                    "This image could not be displayed.";

                errorMessage.style.padding = "22px";
                errorMessage.style.textAlign = "center";
                errorMessage.style.color = "var(--muted)";
                errorMessage.style.fontSize = "11px";

                container.appendChild(errorMessage);

            }

        });

    });


    /* =====================================================
       11. FOOTER YEAR
       ===================================================== */

    const currentYearElements = document.querySelectorAll(
        "[data-current-year]"
    );

    const currentYear = new Date().getFullYear();

    currentYearElements.forEach((element) => {
        element.textContent = currentYear;
    });


    /* =====================================================
       12. ACCESSIBILITY IMPROVEMENTS
       ===================================================== */

    const externalLinks = document.querySelectorAll(
        'a[target="_blank"]'
    );

    externalLinks.forEach((link) => {

        const existingRel = link.getAttribute("rel") || "";

        const relValues = new Set(existingRel.split(/\s+/).filter(Boolean));

        relValues.add("noopener");
        relValues.add("noreferrer");

        link.setAttribute("rel", [...relValues].join(" "));

    });


    /* =====================================================
       13. INITIAL PAGE SETUP
       ===================================================== */

    document.documentElement.classList.add("js-enabled");

    console.log("Devora frontend initialized.");

});
