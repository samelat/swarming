#include <iostream>

#include "test.hpp"

void Test::login(const char * username, const char * password) {
    std::cout << "[!] " << username << " - " << password << std::endl;
}

BOOST_PYTHON_MODULE(test)
{
    bp::class_<Test>("Test", bp::init<bp::object&>())
        .def("crack", &Test::crack);
}