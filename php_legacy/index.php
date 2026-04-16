<?php

require "vendor/autoload.php";

$modem_ip = '192.168.0.1';
$passwd = 'admin';

if ( (strlen($modem_ip)<1) && (strlen($passwd)<1) ) {
  echo "Please set your modem_ip (Ex: 192.168.0.1) and set your password\n";
  exit;
}

if (!array_key_exists(1, $argv)) {
  echo "How to use:\n";
  echo "arg1 |  arg2  |   arg3  |\n";
  echo "-----|--------|---------|\n";
  echo "login| on/off |         | => Login or Logoff\n";
  echo "-----|--------|---------|\n";
  echo "ls   |        |         | => List all Messages\n";
  echo "-----|--------|---------|\n";
  echo "rm   | #      |         | => Delete the # Message\n";
  echo "-----|--------|---------|\n";
  echo "rm   | *      |         | => Delete all Messages\n";
  echo "-----|--------|---------|\n";
  echo "snd  | Phone# | Message | => Send The 'Message' to Phone#\n";
  echo "-----|--------|---------|\n";
  echo "wifi | on/off |         | => Enable or Disable Wifi\n";
  echo "-----|--------|---------|\n";
  echo "wan  | on/off |         | => Enable or Disable WAN\n";
  echo "-----|--------|---------|\n";
  echo "hack |        |         | => Hack Modem (Method 2, built-in telnetd)\n";
  echo "-----|--------|---------|\n";
  echo "hack3| TftpIP |         | => Hack Modem (Method 3, zte_debug.sh, default IP: 192.168.0.22)\n";
  echo "-----|--------|---------|\n";
  echo "hack3d|TftpIP |         | => Hack Modem (Method 3 direct tftp cmd, default IP: 192.168.0.22)\n";
  echo "-----|--------|---------|\n";
  exit;
}

if ( ($argv[1]!='login') && ($argv[1]!='ls') && ($argv[1]!='rm') && ($argv[1]!='snd')
  && ($argv[1]!='wifi') && ($argv[1]!='wan') && ($argv[1]!='hack') && ($argv[1]!='hack3')
  && ($argv[1]!='hack3d') ) {
    echo "How to use:\n";
    echo "arg1 |  arg2  |   arg3  |\n";
    echo "-----|--------|---------|\n";
    echo "login| on/off |         | => Login or Logoff\n";
    echo "-----|--------|---------|\n";
    echo "ls   |        |         | => List all Messages\n";
    echo "-----|--------|---------|\n";
    echo "rm   | #      |         | => Delete the # Message\n";
    echo "-----|--------|---------|\n";
    echo "rm   | *      |         | => Delete all Messages\n";
    echo "-----|--------|---------|\n";
    echo "snd  | Phone# | Message | => Send The 'Message' to Phone#\n";
    echo "-----|--------|---------|\n";
    echo "wifi | on/off |         | => Enable or Disable Wifi\n";
    echo "-----|--------|---------|\n";
    echo "wan  | on/off |         | => Enable or Disable WAN\n";
    echo "-----|--------|---------|\n";
    echo "hack |        |         | => Hack Modem (Method 2, built-in telnetd)\n";
    echo "-----|--------|---------|\n";
    echo "hack3| TftpIP |         | => Hack Modem (Method 3, zte_debug.sh, default IP: 192.168.0.22)\n";
    echo "-----|--------|---------|\n";
    echo "hack3d|TftpIP |         | => Hack Modem (Method 3 direct tftp cmd, default IP: 192.168.0.22)\n";
    echo "-----|--------|---------|\n";
    exit;
  }

use ZTE\Login;

if ($argv[1] == 'login') {

  if(!array_key_exists(2,$argv)) {
    echo "on or off\n";
    exit;
  }

  if ( ($argv[2]!="on") &&  ($argv[2]!="off") ) {
    echo "on or off\n";
    exit;
  }

  if ($argv[2]=="on") {
    // First do Login
    $login = new Login($modem_ip, 'IN', $passwd);
    $ret = $login->login_logout();

    var_dump ($ret);

    $login = new Login($modem_ip, 'OUT', $passwd);
    $login->login_logout();
  }

  if ($argv[2]=="off") {
    $login = new Login($modem_ip, 'OUT', $passwd);
    $ret = $login->login_logout();
    var_dump ($ret);
  }
}

use ZTE\Sms;

$sms = new Sms($modem_ip);

