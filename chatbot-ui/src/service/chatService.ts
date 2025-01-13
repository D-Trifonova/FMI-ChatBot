import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export const sendMessageToApi = async (userMessage: string): Promise<string> => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            question: userMessage,
        });

        if (response.status === 200) {
            const { title, context_excerpt, url } = response.data;

            // Construct a bot response using the API output
            return `Here’s what I found:\n\nTitle: ${title}\nContext: ${context_excerpt}\nURL: ${url}`;
        } else {
            throw new Error("Unexpected response from the server.");
        }
    } catch (error) {
        console.error("Error communicating with the API:", error);
        return "Sorry, something went wrong. Please try again later.";
    }
};
