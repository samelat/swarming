#ifndef CRACKER_HPP
#define CRACKER_HPP

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/stl_iterator.hpp>

namespace bp = boost::python;

class Cracker {
public:
    Cracker(bp::object& callback) : callback(callback) {};
    ~Cracker() {};

    virtual void login(const char * username, const char * password) = 0;

    void crack(bp::list, bp::list, bp::list);

private:
    const bp::object callback;
};

#endif