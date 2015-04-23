#include <openssl/md4.h>
#include <openssl/des.h>

#include <string>
#include <vector>
#include <iostream>

#include <sasl.h>
#include <hmac_md5.hpp>

#include "smb_mod.hpp"

#include "smb_response.hpp"

/*
 * 
 */
const int SMB::SMB_CONNECTION_ERROR;
const int SMB::SMB_TIMEOUT_ERROR;
const int SMB::SMB_PROTOCOL_ERROR;

const int SMB::SMB_LOGIN_SUCCESSFUL;
const int SMB::SMB_LOGIN_FAILED;

const int SMB::SMB_INVALID_USERNAME;

/*

http://technet.microsoft.com/en-us/library/cc960646.aspx

   Most of the new code comes from Medusa smbnt module

   Based on code from: SMB Auditing Tool
   [Copyright (C) Patrik Karlsson 2001]
   This code allows Hydra to directly test NTLM hashes against
   a Windows. This may be useful for an auditor who has aquired 
   a sam._ or pwdump file and would like to quickly determine 
   which are valid entries. This module can also be used to test 
   SMB passwords against devices that do not allow clear text 
   LanMan passwords.

   The "-m 'METHOD'" option is required for this module. The
   following are valid methods: Local, Domain, Hash, Machine,
   NTLMV2, NTLM, LMV2, LM (in quotes).

     Local == Check local account.
     Domain == Check credentials against this hosts primary
          domain controller via this host.
     Hash == Use a NTLM hash rather than a password. 
     Machine == Use the Machine's NetBIOS name as the password. 
     NTLMV2, NTLM, LMV2, LM == set the dialect

   Be careful of mass domain account lockout with this. For
   example, assume you are checking several accounts against 
   many domain workstations. If you are not using the 'L'
   options and these accounts do not exist locally on the 
   workstations, each workstation will in turn check their
   respective domain controller. This could cause a bunch of 
   lockouts. Of course, it'd look like the workstations, not 
   you, were doing it. ;)

   **FYI, this code is unable to test accounts on default XP
   hosts which are not part of a domain and do not have normal
   file sharing enabled. Default XP does not allow shares and
   returns STATUS_LOGON_FAILED for both valid and invalid 
   credentials. XP with simple sharing enabled returns SUCCESS
   for both valid and invalid credentials. If anyone knows a
   way to test in these configurations...

*/

#define PORT_SMB 139

#define WIN2000_NATIVEMODE 1
#define WIN_NETBIOSMODE 2


#define PLAINTEXT 10
#define ENCRYPTED 11


#ifndef CHAR_BIT
#define CHAR_BIT 8
#endif

/************************/

int SMB::_socket_connect() {
	int fd;
	
	struct hostent *server;
	struct sockaddr_in cli_addr;
	
	fd = socket(AF_INET, SOCK_STREAM, 0);
	
	bzero((char *) &cli_addr, sizeof(cli_addr));
	
	cli_addr.sin_family = AF_INET;
    
    cli_addr.sin_addr.s_addr = inet_addr(this->session._hostname.c_str());
    
	cli_addr.sin_port = htons(this->session._port);
	
	connect(fd,(struct sockaddr *)&cli_addr,sizeof(cli_addr));
	
	return fd;
}

/*
   NBS Session Request
   Function: Request a new session from the server
   Returns: TRUE on success else FALSE.
*/
int SMB::smb_start_session() {
    
    NetBIOSSession nb_header;

    
    
	char nb_name[32];             /* netbiosname */
	char nb_local[32];            /* netbios localredirector */
	unsigned char rqbuf[7] = { 0x81, 0x00, 0x00, 0x44, 0x20, 0x00, 0x20 };
	char *buf;
	unsigned char rbuf[400];

	/* if we are running in native mode (aka port 445) don't do netbios */
	if (this->session.protoFlag == WIN2000_NATIVEMODE) {
		return 0;
	}

	/* convert computer name to netbios name */
	memset(nb_name, 0, 32);
	memset(nb_local, 0, 32);
	memcpy(nb_name,  "CKFDENECFDEFFCFGEFFCCACACACACACA", 32);  /* SMBSERVER */
	memcpy(nb_local, "FDFHEBFCENEJEOEHCACACACACACACACA", 32);  /* SWARMING  */

	buf = (char *) malloc(100);
	memset(buf, 0, 100);
	memcpy(buf, (char *) rqbuf, 5);
	memcpy(buf + 5, nb_name, 32);
	memcpy(buf + 37, (char *) rqbuf + 5, 2);
	memcpy(buf + 39, nb_local, 32);
	memcpy(buf + 71, (char *) rqbuf + 5, 1);

	send(this->session._sock, buf, 72, 0);
	free(buf);

	memset(rbuf, 0, 400);
	recv(this->session._sock, (char *) rbuf, sizeof(rbuf), 0);
  

	if ((rbuf != NULL) && (rbuf[0] == 0x82))
		return true;                   /* success */
	return false;                  /* failed */
}

