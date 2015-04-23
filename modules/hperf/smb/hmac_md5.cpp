
#include <hmac_md5.hpp>

#include <string.h>

/*
 * rfc 2104 Microsoft's implementation
 */

HMACMD5::HMACMD5(const unsigned char* key, int key_len) {
	int i;

    /* if key is longer than 64 bytes truncate it */
    if (key_len > 64) {
        key_len = 64;
    }

    /* start out by storing key in pads */
    ZERO_STRUCT(this->ctx.k_ipad);
    ZERO_STRUCT(this->ctx.k_opad);
    memcpy(this->ctx.k_ipad, key, key_len);
    memcpy(this->ctx.k_opad, key, key_len);

    /* XOR key with ipad and opad values */
    for (i=0; i<64; i++) {
        this->ctx.k_ipad[i] ^= 0x36;
        this->ctx.k_opad[i] ^= 0x5c;
    }

    MD5_Init(&(this->ctx.ctx));
    MD5_Update(&(this->ctx.ctx), this->ctx.k_ipad, 64);  
}


void HMACMD5::update(const unsigned char *text, int text_len) {
    MD5_Update(&ctx.ctx, (void *)text, text_len); /* then text of datagram */
}


void HMACMD5::digest(unsigned char *digest) {
    MD5_CTX ctx_o;

    MD5_Final(digest, &ctx.ctx);

    MD5_Init(&ctx_o);
    MD5_Update(&ctx_o, ctx.k_opad, 64);   
    MD5_Update(&ctx_o, digest, 16); 
    MD5_Final(digest, &ctx_o);
}

/***********************************************************************
 the rfc 2104 version of hmac_md5 initialisation.
***********************************************************************/
/*
void hmac_md5_init_rfc2104(const unsigned char *key, int key_len, HMACMD5Context *ctx)
{
        int i;
	unsigned char tk[16];

        // if key is longer than 64 bytes reset it to key=MD5(key)
        if (key_len > 64) {
                MD5_CTX tctx;

                MD5_Init(&tctx);
                MD5_Update(&tctx, (void *)key, key_len);
                MD5_Final(tk, &tctx);

                key = tk;
                key_len = 16;
        }

        // start out by storing key in pads
        ZERO_STRUCT(ctx->k_ipad);
        ZERO_STRUCT(ctx->k_opad);
        memcpy( ctx->k_ipad, key, key_len);
        memcpy( ctx->k_opad, key, key_len);

        // XOR key with ipad and opad values
        for (i=0; i<64; i++) {
                ctx->k_ipad[i] ^= 0x36;
                ctx->k_opad[i] ^= 0x5c;
        }

        MD5_Init(&ctx->ctx);
        MD5_Update(&ctx->ctx, ctx->k_ipad, 64);  
}
*/
