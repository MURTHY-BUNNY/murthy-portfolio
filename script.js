
/* ==========================================
   KOTHAGUNDLA MURTHY — PORTFOLIO
   Complete JavaScript
   ========================================== */

(() => {
    "use strict";

    /* ==========================================
       1. INITIAL SETUP
    ========================================== */

    const root = document.documentElement;

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;


    /* ==========================================
       2. HOMEPAGE MENU
    ========================================== */

    const menuButton = document.getElementById("menuButton");
    const siteMenu = document.getElementById("siteMenu");

    if (menuButton && siteMenu) {

        menuButton.addEventListener("click", () => {
            const isOpen =
                menuButton.getAttribute("aria-expanded") === "true";

            menuButton.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );

            siteMenu.hidden = isOpen;
        });

        // Close the menu with Escape.
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !siteMenu.hidden) {
                siteMenu.hidden = true;

                menuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

                menuButton.focus();
            }
        });

        // Close the menu after selecting a link.
        siteMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                siteMenu.hidden = true;

                menuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            });
        });

        // Close the menu when clicking outside it.
        document.addEventListener("click", (event) => {
            if (
                !siteMenu.hidden &&
                !siteMenu.contains(event.target) &&
                !menuButton.contains(event.target)
            ) {
                siteMenu.hidden = true;

                menuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        });
    }


    /* ==========================================
       3. HOMEPAGE ENTRANCE ANIMATIONS
    ========================================== */

    if (!reduceMotion) {
        root.classList.add("is-entering");

        window.requestAnimationFrame(() => {
            root.classList.add("is-playing");
        });

        // Safety cleanup for the existing startup animation state.
        window.setTimeout(() => {
            root.classList.remove("is-entering", "is-playing");
        }, 4500);
    } else {
        root.classList.remove("is-entering", "is-playing");
    }


    /* ==========================================
       4. SCROLL-REVEAL ANIMATIONS
    ========================================== */

    const revealElements = document.querySelectorAll(
        ".intro, .work-section, .project-card, .contact-cta, .home-footer"
    );

    if (
        reduceMotion ||
        !("IntersectionObserver" in window)
    ) {
        // Keep all content visible if motion is disabled
        // or the browser does not support IntersectionObserver.
        revealElements.forEach((element) => {
            element.classList.add("is-visible");
        });
    } else {

        const revealObserver = new IntersectionObserver(
            (entries, observer) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");

                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.12,
                rootMargin: "0px 0px -35px 0px"
            }
        );

        revealElements.forEach((element) => {
            element.classList.add("js-reveal");

            // Stagger project-card animations.
            if (element.classList.contains("project-card")) {
                const cards = Array.from(
                    document.querySelectorAll(".project-card")
                );

                const cardIndex = cards.indexOf(element);

                element.style.transitionDelay =
                    `${cardIndex * 100}ms`;
            }

            revealObserver.observe(element);
        });
    }


    /* ==========================================
       5. INNER-PAGE NAVIGATION MENUS
       Education, Skills, Projects, Contact, About
    ========================================== */

    const innerMenuButton =
        document.getElementById("innerMenuButton");

    const innerNav =
        document.getElementById("innerNav");

    if (innerMenuButton && innerNav) {

        innerMenuButton.addEventListener("click", () => {
            const isOpen =
                innerMenuButton.getAttribute("aria-expanded") === "true";

            innerMenuButton.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );

            innerNav.hidden = isOpen;

            innerMenuButton.textContent = isOpen
                ? "MENU +"
                : "CLOSE −";
        });

        // Close the inner-page menu with Escape.
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !innerNav.hidden) {
                innerNav.hidden = true;

                innerMenuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

                innerMenuButton.textContent = "MENU +";

                innerMenuButton.focus();
            }
        });

        // Close the menu after selecting a page.
        innerNav.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                innerNav.hidden = true;

                innerMenuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

                innerMenuButton.textContent = "MENU +";
            });
        });
    }

})();
