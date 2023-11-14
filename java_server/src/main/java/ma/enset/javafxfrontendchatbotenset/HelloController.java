package ma.enset.javafxfrontendchatbotenset;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;

public class HelloController {
    public Button hehe;
    @FXML
    private Label welcomeText;

    @FXML
    protected void onHelloButtonClick() {
        welcomeText.setText("Welcome to JavaFX Application!");
}

    public void onButtonClick(ActionEvent actionEvent) {

    }

    public void onHHH(ActionEvent actionEvent) {

    }
}