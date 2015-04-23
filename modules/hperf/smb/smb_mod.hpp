
#include <string>
#include <stdint.h>

#ifndef SMB_MOD_H
#define SMB_MOD_H

#define ENCRYPTED 11
#define AUTH_NTLM 9

/*
 * http://tools.ietf.org/html/rfc1002  (Page 29 and 30 in particular)
 * http://msdn.microsoft.com/en-us/library/ee441774.aspx
 * http://www.ubiqx.org/cifs/rfc-draft/draft-leach-cifs-v1-spec-02.txt
 */

typedef struct __attribute__ ((__packed__)) {
	uint8_t  Type;
	uint8_t  Flags;
	uint16_t Length;
} NetBIOSSession;

typedef struct __attribute__ ((__packed__)) {
	uint8_t  Protocol[4];
	uint8_t  Command;
	uint32_t Status;
	uint8_t  Flags;
	uint16_t Flags2;
	uint16_t PIDHigh;
	uint8_t  SecurityFeatures[8];
	uint16_t Reserved;
	uint16_t TID;
	uint16_t PIDLow;
	uint16_t UID;
	uint16_t MID;
} SMBHeader;

/*
 * If the negotiated protocol is prior to NT LM 0.12, the format of
 * SMB_COM_SESSION_SETUP_ANDX is
 * 
 * uint8_t WordCount;               Count of parameter words = 10
 * uint8_t AndXCommand;             Secondary (X) command; 0xFF = none
 * uint8_t AndXReserved;            Reserved (must be 0)
 * uint16_t AndXOffset;             Offset to next command WordCount
 * uint16_t MaxBufferSize;          Client maximum buffer size
 * uint16_t MaxMpxCount;            Actual maximum multiplexed pending requests
 * uint16_t VcNumber;               0 = first (only), nonzero=additional VC number
 * uint32_t SessionKey;              Session key (valid iff VcNumber != 0)
 * uint16_t PasswordLength;         Account password size
 * uint32_t Reserved;                Must be 0
 * uint16_t ByteCount;              Count of data bytes;    min = 0
 * uint8_t AccountPassword[];       Account Password
 * STRING AccountName[];          Account Name
 * STRING PrimaryDomain[];        Client's primary domain
 * STRING NativeOS[];             Client's native operating system
 * STRING NativeLanMan[];         Client's native LAN Manager type
 */
struct OldSMBAuthHeader {
	uint8_t  WordCount;
	uint8_t  AndXCommand;
	uint8_t  AndXReserved;
	uint16_t AndXOffset;
	uint16_t MaxBufferSize;
	uint16_t MaxMpxCount;
	uint16_t VcNumber;
	uint32_t SessionKey;
	uint16_t PasswordLength;
	uint32_t Reserved;
	uint16_t ByteCount;
    
    OldSMBAuthHeader() {
        WordCount      = 0x01;
        AndXCommand    = 0xff;
        AndXReserved   = 0x00;
        AndXOffset     = 0x0000;
        MaxBufferSize  = 0xffff;
        MaxMpxCount    = 0x0002;
        VcNumber       = 0x7d3c;
        SessionKey     = 0x00000000;
        PasswordLength = 0x0018;
        Reserved       = 0x00000000;
        ByteCount      = 0x0049;
    }
    
} __attribute__((__packed__));

/*
 * If the negotiated SMB dialect is "NT LM 0.12" or later, the format of
 * the response SMB is unchanged, but the request is
 * 
 * uint8_t WordCount;                       Count of parameter words = 13
 * uint8_t AndXCommand;                     Secondary (X) command;  0xFF = none
 * uint8_t AndXReserved;                    Reserved (must be 0)
 * uint16_t AndXOffset;                     Offset to next command WordCount
 * uint16_t MaxBufferSize;                  Client's maximum buffer size
 * uint16_t MaxMpxCount;                    Actual maximum multiplexed pending requests
 * uint16_t VcNumber;                       0 = first (only), nonzero=additional VC number
 * uint32_t SessionKey;                      Session key (valid iff VcNumber != 0)
 * uint16_t CaseInsensitivePasswordLength;  Account password size, ANSI
 * uint16_t CaseSensitivePasswordLength;    Account password size, Unicode
 * uint32_t Reserved;                        must be 0
 * uint32_t Capabilities;                    Client capabilities
 * uint16_t ByteCount;                      Count of data bytes; min = 0
 * uint8_t CaseInsensitivePassword[];       Account Password, ANSI
 * uint8_t CaseSensitivePassword[];         Account Password, Unicode
 * STRING AccountName[];                  Account Name, Unicode
 * STRING PrimaryDomain[];                Client's primary domain, Unicode
 * STRING NativeOS[];                     Client's native operating system, Unicode
 * STRING NativeLanMan[];                 Client's native LAN Manager type, Unicode
 */
