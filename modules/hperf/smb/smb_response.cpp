
#include <openssl/md4.h>
#include <openssl/des.h>

#include <string>
#include <vector>
#include <iostream>

#include <sasl.h>
#include <hmac_md5.hpp>

#include "smb_mod.hpp"
#include "smb_response.hpp"


#define PORT_SMB 139

#define WIN2000_NATIVEMODE 1
#define WIN_NETBIOSMODE 2


#define PLAINTEXT 10
#define ENCRYPTED 11


#ifndef CHAR_BIT
#define CHAR_BIT 8
#endif
  
#ifndef TIME_T_MIN
#define TIME_T_MIN ((time_t)0 < (time_t) -1 ? (time_t) 0 \
        : ~ (time_t) 0 << (sizeof (time_t) * CHAR_BIT - 1))
#endif
#ifndef TIME_T_MAX
#define TIME_T_MAX (~ (time_t) 0 - TIME_T_MIN)
#endif

#define IVAL_NC(buf,pos) (*(unsigned int *)((char *)(buf) + (pos))) /* Non const version of above. */
#define SIVAL(buf,pos,val) IVAL_NC(buf,pos)=((unsigned int)(val))

#define TIME_FIXUP_CONSTANT_INT 11644473600LL

/************************/
unsigned char SMBResponse::Get7Bits(unsigned char *input, int startBit)
{
	register unsigned int word;

	word = (unsigned) input[startBit / 8] << 8;
	word |= (unsigned) input[startBit / 8 + 1];

	word >>= 15 - (startBit % 8 + 7);

	return word & 0xFE;
}


/* Make the key */
void SMBResponse::MakeKey(unsigned char *key, unsigned char *des_key)
{
	des_key[0] = Get7Bits(key, 0);
	des_key[1] = Get7Bits(key, 7);
	des_key[2] = Get7Bits(key, 14);
	des_key[3] = Get7Bits(key, 21);
	des_key[4] = Get7Bits(key, 28);
	des_key[5] = Get7Bits(key, 35);
	des_key[6] = Get7Bits(key, 42);
	des_key[7] = Get7Bits(key, 49);

	des_set_odd_parity((des_cblock *) des_key);
}

/* Do the DesEncryption */
void SMBResponse::DesEncrypt(unsigned char *clear, unsigned char *key, unsigned char *cipher)
{
	des_cblock des_key;
	des_key_schedule key_schedule;

	this->MakeKey(key, des_key);
	des_set_key(&des_key, key_schedule);
	des_ecb_encrypt((des_cblock *) clear, (des_cblock *) cipher, key_schedule, 1);
}

