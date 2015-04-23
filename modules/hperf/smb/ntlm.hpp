
/* 
 * These structures are byte-order dependant, and should not
 * be manipulated except by the use of the routines provided
 */
 
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned char uint8;
 
#include <stdint.h>

typedef struct {
	uint16_t len;
	uint16_t maxlen;
	uint32_t offset;
} tSmbStrHeader;

typedef struct {
	char ident[8];
	uint32_t msgType;
	uint32_t flags;
	tSmbStrHeader host;
	tSmbStrHeader domain;
	uint8_t buffer[1024];
	uint32_t bufIndex;
} tSmbNtlmAuthRequest;

typedef struct {
	char ident[8];
	uint32_t msgType;
	tSmbStrHeader uDomain;
	uint32_t flags;
	uint8_t challengeData[8];
	uint8_t reserved[8];
	tSmbStrHeader emptyString;
	uint8_t buffer[1024];
	uint32_t bufIndex;
} tSmbNtlmAuthChallenge;

typedef struct {
    char ident[8];
    uint32_t msgType;
    tSmbStrHeader lmResponse;
    tSmbStrHeader ntResponse;
    tSmbStrHeader uDomain;
    tSmbStrHeader uUser;
    tSmbStrHeader uWks;
    tSmbStrHeader sessionKey;
    uint32_t flags;
    uint8_t buffer[1024];
    uint32_t bufIndex;
} tSmbNtlmAuthResponse;extern void buildAuthRequest(tSmbNtlmAuthRequest * request, long flags, char *host, char *domain);

void xxor(char *out, char *in1, char *in2, int n);

void strupper(char *s);

#define SmbLength(ptr) (((ptr)->buffer - (uint8*)(ptr)) + (ptr)->bufIndex)

/* Base64 code*/
int from64tobits(char *out, const char *in);
void to64frombits(unsigned char *out, const unsigned char *in, int inlen);

void BuildAuthRequest(tSmbNtlmAuthRequest * request, long flags, char *host, char *domain);

// if flags is 0 minimun security level is selected, otherwise new value superseeds.
// host and domain are optional, they may be NULLed.


void buildAuthResponse(tSmbNtlmAuthChallenge * challenge, tSmbNtlmAuthResponse * response, long flags, char *user, char *password, char *domain, char *host);

//Given a challenge, generates a response for that user/passwd/host/domain.
//flags, host, and domain superseeds given by server. Leave 0 and NULL for server authentication

// info functions
void dumpAuthRequest(FILE * fp, tSmbNtlmAuthRequest * request);
void dumpAuthChallenge(FILE * fp, tSmbNtlmAuthChallenge * challenge);
void dumpAuthResponse(FILE * fp, tSmbNtlmAuthResponse * response);

class NTLM {
    
    typedef struct {
        uint16_t len;
        uint16_t maxlen;
        uint32_t offset;
    } tSmbStrHeader;

    typedef struct {
        char ident[8];
        uint32_t msgType;
        uint32_t flags;
        tSmbStrHeader host;
        tSmbStrHeader domain;
        uint8_t buffer[1024];
        uint32_t bufIndex;
    } tSmbNtlmAuthRequest;

    typedef struct {
        char ident[8];
        uint32_t msgType;
        tSmbStrHeader uDomain;
        uint32_t flags;
        uint8_t challengeData[8];
        uint8_t reserved[8];
        tSmbStrHeader emptyString;
        uint8_t buffer[1024];
        uint32_t bufIndex;
    } tSmbNtlmAuthChallenge;

    typedef struct {
        char ident[8];
        uint32_t msgType;
        tSmbStrHeader lmResponse;
        tSmbStrHeader ntResponse;
        tSmbStrHeader uDomain;
        tSmbStrHeader uUser;
        tSmbStrHeader uWks;
        tSmbStrHeader sessionKey;
        uint32_t flags;
        uint8_t buffer[1024];
        uint32_t bufIndex;
    } tSmbNtlmAuthResponse;
    
    public:

        void BuildAuthRequest(tSmbNtlmAuthRequest * request, long flags, char *host, char *domain);

        // if flags is 0 minimun security level is selected, otherwise new value superseeds.
        // host and domain are optional, they may be NULLed.


        void buildAuthResponse(tSmbNtlmAuthChallenge * challenge, tSmbNtlmAuthResponse * response, long flags, char *user, char *password, char *domain, char *host);

        //Given a challenge, generates a response for that user/passwd/host/domain.
        //flags, host, and domain superseeds given by server. Leave 0 and NULL for server authentication

        // info functions
        void dumpAuthRequest(FILE * fp, tSmbNtlmAuthRequest * request);
        void dumpAuthChallenge(FILE * fp, tSmbNtlmAuthChallenge * challenge);
        void dumpAuthResponse(FILE * fp, tSmbNtlmAuthResponse * response);
};
