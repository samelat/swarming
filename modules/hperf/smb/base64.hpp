
#include <stdint.h>
#include <vector>
#include <string>

class Base64 {
    public:
    
        static std::string encode(std::vector<uint8_t> src);
        static std::vector<uint8_t> decode(std::string src);
};
