package ma.enset.java_server;

import org.json.JSONException;
import org.json.JSONObject;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

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
            String command = "python -u " + pythonQueryPath + " " + new JSONObject(jsonRequest).getString("message");
            System.out.println("Executing command: " + command);
            ProcessBuilder processBuilder = new ProcessBuilder(command.split("\\s+")).directory(aiChatDir);
            Process process = processBuilder.start();


            // Get input stream to read the Python script's output
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();

            // Read the output of the Python script
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }

            // Handle the output and exit code as needed
            System.out.println("Python script output:\n" + output);
            return ResponseEntity.ok(output.toString());

        } catch (IOException | JSONException e) {
            e.printStackTrace();
        }
        return ResponseEntity.ok("error buddy");
    }
}
