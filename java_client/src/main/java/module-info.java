module ma.enset.java_client {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.web;

    requires org.controlsfx.controls;
    requires com.dlsc.formsfx;
    requires org.kordamp.bootstrapfx.core;
    requires eu.hansolo.tilesfx;
    requires spring.web;

    opens ma.enset.java_client to javafx.fxml;
    exports ma.enset.java_client;
}