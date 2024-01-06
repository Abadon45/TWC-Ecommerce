<?php 

 //contact form info
 $name=  $_POST['name'];
 $email=  $_POST['email'];
 $subject = $_POST['subject'];
 $contact_message = $_POST['message'];


 $message = "<b>Mail Sender Info:</b> </br>
            <h5><b>Name:</b>".$name."</h5>
            <h5><b>Email:</b>".$email."</h5>
            </br>
            <p>".$contact_message."</p>";
            
            
 $to = "contact@example.com"; //Replace your real receiving email address

 $header = "From:info@example.com \r\n"; //Replace with your real web master email
 $header .= "MIME-Version: 1.0\r\n";
 $header .= "Content-type: text/html\r\n";
 
 $mail_send = mail ($to,$subject,$message,$header);
 
//  if( $mail_send == true ) {
//     echo "Your message send successfully!.";
//  }else {
//     echo "Your message could not be send!.";
//  }

echo "Your message send successfully!.";


?>