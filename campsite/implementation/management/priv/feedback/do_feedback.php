<?php
require_once "HTTP/Client.php";
require_once($_SERVER['DOCUMENT_ROOT'] . "/classes/BugReporter.php");
require_once($_SERVER['DOCUMENT_ROOT'] . "/classes/Input.php");
camp_load_translation_strings("bug_reporting");

//
// Post the error to server
//

global $Campsite, $ADMIN_DIR, $g_documentRoot, $g_bugReporterDefaultServer;

$server = $g_bugReporterDefaultServer;
//$server = "http://localhost/trac/autotrac";
$f_isFromInterface = Input::Get("f_isFromInterface", "boolean", false);
$f_email = Input::Get("f_email", "string", "", true);
$f_description = Input::Get("f_description", "string", "", true);


// --- If this information is a POST from errormessage.php, send it to
//     the server ---
if ($f_isFromInterface && ($_SERVER['REQUEST_METHOD'] == "POST") ) {

    $wasSent = false;

    $reporter = new BugReporter(0, "", "", "", "Campsite", $Campsite['VERSION']);
    $reporter->setServer($server);
    $reporter->setDescription($f_description);
    $reporter->setEmail($f_email);        
    $wasSent = $reporter->sendToServer();


    // --- Verify send was successful, and say thank you or sorry
    //     accordingly ---
    if ($wasSent == true) {
        include($Campsite['HTML_DIR'] . "/$ADMIN_DIR/feedback/thankyou.php");
    } else {
    	include($Campsite['HTML_DIR'] . "/$ADMIN_DIR/feedback/emailus.php");
    }
}

?>