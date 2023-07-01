<?php
// Here I connect to my database
$mysqli = new mysqli('localhost', 'unn_w22025411', 'Cssfad60', 'unn_w22025411');

// Here I check for connection errors
   if ($mysqli->connect_error) {
  die('Connect Error (' . $mysqli->connect_errno . ') '
    . $mysqli->connect_error);
}

  // Here I check if the form has been submitted
  if ($_SERVER['REQUEST_METHOD'] == 'POST') {
  
  // Here I get the values submitted in the form while using real_escape to improve secuirty
  $forename = isset($_REQUEST['forename']) ? $mysqli->real_escape_string($_REQUEST['forename']) : null;
  $surname = isset($_REQUEST['surname']) ? $mysqli->real_escape_string($_REQUEST['surname']) : null;
  $postalAddress = isset($_REQUEST['postalAddress']) ? $mysqli->real_escape_string($_REQUEST['postalAddress']) : null;
  $mobileTelNo = isset($_REQUEST['mobileTelNo']) ? $mysqli->real_escape_string($_REQUEST['mobileTelNo']) : null;
  $email = isset($_REQUEST['email']) ? $mysqli->real_escape_string($_REQUEST['email']) : null;
  $sendMethod = isset($_REQUEST['sendMethod']) ? $mysqli->real_escape_string($_REQUEST['sendMethod']) : null;
  $catID = isset($_REQUEST['catID']) ? $mysqli->real_escape_string($_REQUEST['catID']) : null;

   // Here i am running a form input validation
    if (empty($forename) || empty($surname) || empty($catID)) {
        die('Your form has NOT been submitted. Please fill in all required fields.');
    }

    if (empty($sendMethod)) {
        die('Your form has NOT been submitted. Please select at least one method of contact.');
    }
   // Here I am creating the SQL query to retrieve the category description
    $categoryQuery = "SELECT catDesc FROM CT_category WHERE catID = '$catID'";
    $categoryResult = $mysqli->query($categoryQuery);

    if ($categoryResult->num_rows > 0) {
        $categoryRow = $categoryResult->fetch_assoc();
        $categoryDesc = $categoryRow['catDesc'];
    } else {
        $categoryDesc = 'Unknown';
    }	

  // Here I am creating the SQL query string
  $sql = "INSERT INTO CT_expressedInterest (forename, surname, postalAddress, mobileTelNo, email, sendMethod, catID) VALUES ('$forename', '$surname', '$postalAddress', '$mobileTelNo', '$email', '$sendMethod', '$catID')";

  // Here I execute the SQL query
  $success = $mysqli->query($sql);

  // Here I check if the insert query was successful
  if ($success) {
    // Here I display the thank you message with html so that it is more appealing
      echo '
   <html lang="en">
    <head>
    <link rel="stylesheet" type="text/css" href="newstyle.css">
    <meta charset="UTF-8">
	
    <title>Submission summary</title>
            
    </head>
    <body>
        <div class="navigate">
            <img src="brand_logo.png" alt="Chollerton Tearooms logo" class="slogo">
            <a href="assignment.html">Home</a>
             <a class="active" href="more.html">Find out more</a>
             <a href="requests.php">View requests</a>
             <a href="credits.html">Credits</a>
        </div>
			
			
     <img src="brand_logo.png" alt="Chollerton Tearooms logo" class="logo">        
	<h1 style="text-align: center;">Chollerton Tearrooms</h1>
	
	
  <div class="redirect">
        <h2>Your Submission Details:</h2>
        <p>Forename: ' . $forename . '</p>
        <p>Surname: ' . $surname . '</p>
		<p>Postal Address: ' . $postalAddress . '</p>
        <p>Mobile Phone Number: ' . $mobileTelNo . '</p>
		<p>Email Address: ' . $email . '</p>
		<p>Facility Category: ' . $categoryDesc . '</p>
		<p>Chosen Method of contact: ' . $sendMethod . '</p>
         <br>
        <p>Thank you for submitting your interest. We will be in touch soon!</p><br>
        <a class="active" href="more.html">Submit a new form</a>      
     </div>
	 
	 
        </body>
        </html>
        ';
  } else {
    // Here i display an error message if the insert query failed
    echo 'Error: ' . $mysqli->error;
  }

  // Now I close the database connection
  $mysqli->close();
}
?>