/*
   SMBNegProt
   Function: Negotiate protocol with server ...
       Actually a pseudo negotiation since the whole
       program counts on NTLM support :)

    The challenge is retrieved from the answer
    No error checking is performed i.e cross your fingers....
*/
int SMB::smb_negotiation()
{
	unsigned char buf[] = {
		0x00, // Session message
		0x00, 0x00, 0xbe, // Lenght
		//0x00, 0x00, 0x91, // Lenght
		0xff, 0x53, 0x4d, 0x42, // \xffSMB
		0x72, // SMB Command: Negotiate protocol
		0x00, 0x00, 0x00, 0x00, // NT Status: SUCCESS
		0x08, // Flags
		0x01, 0x40, // Flags2
		0x00, 0x00, // Proccess ID High
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00,	0x00, 0x00, // Signature
		0x00, 0x00, // Reserved
		0x00, 0x00, // Tree ID
		0x3c, 0x7d, // Process ID
		0x00, 0x00, // User ID
		0x01, 0x00, //Multiplex ID
		0x00, // Word Count
		0x9b, 0x00, // Byte Count
		//0x6e, 0x00, // Byte Count
		
		// PC NETWORK PROGRAM 1.0 (dialect 0x2)
		0x02, 0x50, 0x43, 0x20, 0x4e, 0x45, 0x54, 0x57, 0x4f, 0x52, 0x4b, 0x20, 0x50, 0x52, 0x4f, 0x47, 0x52, 0x41, 0x4d, 0x20, 0x31, 0x2e, 0x30, 0x00,
		
		// MICROSOFT NETWORK 1.03
		0x02, 0x4d, 0x49, 0x43, 0x52, 0x4f, 0x53, 0x4f, 0x46, 0x54, 0x20, 0x4e, 0x45, 0x54, 0x57, 0x4f, 0x52, 0x4b, 0x53, 0x20, 0x31, 0x2e, 0x30, 0x33, 0x00,
		
		// MICROSOFT NETWORK 3.0
		0x02, 0x4d, 0x49, 0x43, 0x52, 0x4f, 0x53, 0x4f,	0x46, 0x54, 0x20, 0x4e, 0x45, 0x54, 0x57, 0x4f,	0x52, 0x4b, 0x53, 0x20, 0x33, 0x2e, 0x30, 0x00,
		
		// LANMAN1.0
		0x02, 0x4c, 0x41, 0x4e, 0x4d, 0x41, 0x4e, 0x31, 0x2e, 0x30, 0x00,
		
		// LM1.2X002
		0x02, 0x4c, 0x4d, 0x31, 0x2e, 0x32, 0x58, 0x30, 0x30, 0x32, 0x00,
		
		// DOS LANMAN2.1
		0x02, 0x44,	0x4f, 0x53, 0x20, 0x4c, 0x41, 0x4e, 0x4d, 0x41,	0x4e, 0x32, 0x2e, 0x31, 0x00,
		
		// LANMAN2.1
		0x02, 0x4c, 0x41, 0x4e, 0x4d, 0x41, 0x4e, 0x32, 0x2e, 0x31, 0x00,
		
		// Samba
		0x02, 0x53, 0x61, 0x6d, 0x62, 0x61, 0x00,
		
		// NT LM 0.12
		0x02, 0x4e,	0x54, 0x20, 0x4c, 0x4d, 0x20, 0x30, 0x2e, 0x31,	0x32, 0x00,
        
        // NT LANMAN 1.0
		0x02, 0x4e, 0x54, 0x20, 0x4c, 0x41, 0x4e, 0x4d, 0x41, 0x4e, 0x20, 0x31, 0x2e, 0x30, 0x00
	};

	unsigned char rbuf[400];
	unsigned char sess_key[2];
	unsigned char userid[2] = {0xCD, 0xEF};
	int i = 0, j = 0;
	int iLength = sizeof(buf);
	int iResponseOffset = 73;

	memset((char *) rbuf, 0, 400);

	/* set session key */
	sess_key[1] = getpid() / 100;
	sess_key[0] = getpid() - (100 * sess_key[1]);
	memcpy(buf + 30, sess_key, 2);
	memcpy(buf + 32, userid, 2);

	if (this->session.smb_auth_mechanism == AUTH_LM)
	{
		// Setting Negotiate Protocol Response for LM.
		buf[3] = 0xA3;    // Set message length
		buf[37] = 0x80;   // Set byte count for dialects
		iLength = 167;
		iResponseOffset = 65;
	}

  
	send(this->session._sock, (char *) buf, iLength, 0);
	
	recv(this->session._sock, (char *) rbuf, sizeof(rbuf), 0);
	if (rbuf == NULL)
		return 3;

	/* retrieve the security mode */
	/*
		[0] Mode:       (0) ?                                 (1) USER security mode 
		[1] Password:   (0) PLAINTEXT password                (1) ENCRYPTED password. Use challenge/response
		[2] Signatures: (0) Security signatures NOT enabled   (1) ENABLED
		[3] Sig Req:    (0) Security signatures NOT required  (1) REQUIRED

		SAMBA: 0x01 (default)
		WinXP: 0x0F (default)
		WinXP: 0x07 (Windows 2003 / DC)
	*/
	switch (rbuf[39]) {
		case 0x01:
		  //real plaintext should be used with LM auth
		  this->session.security_mode = PLAINTEXT;
		  
		  if((this->session.hashFlag == 1) || (this->session.hashFlag == 2))
		  {
			// Server requested PLAINTEXT password. HASH password mode not supported for this configuration.
			return SMB_PROTOCOL_ERROR;
		  }
		  break;
		case 0x03: // Server requested ENCRYPTED password without security signatures.
			this->session.security_mode = ENCRYPTED;
			break;
		  
		case 0x07:
		case 0x0F: // Server requested ENCRYPTED password
            this->session.security_mode = ENCRYPTED;
			break;
		default: // Unknown security mode
			this->session.security_mode = ENCRYPTED;
			break;
	}

	/* Retrieve the challenge */
	memcpy(this->session.challenge, (char *) rbuf + iResponseOffset, sizeof(this->session.challenge));

	/* Find the primary domain/workgroup name */
	memset(this->session.workgroup, 0, 16);
	memset(this->session.machine_name, 0, 16);

	//seems using LM only the domain is returned not the server
	//and the domain is not padded with null chars
	if (this->session.smb_auth_mechanism == AUTH_LM) {
		while ((rbuf[iResponseOffset + 8 + i] != 0) && (i < 16)) {
			(this->session.workgroup)[i] = rbuf[iResponseOffset + 8 + i];
			i++;
		}
		
	} else {
		while ((rbuf[iResponseOffset + 8 + i * 2] != 0) && (i < 16)) {
			(this->session.workgroup)[i] = rbuf[iResponseOffset + 8 + i * 2];
			i++;
		}

		while ((rbuf[iResponseOffset + 8 + (i + j + 1) * 2] != 0) && (j < 16)) {
		  (this->session.machine_name)[j] = rbuf[iResponseOffset + 8 + (i + j + 1) * 2];
		  j++;
		}
	}

	//success
	return 2;
}

