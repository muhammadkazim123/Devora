
/* ==========================================
   DEVORA — INTERACTIONS
   Reusable interface interactions
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* --------------------------------------
       Password visibility toggle
       Add data-toggle-password to a button.
       Add data-password-input to its input.
    -------------------------------------- */

    document.addEventListener("click", (event) => {
        const toggle = event.target.closest("[data-toggle-password]");

        if (!toggle) return;

        const targetId = toggle.dataset.togglePassword;
        const input = document.getElementById(targetId);

        if (!input) return;

        const isPassword = input.type === "password";

        input.type = isPassword ? "text" : "password";
        toggle.setAttribute("aria-pressed", String(isPassword));

        toggle.textContent = isPassword ? "Hide" : "Show";
    });


    /* --------------------------------------
       Confirm important actions
       Add data-confirm="Your message"
       to a form or link.
    -------------------------------------- */

    document.addEventListener("submit", (event) => {
        const form = event.target;

        if (!(form instanceof HTMLFormElement)) return;

        const message = form.dataset.confirm;

        if (!message) return;

        if (!window.confirm(message)) {
            event.preventDefault();
        }
    });

    document.addEventListener("click", (event) => {
        const link = event.target.closest("a[data-confirm]");

        if (!link) return;

        if (!window.confirm(link.dataset.confirm)) {
            event.preventDefault();
        }
    });


    /* --------------------------------------
       Character counters
       Add data-character-counter to an input
       and data-counter-target="counter-id".
    -------------------------------------- */

    document.querySelectorAll("[data-character-counter]").forEach((input) => {
        const counterId = input.dataset.counterTarget;
        const counter = document.getElementById(counterId);

        if (!counter) return;

        const updateCounter = () => {
            const current = input.value.length;
            const maximum = input.maxLength > 0
                ? input.maxLength
                : null;

            counter.textContent = maximum
                ? `${current}/${maximum}`
                : `${current}`;

            counter.classList.toggle(
                "character-limit-reached",
                maximum !== null && current >= maximum
            );
        };

        input.addEventListener("input", updateCounter);
        updateCounter();
    });


    /* --------------------------------------
       Image previews
       Add data-image-preview to a file input.
       Add data-preview-target="image-id".
    -------------------------------------- */

    document.querySelectorAll("[data-image-preview]").forEach((input) => {
        input.addEventListener("change", () => {
            const file = input.files && input.files[0];

            const previewId = input.dataset.previewTarget;
            const preview = document.getElementById(previewId);

            if (!preview || !file) return;

            if (!file.type.startsWith("image/")) {
                window.dispatchEvent(new CustomEvent("devora:notify", {
                    detail: {
                        message: "Please select a valid image.",
                        type: "error"
                    }
                }));

                input.value = "";
                return;
            }

            const maximumSize = 5 * 1024 * 1024;

            if (file.size > maximumSize) {
                window.dispatchEvent(new CustomEvent("devora:notify", {
                    detail: {
                        message: "The image must be smaller than 5 MB.",
                        type: "error"
                    }
                }));

                input.value = "";
                return;
            }

            const reader = new FileReader();

            reader.addEventListener("load", () => {
                preview.src = reader.result;
                preview.hidden = false;
            });

            reader.readAsDataURL(file);
        });
    });


    /* --------------------------------------
       Copy text
       Add data-copy="text to copy".
    -------------------------------------- */

    document.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-copy]");

        if (!button) return;

        const value = button.dataset.copy;

        try {
            await navigator.clipboard.writeText(value);

            window.dispatchEvent(new CustomEvent("devora:notify", {
                detail: {
                    message: "Copied to clipboard.",
                    type: "success"
                }
            }));
        } catch (error) {
            window.dispatchEvent(new CustomEvent("devora:notify", {
                detail: {
                    message: "Could not copy the text.",
                    type: "error"
                }
            }));
        }
    });


    /* --------------------------------------
       Dropdown menus
       Button: data-dropdown-toggle="menu-id"
       Menu:   id="menu-id"
    -------------------------------------- */

    document.addEventListener("click", (event) => {
        const toggle = event.target.closest("[data-dropdown-toggle]");

        if (toggle) {
            const menuId = toggle.dataset.dropdownToggle;
            const menu = document.getElementById(menuId);

            if (!menu) return;

            const willOpen = menu.hidden;

            document.querySelectorAll("[data-dropdown-menu]").forEach((item) => {
                item.hidden = true;
            });

            menu.hidden = !willOpen;
            toggle.setAttribute("aria-expanded", String(willOpen));

            return;
        }

        if (!event.target.closest("[data-dropdown-menu]")) {
            document.querySelectorAll("[data-dropdown-menu]").forEach((menu) => {
                menu.hidden = true;
            });

            document.querySelectorAll("[data-dropdown-toggle]").forEach((button) => {
                button.setAttribute("aria-expanded", "false");
            });
        }
    });


    /* --------------------------------------
       Dismissible elements
       Add data-dismiss to the close button.
    -------------------------------------- */

    document.addEventListener("click", (event) => {
        const button = event.target.closest("[data-dismiss]");

        if (!button) return;

        const target = button.closest("[data-dismissible]");

        if (target) {
            target.remove();
        }
    });


    /* --------------------------------------
       Comment textarea keyboard behaviour
       Enter submits; Shift + Enter adds a line.
    -------------------------------------- */

    document.addEventListener("keydown", (event) => {
        const textarea = event.target;

        if (
            !(textarea instanceof HTMLTextAreaElement) ||
            !textarea.matches("[data-comment-input]")
        ) {
            return;
        }

        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();

            const form = textarea.closest("form");

            if (form && form.requestSubmit) {
                form.requestSubmit();
            }
        }
    });

});
