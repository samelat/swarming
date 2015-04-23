
#include <openssl/md5.h>

#define ZERO_STRUCT(x) memset((char *)&(x), 0, sizeof(x))

class HMACMD5 {
	
    typedef struct {
        MD5_CTX ctx;
        unsigned char k_ipad[65];    
        unsigned char k_opad[65];
    } HMACMD5Context;
    
    private:
    
        HMACMD5Context ctx;
    
    public:
    
        HMACMD5(const unsigned char* key, int key_len);
    
        void update(const unsigned char *text, int text_len);
        void digest(unsigned char *digest);
};
