/*
Integration helper for your existing Contact.html.
1. Give your contact form id="contact-form".
2. Form controls must have name="name", "email", "subject", and "message".
3. Add <p id="form-status" role="status" aria-live="polite"></p> under the form.
4. Change API_BASE to your deployed backend URL after hosting it.
*/
const contactForm = document.querySelector("#contact-form");
const formStatus = document.querySelector("#form-status");
const isLocalDevelopment =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";
const API_BASE =
  contactForm?.dataset.apiBase?.trim() ||
  (isLocalDevelopment ? "http://127.0.0.1:8000" : "");

if (contactForm) {
  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = contactForm.querySelector('button[type="submit"]');

    if (!API_BASE) {
      if (formStatus) {
        formStatus.textContent =
          "The online message service is not configured yet. Please email kothagundlamurthy@gmail.com instead.";
      }
      return;
    }

    const formData = new FormData(contactForm);
    const payload = {
      name: String(formData.get("name") || "").trim(),
      email: String(formData.get("email") || "").trim(),
      subject: String(formData.get("subject") || "").trim(),
      message: String(formData.get("message") || "").trim(),
    };

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
        formStatus.textContent = isLocalDevelopment
          ? `${message} Check that FastAPI is running locally.`
          : `${message} Please email kothagundlamurthy@gmail.com if the problem continues.`;
      }
    } finally {
      if (submitButton) submitButton.disabled = false;
    }
  });
}
