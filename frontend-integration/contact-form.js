const CONTACT_EMAIL = "kothagundlamurthy@gmail.com";
const contactForm = document.querySelector("#contact-form");
const formStatus = document.querySelector("#form-status");
const isLocalDevelopment =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";
const API_BASE =
  contactForm?.dataset.apiBase?.trim() ||
  (isLocalDevelopment ? "http://127.0.0.1:8000" : "");

function showEmailFallback(payload, reason) {
  if (!formStatus) return;

  const emailBody = [
    `Name: ${payload.name}`,
    `Email: ${payload.email}`,
    "",
    payload.message,
  ].join("\n");
  const mailto = new URL(`mailto:${CONTACT_EMAIL}`);
  mailto.searchParams.set("subject", `Portfolio contact: ${payload.subject}`);
  mailto.searchParams.set("body", emailBody);

  const emailLink = document.createElement("a");
  emailLink.href = mailto.toString();
  emailLink.textContent = "Open your email app";

  formStatus.replaceChildren(
    document.createTextNode(`${reason} `),
    emailLink,
    document.createTextNode(` to send your message to ${CONTACT_EMAIL}.`)
  );
}

if (contactForm) {
  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = contactForm.querySelector('button[type="submit"]');

    const formData = new FormData(contactForm);
    const payload = {
      name: String(formData.get("name") || "").trim(),
      email: String(formData.get("email") || "").trim(),
      subject: String(formData.get("subject") || "").trim(),
      message: String(formData.get("message") || "").trim(),
    };

    if (!API_BASE) {
      showEmailFallback(
        payload,
        "The online message service is not configured. Your message has not been sent."
      );
      return;
    }

    if (formStatus) {
      formStatus.textContent = "Sending message...";
    }
    if (submitButton) submitButton.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      if (!response.ok) {
        const details = Array.isArray(result.detail)
          ? result.detail.map((item) => item.msg).join("; ")
          : result.detail || "Unable to send your message.";
        throw new Error(details);
      }

      if (formStatus) {
        formStatus.textContent = result.message;
      }
      contactForm.reset();
    } catch (error) {
      if (formStatus) {
        const message = error instanceof Error
          ? error.message
          : "Unable to send your message.";
        const reason = isLocalDevelopment
          ? `${message} Your message has not been sent.`
          : "Could not reach the online message service. Your message has not been sent.";
        showEmailFallback(payload, reason);
      }
    } finally {
      if (submitButton) submitButton.disabled = false;
    }
  });
}