/*
  HashLM
  Function: Create a LM hash from the challenge
  Variables:
        lmhash    = the hash created from this function
        pass      = users password
        challenge = the challenge recieved from the server
*/
int SMBResponse::HashLM(unsigned char **lmhash, unsigned char *pass, unsigned char *_challenge) {
	
	static unsigned char magic[] = {0x4b, 0x47, 0x53, 0x21, 0x40, 0x23, 0x24, 0x25};
	unsigned char password[14 + 1];
	unsigned char lm_hash[21];
	unsigned char lm_response[24];
	int i = 0, j = 0;
	unsigned char *p = NULL;
	char HexChar;
	int HexValue;

	memset(password, 0, 14 + 1);
	memset(lm_hash, 0, 21);
	memset(lm_response, 0, 24);

	/* Use LM Hash instead of password */
	/* D42E35E1A1E4C22BD32E2170E4857C20:5E20780DD45857A68402938C7629D3B2::: */
	if (this->session.hashFlag == 1) {
		p = pass;
		while ((*p != '\0') && (i < 1)) {
			if (*p == ':')
				i++;
			p++;
		}


		if (*p == 'N') {
			// "NO PASSWORD" for LM Hash.
			// Generate 16-byte LM hash
			this->DesEncrypt(magic, &password[0], &lm_hash[0]);
			this->DesEncrypt(magic, &password[7], &lm_hash[8]);
		} else {
			// Convert ASCII PwDump LM Hash (%s).
			for (i = 0; i < 16; i++) {
				HexValue = 0x0;
				for (j = 0; j < 2; j++) {
					HexChar = (char) p[2 * i + j];

					if (HexChar > 0x39)
						HexChar = HexChar | 0x20;     /* convert upper case to lower */

					if (!(((HexChar >= 0x30) && (HexChar <= 0x39)) ||       /* 0 - 9 */
						((HexChar >= 0x61) && (HexChar <= 0x66)))) {      /* a - f */
						HexChar = 0x30;
					}

					HexChar -= 0x30;
					if (HexChar > 0x09)     /* HexChar is "a" - "f" */
						HexChar -= 0x27;

					HexValue = (HexValue << 4) | (char) HexChar;
				}
				lm_hash[i] = (unsigned char) HexValue;
			}
		}
	} else {
		/* Password == Machine Name */
		if (this->session.hashFlag == 2) {
			for (i = 0; i < 16; i++) {
				if (this->session.machine_name[i] > 0x39)
					this->session.machine_name[i] = this->session.machine_name[i] | 0x20;     /* convert upper case to lower */
				pass = this->session.machine_name;
			}
		}

		/* convert lower case characters to upper case */
		strncpy((char *)password,(char *) pass, 14);
		for (i = 0; i < 14; i++) {
			if ((password[i] >= 0x61) && (password[i] <= 0x7a))      /* a - z */
				password[i] -= 0x20;
		}

		/* Generate 16-byte LM hash */
		this->DesEncrypt(magic, &password[0], &lm_hash[0]);
		this->DesEncrypt(magic, &password[7], &lm_hash[8]);
	}

	/* 
		NULL-pad 16-byte LM hash to 21-bytes
		Split resultant value into three 7-byte thirds
		DES-encrypt challenge using each third as a key
		Concatenate three 8-byte resulting values to form 24-byte LM response
	*/
	this->DesEncrypt(this->session.challenge, &lm_hash[0], &lm_response[0]);
	this->DesEncrypt(this->session.challenge, &lm_hash[7], &lm_response[8]);
	this->DesEncrypt(this->session.challenge, &lm_hash[14], &lm_response[16]);

	memcpy(*lmhash, lm_response, 24);

	return 0;
}


