
#include <module.hpp>

void Cracker::crack(bp::list usernames, bp::list passwords, bp::list pairs) {
    
    using string_iterator = bp::stl_input_iterator<const char *>;

    status_t result;

    for(string_iterator usr(usernames); usr != string_iterator(); usr++) {
        for(string_iterator pwd(passwords); pwd != string_iterator(); pwd++) {
            result = login(*usr, *pwd);
            switch(result) {
                case status_t::SUCCESS: callback(*usr, *pwd); break;
                case status_t::FAILED:  break;
                case status_t::ERROR:   break; // This will be handle.
            }
        }
    }

    for(bp::stl_input_iterator<bp::tuple> p(pairs); p != bp::stl_input_iterator<bp::tuple>(); p++) {
        result = login(bp::extract<const char *>((*p)[0])(), bp::extract<const char *>((*p)[1])());
        switch(result) {
            case status_t::SUCCESS: callback(bp::extract<const char *>((*p)[0])(),
                                             bp::extract<const char *>((*p)[1])());
                break;
            case status_t::FAILED:  break;
            case status_t::ERROR:   break; // This will be handle.
        }
    }
}

BOOST_PYTHON_MODULE(MODULE_NAME)
{
    bp::class_<CLASS_NAME>(STRINGIFY(CLASS_NAME), bp::init<bp::object&>())
        .def("crack",
             &CLASS_NAME::crack,
             (bp::arg("usernames"), bp::arg("passwords"), bp::arg("pairs")));
}