// Get Message List
if ($argv[1] == 'ls') {

  // First do Login
  $login = new Login($modem_ip, 'IN', $passwd);
  $login->login_logout();

  $messages = $sms->read_sms();

  var_dump($messages);

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

// Delete Message
if ( ($argv[1] == 'rm')) {

  if(!array_key_exists(2,$argv)) {
    echo 'No message # or "*" for all'."\n";
    exit;
  }

  $id = $sms->setId($argv[2]);
  $ret = $sms->delete_message();

  if (!is_array($ret)) {
    var_dump($ret);

    // Do Logout
    $login = new Login($modem_ip, 'OUT', $passwd);
    $login->login_logout();

    exit;
  }

  if (array_key_exists('txt', $ret)) {
    echo $ret['txt']."\n";
  } else {
    var_dump($ret);
  }

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

// Send Message
if ($argv[1] =='snd') {

  if(!array_key_exists(2,$argv)) {
    echo "No Phone #\n";
    exit;
  }

  if(!array_key_exists(3,$argv)) {
    echo "No Text\n";
    exit;
  }

  // First do Login
  $login = new Login($modem_ip, 'IN', $passwd);
  $login->login_logout();

  $phone = $sms->setPhone($argv[2]);
  $message = $sms->setMessage($argv[3]);
  $ret = $sms->send_sms();

  if (!is_array($ret)) {
    var_dump($ret);

    // Do Logout
    $login = new Login($modem_ip, 'OUT', $passwd);
    $login->login_logout();

    exit;
  }

  if (array_key_exists('txt', $ret)) {
    echo $ret['txt']."\n";
  } else {
    var_dump($ret);
  }

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

use ZTE\Wifi;
// Enable or Disable Wifi
if ( ($argv[1] == 'wifi')) {

  if(!array_key_exists(2,$argv)) {
    echo "on or off\n";
    exit;
  }

  if ( ($argv[2]!="on") &&  ($argv[2]!="off") ) {
    echo "on or off\n";
    exit;
  }

  // First do Login
  $login = new Login($modem_ip, 'IN', $passwd);
  $login->login_logout();

  if ($argv[2]=="on") {
    $wifi = new Wifi($modem_ip,'ENA');
    $ret = $wifi->disable_enable();
  }

  if ($argv[2]=="off") {
    $wifi = new Wifi($modem_ip,'DIS');
    $ret = $wifi->disable_enable();
  }

  var_dump($ret);

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

use ZTE\Wan;
// Connect or Disconnect WAN
if ($argv[1] == 'wan') {

  if(!array_key_exists(2,$argv)) {
    echo "on or off\n";
    exit;
  }

  if ( ($argv[2]!="on") &&  ($argv[2]!="off") ) {
    echo "on or off\n";
    exit;
  }

  // First do Login
  $login = new Login($modem_ip, 'IN', $passwd);
  $login->login_logout();

  if ($argv[2]=="on") {
    $wan = new Wan($modem_ip,'CON');
    $ret = $wan->connect_disconnect();
  }

  if ($argv[2]=="off") {
    $wan = new Wan($modem_ip,'DIS');
    $ret = $wan->connect_disconnect();
  }

  var_dump($ret);

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

use ZTE\Hack;
// Hack Modem - Method 2 (requires built-in telnetd in busybox)
if ( ($argv[1] == 'hack')) {

  // Login first
  $login = new Login($modem_ip, 'IN', $passwd);
  $ret = $login->login_logout();
  var_dump($ret);

  $hack = new Hack($modem_ip, $passwd);
  $back = $hack->factory_backdoor();
  var_dump($back);
  $nvram = $hack->exploits_nvram();
  var_dump($nvram);

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

// Hack Modem - Method 3 (TFTP, for firmware without built-in telnetd)
// Prerequisites: TFTP server running at TftpIP with a MIPS busybox binary
// named "telnetd" in its root. Telnetd will listen on port 23 (admin/admin).
if ( ($argv[1] == 'hack3')) {

  $tftp_ip = array_key_exists(2, $argv) ? $argv[2] : '192.168.0.22';

  // Login first
  $login = new Login($modem_ip, 'IN', $passwd);
  $ret = $login->login_logout();
  var_dump($ret);

  $hack = new Hack($modem_ip, $passwd);
  $back = $hack->factory_backdoor();
  var_dump($back);
  $tftp = $hack->tftp_telnetd($tftp_ip);
  var_dump($tftp);

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}

// Hack Modem - Method 3 direct (fallback if zte_debug.sh is not present)
// Uses raw busybox tftp command to fetch and execute telnetd.
if ( ($argv[1] == 'hack3d')) {

  $tftp_ip = array_key_exists(2, $argv) ? $argv[2] : '192.168.0.22';

  // Login first
  $login = new Login($modem_ip, 'IN', $passwd);
  $ret = $login->login_logout();
  var_dump($ret);

  $hack = new Hack($modem_ip, $passwd);
  $back = $hack->factory_backdoor();
  var_dump($back);
  $tftp = $hack->tftp_telnetd_direct($tftp_ip);
  var_dump($tftp);

  // Do Logout
  $login = new Login($modem_ip, 'OUT', $passwd);
  $login->login_logout();
}
