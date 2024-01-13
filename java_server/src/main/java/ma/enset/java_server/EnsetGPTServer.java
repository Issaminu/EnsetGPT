package ma.enset.java_server;


import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import org.json.JSONException;
import org.json.JSONObject;
import org.springframework.http.ResponseEntity;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.sql.*;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class EnsetGPTServer {
    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/api/send-message", new MessagingHandler());
        server.setExecutor(null);
        server.start();
        System.out.println("Server started on port 8080");
    }

    static class MessagingHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String requestMethod = exchange.getRequestMethod();
            if(!requestMethod.equalsIgnoreCase("POST")) {
                // Only accept POST requests
                exchange.sendResponseHeaders(405, -1);
                return;
            }

            exchange.getResponseHeaders().set("Content-Type", "text/plain");
            InputStream requestBody = exchange.getRequestBody();
            String jsonRequest = convertStreamToString(requestBody);
            
            try {
                String currentWorkingDir = System.getProperty("user.dir");

                // Set the working directory to the 'ai_chat' directory
                File aiChatDir = new File(currentWorkingDir, "ai_chat");
                String pythonQueryPath = "query.py";

                // Build the command to execute
                JSONObject jsonObject = new JSONObject(jsonRequest);
                String sessionId = jsonObject.getString("session_id");
                if(sessionId.isEmpty()) {
                    sessionId = "1";
                }
                String message = jsonObject.getString("message");
                List<String> command = Arrays.asList("python3.11", "-u", pythonQueryPath, sessionId, message);
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
                System.out.println("response: " + response);
                resultSet.close();
                preparedStatement.close();
                connection.close();
                String jsonResponse = "{\"message\": \"" + response + "\"}";
                exchange.sendResponseHeaders(200, jsonResponse.length());
                OutputStream os = exchange.getResponseBody();
                os.write(jsonResponse.getBytes());
                os.close();
                return;
            } catch (JSONException | ClassNotFoundException | SQLException | IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
             System.out.println("error buddy");
        }

        private String convertStreamToString(InputStream inputStream) {
            Scanner scanner = new Scanner(inputStream, StandardCharsets.UTF_8).useDelimiter("\\A");
            return scanner.hasNext() ? scanner.next() : "";
        }


    }
}
