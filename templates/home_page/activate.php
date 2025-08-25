<?php require_once('Connections/halicnn.php'); 
mysql_select_db($database_halicnn);
?>
<?php
$updatecode = "UPDATE userdetails SET active = 1 WHERE actcode = '$_GET[lnk]'";
$runq = mysql_query($updatecode) or die(mysql_error());
?>
<table border="0" width="100%" align="left" id="table1">
	<tr>
		<td>
      <table border="0" cellpadding="0" cellspacing="0" height="62"
 width="100%" id="table99">
          <tr>
        <td width="100%" height="36" style="color: #FF0000" bgcolor="#FFFFFF">

		<table border="0" width="100%" id="table100">
			<tr>
								<td width="9%" style="color: #FF0000; font-family:Tahoma; font-size:11.5px">
								<p align="center">
								<img border="0" src="images/logo.png" width="253" height="60" align="left"></td>
								<td width="27%" style="color: #FF0000; font-family:Tahoma; font-size:11.5px">
								&nbsp;</td>
								<td width="26%" style="color: #FF0000; font-family:Tahoma; font-size:11.5px">
								&nbsp;</td>
								<td style="color: #FF0000; font-family:Tahoma; font-size:11.5px" width="26%">
								<div align="right">
									<table border="0" width="43%" id="table101">
										<tr>
											<td width="246" style="color: #FF0000; font-family:Tahoma; font-size:11.5px">
											</td>
										</tr>
									</table>
								<div id="language">
	<font color="#FFFFFF" face="Georgia" style="font-size: 8pt"><b> &nbsp;</b></font><div id="google_translate_element"></div><script>
function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'en',
    multilanguagePage: true,
    gaTrack: true,
    layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL
  }, 'google_translate_element');
}
function doTranslate(newValue){
		//var lang_dropdown = document.getElementById(':0.targetLanguage').firstChild;        lang_dropdown.value = newValue;
	google.language.translate(translateDiv.get("html"),'en',newValue,callback);


}
</script><script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
		 
		</div></div>
								</td>
							</tr>
		</table>
		</td>
      	</tr>
			<tr>
        <td width="100%" height="26" background="images/topper.jpg" style="color: #FF0000">

<font color="#FFFFFF" face="Verdana"><span style="font-size: 9pt">
					<marquee> Global Trust Bank -&nbsp; Secured Internet Bank</marquee></span></font></td>
      	</tr>
          </table>
    
    
		<font face="Arial" size="2"><br>
		</font><font face="Arial"><b>Account Activated !</b></font><font face="Arial" size="2"><br>
&nbsp;</font></td>
	</tr>
	<tr>
		<td height="113"><font face="Arial" size="2">Your account has been activated successfully, <br>
Please note that this registration would be subjected to confirmation<br>
once this is completed you would receive your login details through your<br>
registered Email Address. <br>
&nbsp;</font></td>
	</tr>
	<tr>
		<td><font face="Arial" size="2"> 
		<a style="text-decoration: none; font-weight: 700" href="index.htm">
		<font color="#000000">Go to Home Page</font></a></font></td>
	</tr>
</table>
&nbsp;