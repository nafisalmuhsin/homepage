<!DOCTYPE html>
<html lang="en">
<head>

    <link rel="stylesheet" type="text/css" href="newstyle.css">
    <meta charset="UTF-8">
	
	
	
    <title>View Requests</title>
    <style>
       
        .content {
            margin: 20px;
        }

        .request-table {
            width: 100%;
            border-collapse: collapse;
        }

        .request-table th,
        .request-table td {
            border: 1px solid #ccc;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="navigate">
        <img src="brand_logo.png" alt="Chollerton Tearooms logo" class="slogo">
        <a href="assignment.html">Home</a>
        <a href="more.html">Find out more</a>
        <a class="active" href="requests.php">View requests</a>
        <a href="credits.html">Credits</a>
    </div>

    <img src="brand_logo.png" alt="Chollerton Tearooms logo" class="logo">
    <h1 class="title">Chollerton Tearrooms</h1>

    <div class="break">
        <p>&nbsp;</p>
    </div>

    <div class="content">
        <h2>Requests for More Information</h2>

        
        
<?php
// Here I connect to my database
$mysqli = new mysqli('localhost', 'unn_w22025411', 'Cssfad60', 'unn_w22025411');

// Here I check for connection errors
if ($mysqli->connect_error) {
    die('Connect Error (' . $mysqli->connect_errno . ') ' . $mysqli->connect_error);
}

// Here I am creating the SQL query to fetch the requests with category descriptions
$sql = "SELECT e.forename, e.surname, e.postalAddress, e.mobileTelNo, e.email, e.sendMethod, c.catDesc AS categoryDescription
        FROM CT_expressedInterest e
        INNER JOIN CT_category c ON e.catID = c.catID
        ORDER BY e.surname";

 // Here I execute the SQL query
 $result = $mysqli->query($sql);

// Here I check for any records
if ($result && $result->num_rows > 0) {
    // Here i create a table in my HTML to display the requests
     echo '<table class="request-table">';
     echo '<tr><th>Forename</th><th>Surname</th><th>Postal Address</th><th>Mobile Tel No</th><th>Email</th><th>Send Method</th><th>Category</th></tr>';

   // Here i get it to loop through each record and show the details in table rows
    while ($row = $result->fetch_assoc()) {
        $forename = $row['forename'];
        $surname = $row['surname'];
        $postalAddress = $row['postalAddress'];
        $mobileTelNo = $row['mobileTelNo'];
        $email = $row['email'];
        $sendMethod = $row['sendMethod'];
        $categoryDescription = $row['categoryDescription'];

        // Here i show the details in table rows
        echo "<tr>";
        echo "<td>$forename</td>";
        echo "<td>$surname</td>";
        echo "<td>$postalAddress</td>";
        echo "<td>$mobileTelNo</td>";
        echo "<td>$email</td>";
        echo "<td>$sendMethod</td>";
        echo "<td>$categoryDescription</td>";
        echo "</tr>";
    }

    echo '</table>'; 
	
} else {
    // Here i show a message if there are no records
    echo "<p>No requests found.</p>";
}

// Now I close the database connection
$mysqli->close();
?>


    </div>
</body>
</html>

