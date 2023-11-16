import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api")
public class ApiController {

    @PostMapping("/send-message")
    public ResponseEntity<String> processJsonRequest(@RequestBody String jsonRequest) {
        // Process JSON request, interact with Python files, and handle responses
        String pythonResponse = jsonRequest+" processed by Java";
        // Send JSON response
        return ResponseEntity.ok(pythonResponse);
    }

    // Add more methods for other endpoints as needed
}