/*
  HashLMv2

  This function implements the LMv2 response algorithm. The LMv2 response is used to 
  provide pass-through authentication compatibility with older servers. The response
  is based on the NTLM password hash and is exactly 24 bytes.

  The below code is based heavily on the following resources:

    http://davenport.sourceforge.net/ntlm.html#theLmv2Response
    samba-3.0.28a - libsmb/smbencrypt.c
    jcifs - packet capture of LMv2-only connection
*/
int SMBResponse::HashLMv2(unsigned char **LMv2hash, unsigned char *szLogin, unsigned char *szPassword) {
	unsigned char ntlm_hash[16];
	unsigned char lmv2_response[24];
	unsigned char unicodeUsername[20 * 2];
	unsigned char unicodeTarget[256 * 2];
	unsigned char kr_buf[16];
	int ret, i;
	unsigned char client_challenge[8] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88 };

	memset(ntlm_hash, 0, 16);
	memset(lmv2_response, 0, 24);
	memset(kr_buf, 0, 16);

	/* --- HMAC #1 Caculations --- */

	/* Calculate and set NTLM password hash */
	ret = this->MakeNTLM((unsigned char *)&ntlm_hash, (unsigned char *) szPassword);
	if (ret == -1)
		return -1;

	/*
		The Unicode uppercase username is concatenated with the Unicode authentication target
		(the domain or server name specified in the Target Name field of the Type 3 message).
		Note that this calculation always uses the Unicode representation, even if OEM encoding
		has been negotiated; also note that the username is converted to uppercase, while the
		authentication target is case-sensitive and must match the case presented in the Target
		Name field.

		The HMAC-MD5 message authentication code algorithm (described in RFC 2104) is applied to
		this value using the 16-byte NTLM hash as the key. This results in a 16-byte value - the
		NTLMv2 hash.
	*/

	/* Initialize the Unicode version of the username and target. */
	/* This implicitly supports 8-bit ISO8859/1 characters. */
	/* convert lower case characters to upper case */
	bzero(unicodeUsername, sizeof(unicodeUsername));
	for (i = 0; i < strlen((char *)szLogin); i++) {
		if ((szLogin[i] >= 0x61) && (szLogin[i] <= 0x7a))      /* a - z */
			unicodeUsername[i * 2] = (unsigned char) szLogin[i] - 0x20;
		else
			unicodeUsername[i * 2] = (unsigned char) szLogin[i];
	} 

	bzero(unicodeTarget, sizeof(unicodeTarget));
	for (i = 0; i < strlen((char *)this->session.workgroup); i++)
		unicodeTarget[i * 2] = (unsigned char)(this->session.workgroup)[i];
  
    HMACMD5 *hmac = new HMACMD5(ntlm_hash, 16);
    hmac->update((const unsigned char *)unicodeUsername, 2 * strlen((char *)szLogin));
    hmac->update((const unsigned char *)unicodeTarget, 2 * strlen((char *)this->session.workgroup));
    hmac->digest(kr_buf);
 
	/* --- HMAC #2 Calculations --- */
	/*
	   The challenge from the Type 2 message is concatenated with our fixed client nonce. The HMAC-MD5 
	   message authentication code algorithm is applied to this value using the 16-byte NTLMv2 hash 
	   (calculated above) as the key. This results in a 16-byte output value.
	*/
    hmac = new HMACMD5(kr_buf, 16);
    hmac->update((const unsigned char *) this->session.challenge, 8);
    hmac->update(client_challenge, 8);
    hmac->digest(lmv2_response);

	/* --- 24-byte LMv2 Response Complete --- */
	*LMv2hash = (unsigned char *) malloc(24);
	memset(*LMv2hash, 0, 24); 
	memcpy(*LMv2hash, lmv2_response, 16);
	memcpy(*LMv2hash + 16, client_challenge, 8);

	return 0;
}


/*
  MakeNTLM
  Function: Create a NTLM hash from the password 
*/
int SMBResponse::MakeNTLM (unsigned char *ntlmhash, unsigned char *pass) {
	MD4_CTX md4Context;
	unsigned char hash[16];       /* MD4_SIGNATURE_SIZE = 16 */
	unsigned char unicodePassword[256 * 2];       /* MAX_NT_PASSWORD = 256 */
	int i = 0, j = 0;
	int mdlen;
	unsigned char *p = NULL;
	char HexChar;
	int HexValue;

	/* Use NTLM Hash instead of password */
	if (this->session.hashFlag == 1) {
		/* 1000:D42E35E1A1E4C22BD32E2170E4857C20:5E20780DD45857A68402938C7629D3B2::: */
		p = pass;
		while ((*p != '\0') && (i < 1)) {
			if (*p == ':')
				i++;
			p++;
		}

		for (i = 0; i < 16; i++) {
			HexValue = 0x0;
			for (j = 0; j < 2; j++) {
				HexChar = (char) p[2 * i + j];

				if (HexChar > 0x39)
					HexChar = HexChar | 0x20;     /* convert upper case to lower */

				if (!(((HexChar >= 0x30) && (HexChar <= 0x39)) ||       /* 0 - 9 */
					((HexChar >= 0x61) && (HexChar <= 0x66)))) {      /* a - f */
					/*
					*  fprintf(stderr, "Error invalid char (%c) for hash.\n", HexChar);
					*  exit(0);
					*/
					HexChar = 0x30;
				}

				HexChar -= 0x30;
				if (HexChar > 0x09)     /* HexChar is "a" - "f" */
					HexChar -= 0x27;

				HexValue = (HexValue << 4) | (char) HexChar;
			}
			hash[i] = (unsigned char) HexValue;
		}
	} else {
		/* Password == Machine Name */
		if (this->session.hashFlag == 2) {
			for (i = 0; i < 16; i++) {
				if ((this->session.machine_name[i]) > 0x39)
					(this->session.machine_name)[i] = (this->session.machine_name)[i] | 0x20;     /* convert upper case to lower */
				pass = this->session.machine_name;
			}
		}

		/* Initialize the Unicode version of the secret (== password). */
		/* This implicitly supports 8-bit ISO8859/1 characters. */
		bzero(unicodePassword, sizeof(unicodePassword));
		for (i = 0; i < strlen((char *) pass); i++)
		  unicodePassword[i * 2] = (unsigned char) pass[i];

		mdlen = strlen((char *) pass) * 2;    /* length in bytes */
		MD4_Init(&md4Context);
		MD4_Update(&md4Context, unicodePassword, mdlen);
		MD4_Final(hash, &md4Context);        /* Tell MD4 we're done */
	}

	memcpy(ntlmhash, hash, 16);
	return 0;
}


