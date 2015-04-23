#include <boost/range/adaptors.hpp>
#include <boost/archive/iterators/base64_from_binary.hpp>
#include <boost/archive/iterators/binary_from_base64.hpp>
#include <boost/archive/iterators/transform_width.hpp>
#include <boost/archive/iterators/ostream_iterator.hpp>

#include <sstream>

#include <vector>
#include <string>

#include <base64.hpp>

using namespace boost::archive::iterators;

std::string Base64::encode(std::vector<uint8_t> src) {
    
    typedef base64_from_binary< transform_width<std::vector<uint8_t>::iterator, 6, 8> > base64_enc;
    
    std::stringstream os;

    std::copy(
        base64_enc(src.begin()),
        base64_enc(src.end()),
        ostream_iterator<char>(os)
    );
    
    std::string result = os.str();
    
    result.resize(((result.size() + (result.size()%4))/4*4), '=');
    
    return result;
}

std::vector<uint8_t> Base64::decode(std::string src) {
    
    typedef transform_width<binary_from_base64<std::string::iterator>, 8, 6> base64_dec;
    
    std::vector<uint8_t> dst;
    
    unsigned int count = src.size()/4*3;
    for(std::string::reverse_iterator c = src.rbegin(); *c == '='; c++, count--);
    
    for(base64_dec i(src.begin()); count; --count, i++)
        dst.push_back(*i);
    
    return dst;
}
