import axios from "axios";

const API_URL = "http://localhost:8000/api";

export const sendMessageToApi = async (message: string): Promise<string> => {
  try {
    const response = await axios.post(API_URL, { message });
    return response.data.reply;
  } catch (error) {
    console.error("Error communicating with the API:", error);
    return "Sorry, something went wrong while connecting to the server.";
  }
};