/*
  HashNTLMv2

  This function implements the NTLMv2 response algorithm. Support for this algorithm
  was added with Microsoft Windows with NT 4.0 SP4. It should be noted that code doesn't
  currently work with Microsoft Vista. While NTLMv2 authentication with Samba and Windows
  2003 functions as expected, Vista systems respond with the oh-so-helpful 
  "INVALID_PARAMETER" error code. LMv2-only authentication appears to work against Vista 
  in cases where LM and NTLM are refused. 

  The below code is based heavily on the following two resources:

    http://davenport.sourceforge.net/ntlm.html#theNtlmv2Response
    samba-3.0.28 - libsmb/smbencrypt.c

  NTLMv2 network authentication is required when attempting to authenticated to
  a system which has the following policy enforced:
  
  GPO:     "Network Security: LAN Manager authentication level"
  Setting: "Send NTLMv2 response only\refuse LM & NTLM"
*/
int SMBResponse::HashNTLMv2(unsigned char **NTLMv2hash, int *iByteCount, unsigned char *szLogin, unsigned char *szPassword)
{
  unsigned char ntlm_hash[16];
  unsigned char ntlmv2_response[56 + 20 * 2 + 256 * 2];
  unsigned char unicodeUsername[20 * 2];
  unsigned char unicodeTarget[256 * 2];
  unsigned char kr_buf[16];
  int ret, i, iTargetLen;
  unsigned char client_challenge[8] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88 };

  /*
    -- Example NTLMv2 Response Data --

    [0]       HMAC: (16 bytes) 

    [16]      Header: Blob Signature [01 01 00 00] (4 bytes)
    [20]      Reserved: [00 00 00 00] (4 bytes)
    [24]      Time: Little-endian, 64-bit signed value representing the number of
                    tenths of a microsecond since January 1, 1601. (8 bytes)
    [32]      Client Nonce: (8 bytes)
    [40]      Unknown: 00 00 00 00 (4 bytes)
    [44]      Target Information (from the Type 2 message)    
              NetBIOS domain/workgroup:
                Type: domain 02 00 (2 bytes)
                Length: 12 00 (2 bytes)
                Name: WORKGROUP [NULL spacing -> 57 00 4f 00 ...] (18 bytes)  
                End-of-list: 00 00 00 00 (4 bytes)
              Termination: 00 00 00 00 (4 bytes)
  */


  iTargetLen = 2 * strlen((char *)this->session.workgroup);

  memset(ntlm_hash, 0, 16);
  memset(ntlmv2_response, 0, 56 + 20 * 2 + 256 * 2);
  memset(kr_buf, 0, 16);

  /* --- HMAC #1 Caculations --- */

  /* Calculate and set NTLM password hash */
  ret = MakeNTLM((unsigned char *)&ntlm_hash, (unsigned char *) szPassword);
  if (ret == -1)
    return -1;

  /*
    The Unicode uppercase username is concatenated with the Unicode authentication target
    (the domain or server name specified in the Target Name field of the Type 3 message).
    Note that this calculation always uses the Unicode representation, even if OEM encoding
    has been negotiated; also note that the username is converted to uppercase, while the
    authentication target is case-sensitive and must match the case presented in the Target
    Name field.

    The HMAC-MD5 message authentication code algorithm (described in RFC 2104) is applied to
    this value using the 16-byte NTLM hash as the key. This results in a 16-byte value - the
    NTLMv2 hash.
  */

  /* Initialize the Unicode version of the username and target. */
  /* This implicitly supports 8-bit ISO8859/1 characters. */
  /* convert lower case characters to upper case */
  bzero(unicodeUsername, sizeof(unicodeUsername));
  for (i = 0; i < strlen((char *)szLogin); i++)
  {
    if ((szLogin[i] >= 0x61) && (szLogin[i] <= 0x7a))      /* a - z */
      unicodeUsername[i * 2] = (unsigned char) szLogin[i] - 0x20;
    else
      unicodeUsername[i * 2] = (unsigned char) szLogin[i];
  } 

  bzero(unicodeTarget, sizeof(unicodeTarget));
  for (i = 0; i < strlen((char *)this->session.workgroup); i++)
    unicodeTarget[i * 2] = (unsigned char)(this->session.workgroup)[i];
  
  HMACMD5 *hmac = new HMACMD5(ntlm_hash, 16);
  hmac->update((const unsigned char *)unicodeUsername, 2 * strlen((char *)szLogin));
  hmac->update((const unsigned char *)unicodeTarget, 2 * strlen((char *)this->session.workgroup));
  hmac->digest(kr_buf);

  /* --- Blob Construction --- */
 
  memset(ntlmv2_response + 16, 1, 2); /* Blob Signature 0x01010000 */
  memset(ntlmv2_response + 18, 0, 2);
  memset(ntlmv2_response + 20, 0, 4); /* Reserved */
  
  /* Time -- Take a Unix time and convert to an NT TIME structure:
     Little-endian, 64-bit signed value representing the number of tenths of a 
     microsecond since January 1, 1601.
  */
  struct timespec ts;
  unsigned long long nt;

  ts.tv_sec = (time_t)time(NULL);
  ts.tv_nsec = 0;

  if (ts.tv_sec ==0)
    nt = 0;
  else if (ts.tv_sec == TIME_T_MAX)
    nt = 0x7fffffffffffffffLL;
  else if (ts.tv_sec == (time_t)-1)
    nt = (unsigned long)-1;
  else
  { 
    nt = ts.tv_sec;
    nt += TIME_FIXUP_CONSTANT_INT;
    nt *= 1000*1000*10; /* nt is now in the 100ns units */
  }

  SIVAL(ntlmv2_response + 24, 0, nt & 0xFFFFFFFF);
  SIVAL(ntlmv2_response + 24, 4, nt >> 32);
  /* End time calculation */

  /* Set client challenge - using a non-random value in this case. */
  memcpy(ntlmv2_response + 32, client_challenge, 8); /* Client Nonce */
  memset(ntlmv2_response + 40, 0, 4); /* Unknown */

  /* Target Information Block */
  /*
    0x0100 Server name
    0x0200 Domain name
    0x0300 Fully-qualified DNS host name
    0x0400 DNS domain name
  
    TODO: Need to rework negotiation code to correctly extract target information
  */

  memset(ntlmv2_response + 44, 0x02, 1); /* Type: Domain */
  memset(ntlmv2_response + 45, 0x00, 1);
  memset(ntlmv2_response + 46, iTargetLen, 1); /* Length */
  memset(ntlmv2_response + 47, 0x00, 1);
 
  /* Name of domain or workgroup */ 
  for (i = 0; i < strlen((char *)this->session.workgroup); i++)
    ntlmv2_response[48 + i * 2] = (unsigned char)(this->session.workgroup)[i];

  memset(ntlmv2_response + 48 + iTargetLen, 0, 4); /* End-of-list */

  /* --- HMAC #2 Caculations --- */

  /*
    The challenge from the Type 2 message is concatenated with the blob. The HMAC-MD5 message 
    authentication code algorithm is applied to this value using the 16-byte NTLMv2 hash 
    (calculated above) as the key. This results in a 16-byte output value.
  */
  
  hmac = new HMACMD5(kr_buf, 16);
  hmac->update(this->session.challenge, 8);
  hmac->update(ntlmv2_response + 16, 48 - 16 + iTargetLen + 4);
  hmac->digest(ntlmv2_response);

  *iByteCount = 48 + iTargetLen + 4;
  *NTLMv2hash = (unsigned char *)malloc(*iByteCount);
  memset(*NTLMv2hash, 0, *iByteCount); 
  memcpy(*NTLMv2hash, ntlmv2_response, *iByteCount);

  return 0;
}
/*
 * NTLM
 */
