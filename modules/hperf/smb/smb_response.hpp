
#include "smb_mod.hpp"

#ifndef SMB_RESPONSE_H
#define SMB_RESPONSE_H

class SMBResponse {
private:

    SMBSession& session;
    
public:
    SMBResponse(SMBSession &s) : session(s) {};
    unsigned long smb_session_setup(std::string szLogin, std::string szPassword);
    
    unsigned char Get7Bits(unsigned char *input, int startBit);
    void MakeKey(unsigned char *key, unsigned char *des_key);
    void DesEncrypt(unsigned char *clear, unsigned char *key, unsigned char *cipher);
    
    int HashLM(unsigned char **lmhash, unsigned char *pass, unsigned char *_challenge);
    
    int MakeNTLM (unsigned char *ntlmhash, unsigned char *pass);
    int HashLMv2(unsigned char **LMv2hash, unsigned char *szLogin, unsigned char *szPassword);
    int HashNTLMv2(unsigned char **NTLMv2hash, int *iByteCount, unsigned char *szLogin, unsigned char *szPassword);
    int HashNTLM(unsigned char **ntlmhash, unsigned char *pass, unsigned char *_challenge);
    
};

class LMv1SMBResponse : SMBResponse {
    
};

class LMv2SMBResponse : SMBResponse {
    
};

class NTLMv1SMBResponse : SMBResponse {
    
};

class NTLMv2SMBResponse : SMBResponse {
    
};

#endif