struct NewSMBAuthHeader {
	uint8_t  WordCount;
    uint8_t  AndXCommand;
	uint8_t  AndXReserved;
	uint16_t AndXOffset;
	uint16_t MaxBufferSize;
	uint16_t MaxMpxCount;
	uint16_t VcNumber;
	uint32_t SessionKey;
	uint16_t CaseInsensitivePasswordLength;
	uint16_t CaseSensitivePasswordLength;
	uint32_t Reserved;
	uint32_t Capabilities;
	uint16_t ByteCount;
    
    NewSMBAuthHeader() {
        WordCount     = 0x0d;
        AndXCommand   = 0xff;
        AndXReserved  = 0x00;
        AndXOffset    = 0x0000;
        MaxBufferSize = 0xffff;
        MaxMpxCount   = 0x0002;
        VcNumber      = 0x7d3c;
        SessionKey    = 0x00000000;
        CaseInsensitivePasswordLength = 0x0018;
        CaseSensitivePasswordLength   = 0x0000;
        Reserved      = 0x00000000;
        Capabilities  = 0x00000050;
        ByteCount     = 0x0049;
    }
    
} __attribute__((__packed__));

/*
 * And the response is:
 *
 * uint8_t WordCount;                   Count of parameter words = 3
 * uint8_t AndXCommand;                 Secondary (X) command;  0xFF = none
 * uint8_t AndXReserved;                Reserved (must be 0)
 * uint16_t AndXOffset;                 Offset to next command WordCount
 * uint16_t Action;                     Request mode: bit0 = logged in as GUEST
 * uint16_t ByteCount;                  Count of data bytes
 * STRING NativeOS[];                 Server's native operating system
 * STRING NativeLanMan[];             Server's native LAN Manager type
 * STRING PrimaryDomain[];            Server's primary domain
 */
typedef struct __attribute__ ((__packed__)) {
	uint8_t WordCount;
	uint8_t AndXCommand;
	uint8_t AndXReserved;
	uint16_t AndXOffset;
	uint16_t Action;
	uint16_t ByteCount;
} SMBResponseHeader;

struct SMBSession {
    unsigned char domain[16];
	unsigned char challenge[8];
	unsigned char workgroup[16];
	unsigned char machine_name[16];
	int hashFlag, accntFlag, protoFlag;

	int smb_auth_mechanism=AUTH_NTLM;
	int security_mode=ENCRYPTED;
	
	int _sock;
	std::string _hostname;
	unsigned short _port;
	unsigned int _timeout;
};

class SMB {
private:

	SMBSession session;

public:
	static const int SMB_CONNECTION_ERROR = 1;
	static const int SMB_TIMEOUT_ERROR    = 2;
	static const int SMB_PROTOCOL_ERROR   = 5;
	
	static const int SMB_LOGIN_SUCCESSFUL = 0;
	static const int SMB_LOGIN_FAILED     = 3;
	
	static const int SMB_INVALID_USERNAME = 4;

	SMB(std::string hostname, unsigned short port, unsigned int timeout);
	
	int try_login(std::string username, std::string password);
	
	/*
	 * 
	 */	
	int _socket_connect();

	//unsigned char Get7Bits(unsigned char *input, int startBit);

	void MakeKey(unsigned char *key, unsigned char *des_key);

	void DesEncrypt(unsigned char *clear, unsigned char *key, unsigned char *cipher);

	int HashLM(unsigned char **lmhash, unsigned char *pass, unsigned char *challenge);

	int MakeNTLM (unsigned char *ntlmhash, unsigned char *pass);

	int HashLMv2(unsigned char **LMv2hash, unsigned char *szLogin, unsigned char *szPassword);

	int HashNTLMv2(unsigned char **NTLMv2hash, int *iByteCount, unsigned char *szLogin, unsigned char *szPassword);
	
	int HashNTLM(unsigned char **ntlmhash, unsigned char *pass, unsigned char *challenge);



	int smb_start_session();

	int smb_negotiation();

	unsigned long smb_session_setup(std::string szLogin, std::string szPassword);

};

#endif