/*
 *
 */
int SMB::try_login(std::string username, std::string password) {
    
	int SMBerr, SMBaction;
	unsigned long SMBSessionRet;
	char ipaddr_str[64];
	char ErrorCode[10];
	
	int status = -1;

	memset(ErrorCode, 0, 10);
	
	int run = 1, next_run = 1;

	// LOCAL=0, DOMAIN=1, BOTH=2, OTHER_DOMAIN=4
	this->session.accntFlag = 2; //BOTH

	// PASS=0, HASH=1, MACHINE=2
	this->session.hashFlag = 0;
	
	this->session.smb_auth_mechanism=AUTH_NTLM;

    this->session._sock = this->_socket_connect();
    if (this->session._port == PORT_SMB)
        this->session.protoFlag = WIN_NETBIOSMODE; // Attempting NETBIOS mode.
    else
        this->session.protoFlag = WIN2000_NATIVEMODE; // Attempting WIN2K Native mode

	if (this->smb_start_session() < 0) {
		return -1;
	}
	
	next_run = this->smb_negotiation();

	// SMBSessionRet = this->SMBSessionSetup(username, password);
    
    SMBResponse response(this->session);
    
    SMBSessionRet = response.smb_session_setup(username, password);
    
	if (SMBSessionRet == -1) 
		return 3;
	SMBerr = (unsigned long) SMBSessionRet & 0x00FFFFFF;
	SMBaction = ((unsigned long) SMBSessionRet & 0xFF000000) >> 24;

	printf("SMBSessionRet: %8.8X SMBerr: %4.4X SMBaction: %2.2X\n", (unsigned int)SMBSessionRet, SMBerr, SMBaction);

	switch(SMBerr) {
		case 0x000000: /* success */
			if (SMBaction == 0x01) /* invalid account - anonymous connection */
			  status = SMB_LOGIN_FAILED;
			else /* valid account */
			  status = SMB_LOGIN_SUCCESSFUL;
			break;
		
		case 0x000024:	/* change password on next login [success] */
		case 0x00006E:  /* Valid password, GPO Disabling Remote Connections Using NULL Passwords */
		case 0x00015B:  /* Valid password, GPO "Deny access to this computer from the network" */
		case 0x000193:  /* Valid password, account expired  */
		case 0x000224:  /* Valid password, account expired  */
		case 0x050001:  /* AS/400 -- Incorrect password */
			status = SMB_LOGIN_SUCCESSFUL;
			break;
		
		case 0x00006D:  /* STATUS_LOGON_FAILURE */
		case 0x000072:  /* account disabled */ /* BF0002 on w2k*/
		case 0xBF0002:
		case 0x000034:  /* account locked out */
		case 0x000234:
		case 0x00008D:  /* ummm... broken client-domain membership  */
			status = SMB_LOGIN_FAILED;
			break;
	}
	
	if (this->session._sock >= 0)
		this->session._sock = close(this->session._sock);

	return status;
}

/*
 *
 */
SMB::SMB(std::string hostname, unsigned short port, unsigned int timeout) {
	
	this->session._hostname = hostname;
	this->session._port = port;
	this->session._timeout = timeout;
}







