package ma.enset.javafxfrontendchatbotenset;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
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
    private ListView<String> chatListView;

    @FXML
    private TextField messageTextField;

    @FXML
    public void sendMessage(ActionEvent event) {
        String message = messageTextField.getText();
        if (!message.isEmpty()) {
            chatListView.getItems().add("You: " + message);
            messageTextField.clear();
        }
        chatListView.scrollTo(chatListView.getItems().size() - 1);
        sendRequest(message);
    }

    private static void sendRequest(String message) {
        String backendUrl = "http://localhost:8080/api/process-json";  // Replace with your actual backend URL

        // Create headers if needed
        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-Type", "application/json");

        // Create the request body
        String requestBody = "{ \"key\": \"value\" }";  // Replace with your actual JSON request body

        // Create the HttpEntity with headers and body
        HttpEntity<String> requestEntity = new HttpEntity<>(requestBody, headers);

        // Create a RestTemplate
        RestTemplate restTemplate = new RestTemplate();

        // Make the API request
        ResponseEntity<String> responseEntity = restTemplate.exchange(
                backendUrl,
                HttpMethod.POST,  // Use the appropriate HTTP method (GET, POST, etc.)
                requestEntity,
                String.class  // Adjust based on the expected response type
        );

        // Handle the response as needed
        String responseBody = responseEntity.getBody();
    }

    @FXML
    private void handleEnterKey(KeyEvent event) {
        if (event.getCode() == KeyCode.ENTER) {
            // Simulate clicking the button
            sendMessage(null);
        }
    }
}
