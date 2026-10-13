document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("recommend-form");
    if (!form) {
        return;
    }

    const topicSelect = document.getElementById("topic");
    const customWrap = document.getElementById("custom-topic-wrap");
    const customInput = document.getElementById("custom_topic");
    const errorBox = document.getElementById("form-error");

    const toggleCustomTopic = () => {
        const isOther = topicSelect.value === "Other";
        customWrap.classList.toggle("hidden", !isOther);
        customInput.required = isOther;
        if (!isOther) {
            customInput.value = "";
        }
    };

    topicSelect.addEventListener("change", toggleCustomTopic);
    toggleCustomTopic();

    form.addEventListener("submit", (event) => {
        const subject = document.getElementById("subject").value.trim();
        const topic = topicSelect.value.trim();
        const customTopic = customInput.value.trim();
        const level = document.getElementById("level").value.trim();
        const resourceType = document.getElementById("resource_type").value.trim();

        let message = "";
        if (!subject) {
            message = "Please select a subject.";
        } else if (!topic) {
            message = "Please select a topic.";
        } else if (topic === "Other" && !customTopic) {
            message = "Please type your topic.";
        } else if (!level) {
            message = "Please select a learning level.";
        } else if (!resourceType) {
            message = "Please select a resource type.";
        }

        if (message) {
            event.preventDefault();
            errorBox.textContent = message;
            errorBox.classList.remove("hidden");
            return;
        }

        errorBox.classList.add("hidden");
    });
});
