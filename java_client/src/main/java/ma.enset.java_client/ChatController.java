package ma.enset.java_client;

import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ListView;
import javafx.scene.control.TextField;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
public class ChatController {

    @FXML
    private Button sendButton;

    @FXML
    private ListView<String> chatListView;

    @FXML
    private TextField messageTextField;

    @FXML
    public void sendMessage(ActionEvent event) {
        String message = messageTextField.getText();
        if (message.isEmpty()) {
            return;
        }
        chatListView.getItems().add("You: " + message);
        sendButton.setDisable(true); // Disable the button before sending the request

        // Clear the text field after adding the message to the list
        messageTextField.clear();

        chatListView.scrollTo(chatListView.getItems().size() - 1);
        String sessionId;
        if(chatListView.getItems().isEmpty()) {
            sessionId = null;
        } else {
            // TODO: Implement session management logic
            sessionId = "1";
        }

        new Thread(() -> {
            String response = sendRequest(message, sessionId);

            // Update UI with the response on the JavaFX Application Thread
            Platform.runLater(() -> {
                chatListView.getItems().add("EnsetGPT: " + response);

                // Enable the button after receiving the response
                sendButton.setDisable(false);
            });
        }).start();
    }


    private static String sendRequest(String message, String sessionId) {


        String backendUrl = "http://localhost:8080/api/send-message";

        // Create headers if needed
        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-Type", "application/json");

        // Create the request body
        String requestBody = "{\"message\": \"" + message + "\", \"session_id\": \"" + sessionId + "\"}";

        // Create the HttpEntity with headers and body
        HttpEntity<String> requestEntity = new HttpEntity<>(requestBody, headers);

        // Create a RestTemplate
        RestTemplate restTemplate = new RestTemplate();

        // Make the API request
        ResponseEntity<String> responseEntity = restTemplate.exchange(
                backendUrl,
                HttpMethod.POST,
                requestEntity,
                String.class
        );

        // Handle the response as needed
        return responseEntity.getBody();
    }

    @FXML
    private void handleEnterKey(KeyEvent event) {
        if (event.getCode() == KeyCode.ENTER) {
            // Simulate clicking the button
            sendMessage(null);
        }
    }
}
