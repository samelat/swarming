#include "cracker.hpp"

void Cracker::crack(bp::list usernames, bp::list passwords, bp::list pairs) {
    
    using string_iterator = bp::stl_input_iterator<const char *>;

    for(string_iterator usr(usernames); usr != string_iterator(); usr++) {
        for(string_iterator pwd(passwords); pwd != string_iterator(); pwd++) {
            callback(*usr, *pwd);
        }
    }

    for(bp::stl_input_iterator<bp::tuple> p(pairs); p != bp::stl_input_iterator<bp::tuple>(); p++) {
        callback(bp::extract<const char *>((*p)[0])(), bp::extract<const char *>((*p)[1])());
    }
}
