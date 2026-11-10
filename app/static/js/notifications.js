
/* ==========================================
   DEVORA — NOTIFICATIONS
   Toast notifications and message handling
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* --------------------------------------
       Notification container
    -------------------------------------- */

    let notificationContainer = document.getElementById(
        "devora-notifications"
    );

    if (!notificationContainer) {
        notificationContainer = document.createElement("div");

        notificationContainer.id = "devora-notifications";
        notificationContainer.className = "notification-container";
        notificationContainer.setAttribute("aria-live", "polite");
        notificationContainer.setAttribute("aria-atomic", "false");

        document.body.appendChild(notificationContainer);
    }


    /* --------------------------------------
       Create notification
    -------------------------------------- */

    function showNotification(message, type = "info", duration = 3500) {

        if (!message || typeof message !== "string") return;

        const allowedTypes = ["success", "error", "warning", "info"];

        if (!allowedTypes.includes(type)) {
            type = "info";
        }

        const notification = document.createElement("div");

        notification.className = `devora-notification notification-${type}`;
        notification.setAttribute("role", type === "error" ? "alert" : "status");

        const messageElement = document.createElement("span");
        messageElement.className = "notification-message";
        messageElement.textContent = message;

        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "notification-close";
        closeButton.textContent = "×";
        closeButton.setAttribute("aria-label", "Dismiss notification");

        notification.appendChild(messageElement);
        notification.appendChild(closeButton);

        notificationContainer.appendChild(notification);

        requestAnimationFrame(() => {
            notification.classList.add("notification-visible");
        });

        let dismissed = false;

        function dismiss() {
            if (dismissed) return;

            dismissed = true;

            notification.classList.remove("notification-visible");
            notification.classList.add("notification-removing");

            window.setTimeout(() => {
                notification.remove();
            }, 250);
        }

        closeButton.addEventListener("click", dismiss);

        if (duration > 0) {
            window.setTimeout(dismiss, duration);
        }
    }


    /* --------------------------------------
       Listen for notifications from other JS
       Example:
       window.dispatchEvent(
           new CustomEvent("devora:notify", {
               detail: {
                   message: "Post saved!",
                   type: "success"
               }
           })
       );
    -------------------------------------- */

    window.addEventListener("devora:notify", (event) => {
        const details = event.detail || {};

        showNotification(
            details.message,
            details.type || "info",
            details.duration || 3500
        );
    });


    /* --------------------------------------
       Expose notification function
    -------------------------------------- */

    window.DevoraNotifications = {
        show: showNotification
    };


    /* --------------------------------------
       Existing server-side flash messages
       Only auto-dismiss messages that explicitly
       have data-auto-dismiss="true".
    -------------------------------------- */

    document.querySelectorAll(
        '[data-auto-dismiss="true"]'
    ).forEach((message) => {

        window.setTimeout(() => {
            message.classList.add("flash-hidden");

            window.setTimeout(() => {
                message.remove();
            }, 300);
        }, 4500);

    });

});
