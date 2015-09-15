#ifndef EXCEPTIONS_HPP
#define EXCEPTIONS_HPP

#include <exception>
#include <boost/python.hpp>


class standard_error : public std::runtime_error {
public:
    static PyObject *python_type;

    standard_error(const std::string &what) : std::runtime_error(what) {};
};


class fatal_error : public std::runtime_error {
public:
    static PyObject *python_type;

    fatal_error(const std::string &what) : std::runtime_error(what) {};
};


template<typename cpp_exception_type>
void translate_exception(cpp_exception_type const& e) {
    PyErr_SetString(cpp_exception_type::python_type, e.what());
}

#endif