module ma.enset.javafxfrontendchatbotenset {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.web;

    requires org.controlsfx.controls;
    requires com.dlsc.formsfx;
    requires org.kordamp.bootstrapfx.core;
    requires eu.hansolo.tilesfx;

    opens ma.enset.javafxfrontendchatbotenset to javafx.fxml;
    exports ma.enset.javafxfrontendchatbotenset;
}