/*
  HashNTLM
  Function: Create a NTLM hash from the challenge
  Variables:
        ntlmhash  = the hash created from this function
        pass      = users password
        challenge = the challenge recieved from the server
*/
int SMBResponse::HashNTLM(unsigned char **ntlmhash, unsigned char *pass, unsigned char *_challenge)
{
    int ret;
    unsigned char hash[16];                       /* MD4_SIGNATURE_SIZE = 16 */
    unsigned char p21[21];
    unsigned char ntlm_response[24];

    ret = this->MakeNTLM((unsigned char *)&hash, (unsigned char *)pass);
    if (ret == -1)
        exit(0);

    memset(p21, '\0', 21);
    memcpy(p21, hash, 16);

    this->DesEncrypt(_challenge, p21 + 0, ntlm_response + 0);
    this->DesEncrypt(_challenge, p21 + 7, ntlm_response + 8);
    this->DesEncrypt(_challenge, p21 + 14, ntlm_response + 16);

    memcpy(*ntlmhash, ntlm_response, 24);

    return 0;
}


/*
  SMBSessionSetup
  Function: Send username + response to the challenge from
            the server.
  Returns: TRUE on success else FALSE.
*/
unsigned long SMBResponse::smb_session_setup(std::string szLogin, std::string szPassword) {
	unsigned char buf[512];
    
    unsigned char *LMhash = NULL;
	unsigned char *LMv2hash = NULL;
    
	unsigned char *NTLMhash = NULL;
    unsigned char *NTLMv2hash = NULL;

	char bufReceive[512];
	int nReceiveBufferSize = 0;
	int ret;
	int iByteCount, iOffset=0;
	//*************************************
	
	std::vector<unsigned char> buffer(512);
	
	if (this->session.accntFlag == 0) {
		strcpy((char *)this->session.workgroup, "localhost");
	} else
		if (this->session.accntFlag == 2) {
			memset(this->session.workgroup, 0, 16);
		} else
			if (this->session.accntFlag == 4) {
				strncpy((char *)this->session.workgroup, (char *)this->session.domain, 16);
			}

	/* NetBIOS Session Service */
	NetBIOSSession netbios_session{};
	netbios_session.Length = 0x85;
	
    /* SMB Header */
	SMBHeader smb_header = {0};
	
	*((unsigned int *)smb_header.Protocol) = 0x424d53ff;
	smb_header.Command = 0x73;   // SMB Command: Session Setup AndX
	smb_header.Flags   = 0x08;   // Flags
	smb_header.Flags2  = 0x4001; // Flags2
	smb_header.PIDHigh = 0x3713; // Process ID
	smb_header.MID     = 1;      // Multiplx ID

	memset(buf, 0, 512);
	memcpy(buf, (unsigned char *)&netbios_session, 4);
	memcpy(buf +4, (unsigned char *)&smb_header, 32);

	if (this->session.security_mode == ENCRYPTED) {
		/* Session Setup AndX Request */
		if (this->session.smb_auth_mechanism == AUTH_LM) {
			// Attempting LM password authentication.
			
			std::cout << "Usamos LMv1\n";
            
            OldSMBAuthHeader session_request;
			session_request.PasswordLength = 0x18;

			iOffset = 59; /* szNBSS + szSMB + szSessionRequest */
			iByteCount = 24; /* Start with length of LM hash */

			/* Set Session Setup AndX Request header information */
			memcpy(buf + 36, (unsigned char *)&(session_request), 23);

			/* Calculate and set LAN Manager password hash */
			LMhash = (unsigned char *) malloc(24);
			memset(LMhash, 0, 24);

			ret = HashLM(&LMhash, (unsigned char *) szPassword.c_str(), (unsigned char *)this->session.challenge);
			if (ret == -1)
				return -1;

			memcpy(buf + iOffset, LMhash, 24);
			free(LMhash);

		} else {
			
			if (this->session.smb_auth_mechanism == AUTH_NTLM) {
				// Attempting NTLM password authentication.
	
				std::cout << "Usamos NTLMv1\n";
				
                NewSMBAuthHeader session_request;
                
                session_request.CaseInsensitivePasswordLength = 0x18;
                session_request.CaseSensitivePasswordLength   = 0x18;

                iOffset = 65;    /* szNBSS + szSMB + szSessionRequest */
                iByteCount = 48; /* Start with length of NTLM and LM hashes */

                /* Set Session Setup AndX Request header information */
                memcpy(buf + 36, (unsigned char *)&(session_request), 29);

                /* Calculate and set NTLM password hash */
                NTLMhash = (unsigned char *) malloc(24);
                memset(NTLMhash, 0, 24);

                /* We don't need to actually calculated a LM hash for this mode, only NTLM */
                ret = HashNTLM(&NTLMhash, (unsigned char *) szPassword.c_str(), (unsigned char *) this->session.challenge);
                if (ret == -1)
                    return -1;

                memcpy(buf + iOffset + 24, NTLMhash, 24); /* Skip space for LM hash */
                free(NTLMhash);
			} else
				if (this->session.smb_auth_mechanism == AUTH_LMv2) {
					// Attempting LMv2 password authentication.
					
					std::cout << "Usamos LMv2\n";
					
					NewSMBAuthHeader session_request;
                    
					session_request.CaseInsensitivePasswordLength = 0x18;
					session_request.CaseSensitivePasswordLength   = 0x00;

                    iOffset = 65; /* szNBSS + szSMB + szSessionRequest */
					iByteCount = 24; /* Start with length of LMv2 response */

					/* Set Session Setup AndX Request header information */
					memcpy(buf + 36, (unsigned char *)&session_request, 29);

					/* Calculate and set LMv2 response hash */
					LMv2hash = (unsigned char *) malloc(24);
					memset(LMv2hash, 0, 24);

					ret = HashLMv2(&LMv2hash, (unsigned char *) szLogin.c_str(), (unsigned char *) szPassword.c_str());
					if (ret == -1)
						return -1;

					memcpy(buf + iOffset, LMv2hash, 24);
					free(LMv2hash);
				} else
					if (this->session.smb_auth_mechanism == AUTH_NTLMv2) {
						// Attempting LMv2/NTLMv2 password authentication.
						
						std::cout << "Usamos LMv2/NTLMv2\n";
						
                        NewSMBAuthHeader session_request;
						session_request.CaseInsensitivePasswordLength = 0x18;
						// session_request.CaseSensitivePasswordLength   = 0x4b;

                        iOffset = 65; /* szNBSS + szSMB + szSessionRequest */

						/* Set Session Setup AndX Request header information */
						memcpy(buf + 36, (unsigned char *)&(session_request), 29);

						/* Calculate and set LMv2 response hash */
						ret = HashLMv2(&LMv2hash, (unsigned char *) szLogin.c_str(), (unsigned char *) szPassword.c_str());
						if (ret == -1)
							return -1;

						memcpy(buf + iOffset, LMv2hash, 24);
						free(LMv2hash);

						/* Calculate and set NTLMv2 response hash */
						ret = HashNTLMv2(&NTLMv2hash, &iByteCount, (unsigned char *) szLogin.c_str(), (unsigned char *) szPassword.c_str());
						if (ret == -1)
                            return -1;

						/* Set NTLMv2 Response Length */
						// memset(buf + iOffset - 12, iByteCount, 1);
                        
                        session_request.CaseSensitivePasswordLength = iByteCount;

						memcpy(buf + iOffset + 24, NTLMv2hash, iByteCount);
						free(NTLMv2hash);

						iByteCount += 24; /* Reflects length of both LMv2 and NTLMv2 responses */
					}
					
			
		}
	} else
		if (this->session.security_mode == PLAINTEXT) {
			// Attempting PLAINTEXT password authentication.
			
			std::cout << "Usamos Plaintext\n";
			
            OldSMBAuthHeader session_request;
			session_request.PasswordLength = 0x00;

			iOffset = 59; /* szNBSS + szSMB + szSessionRequest */

			/* Set Session Setup AndX Request header information */
			memcpy(buf + 36, (unsigned char *)&(session_request), 23);

			/* Calculate and set password length */
			/* Samba appears to append NULL characters equal to the password length plus 2 */
			// iByteCount = 2 * strlen(szPassword) + 2;
			iByteCount = strlen(szPassword.c_str()) + 1;
			buf[iOffset - 8] = (iByteCount) % 256;
			buf[iOffset - 7] = (iByteCount) / 256;

			/* set ANSI password */

			strncpy((char *)(buf + iOffset), szPassword.c_str(), 256);
		} else
			// Security_mode was not properly set. This should not happen.
			return -1;

	/* Set account and workgroup values */ 
	memcpy(buf + iOffset + iByteCount, szLogin.c_str(), strlen(szLogin.c_str()));
	iByteCount += strlen(szLogin.c_str()) + 1; /* NULL pad account name */
    
	memcpy(buf + iOffset + iByteCount, this->session.workgroup, strlen((char *) this->session.workgroup));
	iByteCount += strlen((char *) this->session.workgroup) + 1; // NULL pad workgroup name

	/* Set native OS and LAN Manager values */

	sprintf((char *)(buf + iOffset + iByteCount), "Unix"); 
	iByteCount += strlen("Unix") + 1; // NULL pad OS name
	sprintf((char *)(buf + iOffset + iByteCount), "Samba"); 
	iByteCount += strlen("Samba") + 1; // NULL pad LAN Manager name

	/* Set the header length */
	buf[2] = (iOffset - 4 + iByteCount) / 256;
	buf[3] = (iOffset - 4 + iByteCount) % 256;

	/* Set data byte count */
	buf[iOffset - 2] = iByteCount;

	send(this->session._sock, (char *) buf, iOffset + iByteCount, 0);

	nReceiveBufferSize = 0;
	nReceiveBufferSize = recv(this->session._sock, bufReceive, sizeof(bufReceive), 0);
	if ((bufReceive == NULL) || (nReceiveBufferSize == 0))
		return -1;

	/* 41 - Action (Guest/Non-Guest Account) */
	/*  9 - NT Status (Error code) */
	return (((bufReceive[41] & 0x01) << 24) | ((bufReceive[11] & 0xFF) << 16) | ((bufReceive[10] & 0xFF) << 8) | (bufReceive[9] & 0xFF));
}
