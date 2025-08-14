#include <array>
#include <openssl/ec.h>
#include <openssl/obj_mac.h>
#include <openssl/bn.h>

bool secp256k1_pubkey(const uint8_t priv[32], uint8_t pub[33]){
    bool ok=false;
    EC_GROUP* group = EC_GROUP_new_by_curve_name(NID_secp256k1);
    EC_POINT* point = EC_POINT_new(group);
    BIGNUM* priv_bn = BN_bin2bn(priv,32,nullptr);
    BN_CTX* ctx = BN_CTX_new();
    if(group && point && priv_bn && ctx){
        if(EC_POINT_mul(group, point, priv_bn, nullptr, nullptr, ctx)==1){
            if(EC_POINT_point2oct(group, point, POINT_CONVERSION_COMPRESSED, pub,33, ctx)==33){
                ok=true;
            }
        }
    }
    if(priv_bn) BN_free(priv_bn);
    if(point) EC_POINT_free(point);
    if(group) EC_GROUP_free(group);
    if(ctx) BN_CTX_free(ctx);
    return ok;
}
