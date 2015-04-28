#include "cracker.hpp"

void Cracker::crack(bp::list usernames, bp::list passwords, bp::list pairs) {
    
    using string_iterator = bp::stl_input_iterator<std::string>;

    for(string_iterator usr(usernames); usr != string_iterator(); usr++) {
        for(string_iterator pwd(passwords); pwd != string_iterator(); pwd++) {
            callback(*usr, *pwd);
        }
    }

    for(bp::stl_input_iterator<bp::tuple> pair(pairs); pair != bp::stl_input_iterator<bp::tuple>(); pair++) {
        callback(bp::extract<std::string>(pair[0]), bp::extract<std::string>(pair[1]));
    }
}
