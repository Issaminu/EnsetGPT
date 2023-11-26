package ma.enset.java_server;

import org.json.JSONException;
import org.json.JSONObject;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api")
public class ApiController {

    @PostMapping("/send-message")
    public ResponseEntity<String> processJsonRequest(@RequestBody String jsonRequest) {
        System.out.println("Received request with JSON: " + jsonRequest);
        try {
            String currentWorkingDir = System.getProperty("user.dir");

            // Set the working directory to the 'ai_chat' directory
            File aiChatDir = new File(currentWorkingDir, "ai_chat");
            String pythonQueryPath = "query.py";

            // Build the command to execute
            JSONObject jsonObject = new JSONObject(jsonRequest);
            String sessionId = jsonObject.getString("session_id");
            String message = jsonObject.getString("message");
            List<String> command = Arrays.asList("python", "-u", pythonQueryPath, sessionId, message);
            System.out.println("Executing command: " + command);
            ProcessBuilder processBuilder = new ProcessBuilder(command).directory(aiChatDir);
            Process process = processBuilder.start();
            process.waitFor();

            Class.forName("org.sqlite.JDBC");
            String url = "jdbc:sqlite:ai_chat/persist/chat_history.db";
            Connection connection = DriverManager.getConnection(url);
            PreparedStatement preparedStatement = connection.prepareStatement("SELECT * FROM message_store WHERE type = 'ai' AND session_id = ? ORDER BY timestamp DESC LIMIT 1;");
            preparedStatement.setString(1, sessionId);
            ResultSet resultSet = preparedStatement.executeQuery();
            String response = resultSet.getString("message");
            resultSet.close();
            preparedStatement.close();
            connection.close();
            return ResponseEntity.ok(response);

        } catch (JSONException | ClassNotFoundException | SQLException | IOException e) {
               e.printStackTrace();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        return ResponseEntity.ok("error buddy");
    }
}
