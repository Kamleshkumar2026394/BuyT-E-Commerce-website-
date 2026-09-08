document.addEventListener("DOMContentLoaded", function () {

    // ========================================
    // GET CHATBOT ELEMENTS
    // ========================================

    const chatbotToggle = document.getElementById("chatbot-toggle");
    const chatbotWindow = document.getElementById("chatbot-window");
    const chatbotClose = document.getElementById("chatbot-close");

    const chatInput = document.getElementById("chatbot-input");
    const sendButton = document.getElementById("chatbot-send");
    const chatMessages = document.getElementById("chatbot-messages");


    // ========================================
    // OPEN CHATBOT
    // ========================================

    chatbotToggle.addEventListener("click", function () {

        chatbotWindow.style.display = "flex";

        chatInput.focus();

    });


    // ========================================
    // CLOSE CHATBOT
    // ========================================

    chatbotClose.addEventListener("click", function () {

        chatbotWindow.style.display = "none";

    });


    // ========================================
    // SEND MESSAGE
    // ========================================

    async function sendMessage() {

        const message = chatInput.value.trim();

        if (!message) {
            return;
        }


        // Show user message
        addMessage(message, "user");


        // Clear input
        chatInput.value = "";


        // Disable send button
        sendButton.disabled = true;


        // Show loading
        const loadingMessage = addMessage("Thinking...", "bot");


        try {

            const response = await fetch("/chat/", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },

                body: JSON.stringify({
                    message: message
                })

            });


            const data = await response.json();


            // Remove loading
            loadingMessage.remove();


            if (response.ok) {

                addMessage(
                    data.answer || "Sorry, I couldn't generate a response.",
                    "bot"
                );

            } else {

                addMessage(
                    data.error || "Something went wrong.",
                    "bot"
                );

            }


        } catch (error) {

            console.error("Chat error:", error);


            loadingMessage.remove();


            addMessage(
                "Sorry, I couldn't connect to BuyT AI.",
                "bot"
            );


        } finally {

            sendButton.disabled = false;

            chatInput.focus();

        }

    }


    // ========================================
    // ADD MESSAGE
    // ========================================

    function addMessage(message, sender) {

        const messageDiv = document.createElement("div");


        if (sender === "user") {

            messageDiv.className = "user-message";

        } else {

            messageDiv.className = "bot-message";

        }


        messageDiv.textContent = message;


        chatMessages.appendChild(messageDiv);


        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;


        return messageDiv;

    }


    // ========================================
    // SEND BUTTON
    // ========================================

    sendButton.addEventListener("click", sendMessage);


    // ========================================
    // ENTER KEY
    // ========================================

    chatInput.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    });


    // ========================================
    // CSRF TOKEN
    // ========================================

    function getCookie(name) {

        let cookieValue = null;


        if (document.cookie && document.cookie !== "") {

            const cookies = document.cookie.split(";");


            for (let cookie of cookies) {

                cookie = cookie.trim();


                if (cookie.startsWith(name + "=")) {

                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;

                }

            }

        }


        return cookieValue;

    }

});